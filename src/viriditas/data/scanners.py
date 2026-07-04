"""Image discovery for dataset roots."""

from __future__ import annotations

from pathlib import Path
from collections.abc import Iterable

from viriditas.data.config import DEFAULT_IMAGE_EXTENSIONS


def iter_image_paths(
    dataset_root: Path,
    extensions: Iterable[str] = DEFAULT_IMAGE_EXTENSIONS,
) -> list[Path]:
    """Return all image paths below ``dataset_root`` in stable order."""

    root = Path(dataset_root)
    normalized_extensions = {ext.lower() for ext in extensions}
    paths = [
        path
        for path in root.rglob("*")
        if path.is_file() and path.suffix.lower() in normalized_extensions
    ]
    return sorted(paths, key=lambda path: path.as_posix().lower())


def infer_dataset_name(dataset_root: Path) -> str:
    """Infer a readable dataset name from a root path."""

    return Path(dataset_root).name.replace("_", " ").replace("-", " ").strip() or "dataset"
