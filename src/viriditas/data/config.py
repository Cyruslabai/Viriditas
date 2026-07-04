"""Configuration constants for dataset indexing."""

from __future__ import annotations

from pathlib import Path

DEFAULT_IMAGE_EXTENSIONS = frozenset({
    ".jpg",
    ".jpeg",
    ".png",
    ".bmp",
    ".webp",
    ".tif",
    ".tiff",
})

SPLIT_ALIASES = {
    "train": "train",
    "training": "train",
    "valid": "val",
    "validation": "val",
    "val": "val",
    "test": "test",
    "testing": "test",
}

NON_CLASS_DIRECTORIES = frozenset({
    "color",
    "coloured",
    "colored",
    "grayscale",
    "grey_scale",
    "gray_scale",
    "segmented",
    "images",
    "image",
    "leaf",
    "leaves",
    "plantvillage",
    "plant_village",
})

DEFAULT_METADATA_DIR = Path("data") / "metadata"

