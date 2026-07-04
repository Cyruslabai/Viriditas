from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from viriditas.data.schemas import ImageRecord
from viriditas.data.splits import assign_splits


def make_record(index: int, label: str = "Tomato Early Blight", source_split: str = "") -> ImageRecord:
    return ImageRecord(
        image_path=f"img_{index}.jpg",
        dataset_name="dataset",
        dataset_root="/dataset",
        source_split=source_split,
        original_label=label,
        plant=label.split()[0],
        disease=" ".join(label.split()[1:]) or "Unknown",
        is_healthy=False,
        task_plant_label=label.split()[0],
        task_disease_label=label,
        file_name=f"img_{index}.jpg",
        file_ext=".jpg",
        image_id=f"dataset:img_{index}.jpg",
    )


class SplitTests(unittest.TestCase):
    def test_assigns_stratified_splits(self) -> None:
        records = [make_record(index) for index in range(10)]

        split_records = assign_splits(records, preserve_source_splits=False)
        split_counts = {split: sum(record.split == split for record in split_records) for split in ("train", "val", "test")}

        self.assertEqual(split_counts["train"], 8)
        self.assertEqual(split_counts["val"], 1)
        self.assertEqual(split_counts["test"], 1)

    def test_preserves_source_splits_but_splits_unsplit_records(self) -> None:
        records = [
            make_record(0, source_split="train"),
            make_record(1, source_split="val"),
            *[make_record(index) for index in range(2, 7)],
        ]

        split_records = assign_splits(records, preserve_source_splits=True)

        self.assertEqual(next(record for record in split_records if record.image_id.endswith("img_0.jpg")).split, "train")
        self.assertEqual(next(record for record in split_records if record.image_id.endswith("img_1.jpg")).split, "val")
        self.assertTrue(any(record.split == "test" for record in split_records if not record.source_split))


if __name__ == "__main__":
    unittest.main()
