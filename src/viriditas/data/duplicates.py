"""
Duplicate image detection utilities.

This module finds exact duplicate images using SHA-256 hashes.
"""

from __future__ import annotations

import hashlib
from collections import defaultdict
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