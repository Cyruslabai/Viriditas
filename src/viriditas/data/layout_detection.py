"""Infer dataset layout and labels from image paths."""

from __future__ import annotations

import re

from pathlib import Path

from viriditas.data.config import NON_CLASS_DIRECTORIES, SPLIT_ALIASES
from viriditas.data.schemas import LabelInfo

_TRAILING_DIGITS = re.compile(r"\d+$")


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

    if not label_parts:
        # No class folder exists between the dataset/split root and the
        # image file itself. Some datasets (e.g. strawberry-disease-
        # detection-dataset) encode the label in the filename instead,
        # such as "angular_leafspot351.jpg". Fall back to parsing that.
        filename_label = _label_from_filename(image_path)
        if filename_label:
            return LabelInfo(
                source_split=source_split,
                original_label=filename_label,
                label_parts=(),
                layout_type="filename_label" if not source_split else "split_filename_label",
            )
        return LabelInfo(
            source_split=source_split,
            original_label="Unknown",
            label_parts=(),
            layout_type=layout_type,
        )

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


def _label_from_filename(image_path: Path) -> str:
    """Derive a class label from a filename when no class folder exists.

    Handles filenames such as ``angular_leafspot351.jpg`` by stripping the
    trailing image-index digits and extension, leaving ``angular_leafspot``.
    Returns an empty string if nothing usable remains (e.g. filenames that
    are purely numeric, like ``0001.jpg``, which carry no label at all).
    """

    stem = image_path.stem
    stem = _TRAILING_DIGITS.sub("", stem)
    stem = stem.strip("_- ")
    return stem


def _looks_like_combined_label(value: str) -> bool:
    text = value.lower()
    return "___" in text or "__" in text or "healthy" in text or "disease" in text or "blight" in text


def _slug(value: str) -> str:
    return value.strip().lower().replace("-", "_").replace(" ", "_")