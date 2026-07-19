"""Build metadata indexes from one or more image datasets."""

from __future__ import annotations

from pathlib import Path
from collections.abc import Iterable

from agriai.data.label_parser import parse_label
from agriai.data.layout_detection import infer_label_info
from agriai.data.normalizer import infer_plant_hint, make_task_disease_label
from agriai.data.scanners import infer_dataset_name, iter_image_paths
from agriai.data.schemas import ImageRecord, make_image_id


def build_dataset_index(
    dataset_roots: Iterable[Path | str],
    *,
    path_mode: str = "absolute",
) -> list[ImageRecord]:
    """Build image metadata records for dataset roots.

    Args:
        dataset_roots: One or more dataset root directories.
        path_mode: ``absolute`` or ``relative``. Relative paths are stored
            relative to each dataset root.
    """

    if path_mode not in {"absolute", "relative"}:
        raise ValueError("path_mode must be 'absolute' or 'relative'")

    records: list[ImageRecord] = []
    for root_value in dataset_roots:
        dataset_root = Path(root_value).expanduser().resolve()
        if not dataset_root.exists():
            raise FileNotFoundError(f"Dataset root does not exist: {dataset_root}")
        if not dataset_root.is_dir():
            raise NotADirectoryError(f"Dataset root is not a directory: {dataset_root}")

        dataset_name = infer_dataset_name(dataset_root)
        plant_hint = infer_plant_hint(" ".join((dataset_name, dataset_root.as_posix())))
        for image_path in iter_image_paths(dataset_root):
            label_info = infer_label_info(image_path, dataset_root)
            parsed = parse_label(label_info.original_label, label_info.label_parts, plant_hint)
            stored_path = _format_image_path(image_path, dataset_root, path_mode)

            records.append(
                ImageRecord(
                    image_path=stored_path,
                    dataset_name=dataset_name,
                    dataset_root=str(dataset_root),
                    source_split=label_info.source_split,
                    original_label=label_info.original_label,
                    plant=parsed.plant,
                    disease=parsed.disease,
                    is_healthy=parsed.is_healthy,
                    task_plant_label=parsed.plant,
                    task_disease_label=make_task_disease_label(parsed.plant, parsed.disease),
                    file_name=image_path.name,
                    file_ext=image_path.suffix.lower(),
                    image_id=make_image_id(dataset_name, image_path.relative_to(dataset_root)),
                    split=label_info.source_split,
                )
            )
    return records


def _format_image_path(image_path: Path, dataset_root: Path, path_mode: str) -> str:
    if path_mode == "relative":
        return image_path.relative_to(dataset_root).as_posix()
    return str(image_path)
