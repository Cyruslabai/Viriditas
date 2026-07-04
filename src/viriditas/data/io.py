"""Input and output helpers for metadata files."""

from __future__ import annotations

import csv
import json
from collections import Counter
from collections.abc import Sequence
from pathlib import Path

from viriditas.data.schemas import CSV_FIELDNAMES, ImageRecord


def write_records_csv(records: Sequence[ImageRecord], output_path: Path | str) -> None:
    """Write image records to a CSV file."""

    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=CSV_FIELDNAMES)
        writer.writeheader()
        for record in records:
            writer.writerow(record.to_csv_row())


def write_label_map(records: Sequence[ImageRecord], field_name: str, output_path: Path | str) -> None:
    """Write a stable label-to-id JSON file."""

    labels = sorted({str(getattr(record, field_name)) for record in records})
    label_map = {label: index for index, label in enumerate(labels)}
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(label_map, indent=2, sort_keys=True), encoding="utf-8")


def write_summary(records: Sequence[ImageRecord], output_path: Path | str) -> None:
    """Write a compact JSON summary for quick dataset inspection."""

    summary = {
        "total_images": len(records),
        "datasets": dict(Counter(record.dataset_name for record in records)),
        "plants": dict(Counter(record.plant for record in records)),
        "diseases": dict(Counter(record.task_disease_label for record in records)),
        "splits": dict(Counter(record.split for record in records)),
    }
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(summary, indent=2, sort_keys=True), encoding="utf-8")


def write_split_csvs(records: Sequence[ImageRecord], output_dir: Path | str) -> None:
    """Write train, val, and test CSV files from already-split records."""

    directory = Path(output_dir)
    for split in ("train", "val", "test"):
        split_records = [record for record in records if record.split == split]
        write_records_csv(split_records, directory / f"{split}.csv")
