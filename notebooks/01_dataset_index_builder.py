"""Kaggle-friendly VIRIDITAS dataset index builder.

In Kaggle, run this after adding the datasets listed in DATASET_ROOTS.
It writes metadata files to /kaggle/working/data/metadata without copying images.
"""

from __future__ import annotations

from pathlib import Path
import sys

PROJECT_ROOT = Path.cwd()
SRC_ROOT = PROJECT_ROOT / "src"
if SRC_ROOT.exists() and str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from viriditas.data.index_builder import build_dataset_index
from viriditas.data.io import write_label_map, write_records_csv, write_split_csvs, write_summary
from viriditas.data.splits import assign_splits


DATASET_ROOTS = [
    "/kaggle/input/datasets/rizwan123456789/potato-disease-leaf-datasetpld",
    "/kaggle/input/datasets/showravdhar/apple-disease-dataset",
    "/kaggle/input/datasets/shuvokumarbasak2030/cherry-leaf-diseases-plant-village-augmented-data",
    "/kaggle/input/datasets/smaranjitghose/corn-or-maize-leaf-disease-dataset",
    "/kaggle/input/datasets/rm1000/grape-disease-dataset-original",
    "/kaggle/input/datasets/zunorain/pea-plant-dataset",
    "/kaggle/input/datasets/shuvokumarbasak2030/peach-leaf-diseases-plant-village-augmented-data",
    "/kaggle/input/datasets/shuvokumarbasak4004/orange-leaf-disease-dataset",
    "/kaggle/input/datasets/ashishmotwani/tomato",
    "/kaggle/input/datasets/usmanafzaal/strawberry-disease-detection-dataset",
    "/kaggle/input/datasets/sivm205/soybean-diseased-leaf-dataset",
    "/kaggle/input/datasets/tahmidmir/pumpkin-leaf-diseases-dataset-from-bangladesh",
    "/kaggle/input/datasets/shuvokumarbasak2030/pepper-leaf-diseases-plant-village-augmented-data",
]

OUTPUT_DIR = Path("/kaggle/working/data/metadata") if Path("/kaggle").exists() else Path("data/metadata")
PATH_MODE = "absolute"


def run() -> None:
    records = build_dataset_index(DATASET_ROOTS, path_mode=PATH_MODE)
    records = assign_splits(records, preserve_source_splits=True)

    write_records_csv(records, OUTPUT_DIR / "master_dataset.csv")
    write_records_csv(records, OUTPUT_DIR / "plant_id_dataset.csv")
    write_records_csv(records, OUTPUT_DIR / "disease_dataset.csv")
    write_split_csvs(records, OUTPUT_DIR)
    write_label_map(records, "task_plant_label", OUTPUT_DIR / "label_map_plants.json")
    write_label_map(records, "task_disease_label", OUTPUT_DIR / "label_map_diseases.json")
    write_summary(records, OUTPUT_DIR / "dataset_summary.json")

    print(f"Indexed {len(records)} images")
    print(f"Metadata directory: {OUTPUT_DIR}")
    print("Files: master_dataset.csv, plant_id_dataset.csv, disease_dataset.csv, split CSVs, label maps, dataset_summary.json")


if __name__ == "__main__":
    run()
