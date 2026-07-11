"""Typed records used by the dataset indexing pipeline."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path


CSV_FIELDNAMES = [
    "image_path",
    "dataset_name",
    "dataset_root",
    "source_split",
    "original_label",
    "plant",
    "disease",
    "is_healthy",
    "task_plant_label",
    "task_disease_label",
    "file_name",
    "file_ext",
    "image_id",
    "duplicate_group_id",
    "split",
]


@dataclass(frozen=True)
class LabelInfo:
    """Label information inferred from an image path."""

    source_split: str
    original_label: str
    label_parts: tuple[str, ...]
    layout_type: str


@dataclass(frozen=True)
class ParsedLabel:
    """Canonical plant and disease labels."""

    plant: str
    disease: str
    is_healthy: bool


@dataclass(frozen=True)
class ImageRecord:
    """One indexed image row."""

    image_path: str
    dataset_name: str
    dataset_root: str
    source_split: str
    original_label: str
    plant: str
    disease: str
    is_healthy: bool
    task_plant_label: str
    task_disease_label: str
    file_name: str
    file_ext: str
    image_id: str
    split: str = ""
    duplicate_group_id: str = ""

    def to_csv_row(self) -> dict[str, str]:
        row = asdict(self)
        row["is_healthy"] = "true" if self.is_healthy else "false"
        return row


def make_image_id(dataset_name: str, image_path: Path) -> str:
    """Build a stable image id from dataset name and path."""

    normalized = image_path.as_posix().lower()
    safe_dataset = dataset_name.strip().lower().replace(" ", "_")
    return f"{safe_dataset}:{normalized}"