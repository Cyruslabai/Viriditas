"""Infer dataset layout and labels from image paths."""

from __future__ import annotations

from pathlib import Path

from agriai.data.config import NON_CLASS_DIRECTORIES, SPLIT_ALIASES
from agriai.data.schemas import LabelInfo


def infer_label_info(image_path: Path, dataset_root: Path) -> LabelInfo:
    """Infer split and raw label information for one image path."""

    relative_parts = image_path.relative_to(dataset_root).parts
    parent_parts = relative_parts[:-1]
    source_split = ""
    label_parts = parent_parts
    layout_type = "class_folder"

    split_index = _find_split_index(parent_parts)
    if split_index is not None:
        source_split = SPLIT_ALIASES[parent_parts[split_index].lower()]
        label_parts = parent_parts[split_index + 1 :]
        layout_type = "split_class_folder"

    label_parts = _trim_non_class_prefix(label_parts)
    original_label = _infer_original_label(label_parts)

    if len(label_parts) >= 2 and original_label == "___".join(label_parts[-2:]):
        layout_type = "nested_plant_disease" if not source_split else "split_nested_plant_disease"

    return LabelInfo(
        source_split=source_split,
        original_label=original_label,
        label_parts=tuple(label_parts),
        layout_type=layout_type,
    )


def _find_split_index(parts: tuple[str, ...]) -> int | None:
    for index, part in enumerate(parts):
        if part.lower() in SPLIT_ALIASES:
            return index
    return None


def _trim_non_class_prefix(parts: tuple[str, ...]) -> tuple[str, ...]:
    trimmed = list(parts)
    while len(trimmed) > 1 and _slug(trimmed[0]) in NON_CLASS_DIRECTORIES:
        trimmed.pop(0)
    return tuple(trimmed)


def _infer_original_label(label_parts: tuple[str, ...]) -> str:
    if not label_parts:
        return "Unknown"

    last = label_parts[-1]
    if _looks_like_combined_label(last) or len(label_parts) == 1:
        return last

    previous = label_parts[-2]
    if _slug(previous) in NON_CLASS_DIRECTORIES:
        return last

    return "___".join(label_parts[-2:])


def _looks_like_combined_label(value: str) -> bool:
    text = value.lower()
    return "___" in text or "__" in text or "healthy" in text or "disease" in text or "blight" in text


def _slug(value: str) -> str:
    return value.strip().lower().replace("-", "_").replace(" ", "_")

