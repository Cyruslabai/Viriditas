"""Build VIRIDITAS metadata CSV files from one or more dataset roots.

Example:
    python scripts/build_dataset_index.py --dataset-root /kaggle/input/my-dataset
"""

from __future__ import annotations

import argparse
from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = PROJECT_ROOT / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from viriditas.data.index_builder import build_dataset_index
from viriditas.data.io import write_label_map, write_records_csv, write_split_csvs, write_summary
from viriditas.data.splits import assign_splits


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build VIRIDITAS dataset metadata indexes.")
    parser.add_argument(
        "--dataset-root",
        action="append",
        required=True,
        help="Dataset root directory. Pass multiple times for multiple Kaggle datasets.",
    )
    parser.add_argument(
        "--output-dir",
        default="data/metadata",
        help="Directory for generated CSV, JSON, and summary files.",
    )
    parser.add_argument(
        "--path-mode",
        choices=("absolute", "relative"),
        default="absolute",
        help="Store image paths as absolute paths or paths relative to each dataset root.",
    )
    parser.add_argument("--train-ratio", type=float, default=0.8)
    parser.add_argument("--val-ratio", type=float, default=0.1)
    parser.add_argument("--test-ratio", type=float, default=0.1)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument(
        "--ignore-source-splits",
        action="store_true",
        help="Create new stratified splits even if datasets already contain train/val/test folders.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    output_dir = Path(args.output_dir)

    records = build_dataset_index(args.dataset_root, path_mode=args.path_mode)
    records = assign_splits(
        records,
        train_ratio=args.train_ratio,
        val_ratio=args.val_ratio,
        test_ratio=args.test_ratio,
        seed=args.seed,
        preserve_source_splits=not args.ignore_source_splits,
    )

    write_records_csv(records, output_dir / "master_dataset.csv")
    write_records_csv(records, output_dir / "plant_id_dataset.csv")
    write_records_csv(records, output_dir / "disease_dataset.csv")
    write_split_csvs(records, output_dir)
    write_label_map(records, "task_plant_label", output_dir / "label_map_plants.json")
    write_label_map(records, "task_disease_label", output_dir / "label_map_diseases.json")
    write_summary(records, output_dir / "dataset_summary.json")

    print(f"Indexed {len(records)} images")
    print(f"Wrote metadata to {output_dir.resolve()}")


if __name__ == "__main__":
    main()
