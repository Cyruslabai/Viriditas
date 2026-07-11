"""
Duplicate image detection utilities.

This module finds exact duplicate images using SHA-256 hashes.
"""

from __future__ import annotations

import csv
import hashlib
from collections import defaultdict
from dataclasses import replace
from pathlib import Path

from viriditas.data.schemas import ImageRecord


def sha256_file(path: str | Path, chunk_size: int = 1024 * 1024) -> str:
    """
    Calculate the SHA-256 hash of a file.

    Args:
        path: Path to the image.
        chunk_size: Number of bytes to read at once.

    Returns:
        SHA-256 hash string.
    """

    hasher = hashlib.sha256()

    with open(path, "rb") as f:
        while True:
            chunk = f.read(chunk_size)
            if not chunk:
                break
            hasher.update(chunk)

    return hasher.hexdigest()


def find_duplicates(
    records: list[ImageRecord],
) -> dict[str, list[ImageRecord]]:
    """
    Find duplicate images.

    Images are considered duplicates if they have the same SHA-256 hash.

    Args:
        records: Dataset image records.

    Returns:
        Dictionary:
            SHA256 -> List[ImageRecord]
    """

    groups = defaultdict(list)

    for record in records:
        try:
            file_hash = sha256_file(record.image_path)
            groups[file_hash].append(record)
        except Exception:
            # Ignore unreadable files for now.
            continue

    duplicates = {
        hash_value: image_records
        for hash_value, image_records in groups.items()
        if len(image_records) > 1
    }

    return duplicates


def _load_hash_cache(cache_path: Path) -> dict[str, tuple[int, float, str]]:
    """Load a cache of image_path -> (file_size, mtime, hash).

    Returns an empty dict if no cache file exists yet.
    """

    if not cache_path.exists():
        return {}

    cache: dict[str, tuple[int, float, str]] = {}
    with open(cache_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            cache[row["image_path"]] = (
                int(row["file_size"]),
                float(row["mtime"]),
                row["file_hash"],
            )
    return cache


def _save_hash_cache(cache_path: Path, cache: dict[str, tuple[int, float, str]]) -> None:
    cache_path.parent.mkdir(parents=True, exist_ok=True)
    with open(cache_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["image_path", "file_size", "mtime", "file_hash"])
        for image_path, (file_size, mtime, file_hash) in cache.items():
            writer.writerow([image_path, file_size, mtime, file_hash])


def hash_with_cache(image_path: str, cache: dict[str, tuple[int, float, str]]) -> str:
    """Return a file's SHA-256 hash, reusing a cached value when the file's
    size and modification time haven't changed since it was last hashed.
    """

    stat = Path(image_path).stat()
    cached = cache.get(image_path)
    if cached is not None:
        cached_size, cached_mtime, cached_hash = cached
        if cached_size == stat.st_size and cached_mtime == stat.st_mtime:
            return cached_hash

    file_hash = sha256_file(image_path)
    cache[image_path] = (stat.st_size, stat.st_mtime, file_hash)
    return file_hash


def deduplicate_records(
    records: list[ImageRecord],
    *,
    prefer_split: str = "train",
    cache_path: str | Path | None = None,
) -> tuple[list[ImageRecord], dict]:
    """Hash every record's image, tag it with a duplicate_group_id, and
    resolve cross-split duplicates to prevent train/val/test leakage.

    Every record is hashed and tagged with a duplicate_group_id (the first
    16 hex characters of its SHA-256 hash), whether or not it turns out to
    be part of a duplicate group. This makes it possible to inspect
    duplicate groups later directly from the CSV, not just at build time.

    For any group of duplicates whose members span more than one split
    (e.g. the same image present in both a source "train" and "test"
    folder), only one copy is kept -- preferring a copy already assigned to
    ``prefer_split`` -- and the rest are dropped, so no image ever appears
    in more than one split. Duplicates that all fall within a single split
    are left as-is; they don't cause leakage, only some redundancy.

    Args:
        records: Dataset image records, expected to already have ``split``
            assigned (i.e. call this after ``assign_splits``).
        prefer_split: Which split to keep when a duplicate group spans
            multiple splits. Defaults to "train" so evaluation data stays
            as clean as possible.
        cache_path: Optional path to a CSV cache file mapping image_path to
            a previously computed hash. When provided, files whose size and
            modification time match the cache are not re-hashed, making
            repeat runs in the same (or a restored) working directory much
            faster. Pass ``None`` to always hash from scratch.

    Returns:
        A tuple of (deduplicated records, summary stats dict).
    """

    cache_path = Path(cache_path) if cache_path is not None else None
    hash_cache = _load_hash_cache(cache_path) if cache_path else {}
    cache_hits = 0

    hash_to_records: dict[str, list[ImageRecord]] = defaultdict(list)
    unreadable: list[ImageRecord] = []

    for record in records:
        try:
            if cache_path:
                before = len(hash_cache)
                file_hash = hash_with_cache(record.image_path, hash_cache)
                if len(hash_cache) == before:
                    cache_hits += 1
            else:
                file_hash = sha256_file(record.image_path)
        except Exception:
            unreadable.append(record)
            continue
        hash_to_records[file_hash].append(record)

    if cache_path:
        _save_hash_cache(cache_path, hash_cache)

    kept_records: list[ImageRecord] = []
    cross_split_groups = 0
    same_split_groups = 0
    rows_dropped = 0

    for file_hash, group in hash_to_records.items():
        group_id = file_hash[:16]
        tagged_group = [replace(record, duplicate_group_id=group_id) for record in group]

        if len(tagged_group) == 1:
            kept_records.append(tagged_group[0])
            continue

        splits_in_group = {record.split for record in tagged_group}
        if len(splits_in_group) > 1:
            cross_split_groups += 1
            preferred = [record for record in tagged_group if record.split == prefer_split]
            keep = preferred[0] if preferred else tagged_group[0]
            kept_records.append(keep)
            rows_dropped += len(tagged_group) - 1
        else:
            same_split_groups += 1
            kept_records.extend(tagged_group)

    kept_records.extend(unreadable)

    stats = {
        "total_input": len(records),
        "total_output": len(kept_records),
        "unreadable_files": len(unreadable),
        "duplicate_groups_total": sum(1 for g in hash_to_records.values() if len(g) > 1),
        "cross_split_groups": cross_split_groups,
        "same_split_groups": same_split_groups,
        "rows_dropped_for_leakage": rows_dropped,
        "cache_hits": cache_hits,
    }

    return kept_records, stats