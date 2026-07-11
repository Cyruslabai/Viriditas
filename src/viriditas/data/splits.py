"""Train, validation, and test split helpers."""

from __future__ import annotations

from collections import defaultdict
from collections.abc import Sequence
from dataclasses import replace
import random

from viriditas.data.schemas import ImageRecord


def assign_splits(
    records: Sequence[ImageRecord],
    *,
    train_ratio: float = 0.8,
    val_ratio: float = 0.1,
    test_ratio: float = 0.1,
    label_field: str = "task_disease_label",
    seed: int = 42,
    preserve_source_splits: bool = True,
) -> list[ImageRecord]:
    """Assign train/val/test splits, stratified by label where possible."""

    _validate_ratios(train_ratio, val_ratio, test_ratio)

    if preserve_source_splits and any(record.source_split for record in records):
        fixed_records = [
            _replace_split(record, record.source_split)
            for record in records
            if record.source_split
        ]
        unsplit_records = [record for record in records if not record.source_split]
        if not unsplit_records:
            return fixed_records
        return sorted(
            fixed_records
            + assign_splits(
                unsplit_records,
                train_ratio=train_ratio,
                val_ratio=val_ratio,
                test_ratio=test_ratio,
                label_field=label_field,
                seed=seed,
                preserve_source_splits=False,
            ),
            key=lambda record: record.image_id,
        )

    grouped: dict[str, list[ImageRecord]] = defaultdict(list)
    for record in records:
        grouped[str(getattr(record, label_field))].append(record)

    rng = random.Random(seed)
    split_records: list[ImageRecord] = []
    for label_records in grouped.values():
        shuffled = list(label_records)
        rng.shuffle(shuffled)
        train_end, val_end = _split_boundaries(len(shuffled), train_ratio, val_ratio)

        for index, record in enumerate(shuffled):
            if index < train_end:
                split = "train"
            elif index < val_end:
                split = "val"
            else:
                split = "test"
            split_records.append(_replace_split(record, split))

    return sorted(split_records, key=lambda record: record.image_id)


def _validate_ratios(train_ratio: float, val_ratio: float, test_ratio: float) -> None:
    total = train_ratio + val_ratio + test_ratio
    if abs(total - 1.0) > 1e-6:
        raise ValueError("train_ratio + val_ratio + test_ratio must equal 1.0")
    if min(train_ratio, val_ratio, test_ratio) < 0:
        raise ValueError("split ratios must be non-negative")


def _split_boundaries(count: int, train_ratio: float, val_ratio: float) -> tuple[int, int]:
    if count <= 1:
        return count, count

    train_count = max(1, int(round(count * train_ratio)))
    val_count = int(round(count * val_ratio))

    if count >= 3 and val_count == 0:
        val_count = 1

    if train_count + val_count >= count and count >= 3:
        train_count = max(1, count - 2)
        val_count = 1

    return train_count, train_count + val_count


def _replace_split(record: ImageRecord, split: str) -> ImageRecord:
    # Uses dataclasses.replace instead of manually listing every field, so
    # new ImageRecord fields (e.g. duplicate_group_id) are carried through
    # automatically instead of silently dropped.
    return replace(record, split=split)