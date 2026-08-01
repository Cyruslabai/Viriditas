from pathlib import Path
import tempfile
import unittest

import tensorflow as tf

from viriditas.data.duplicates import find_duplicates, sha256_file
from viriditas.data.schemas import ImageRecord
from viriditas.data.label_parser import parse_label
from viriditas.data.normalizer import infer_plant_hint
from viriditas.data.index_builder import build_dataset_index
from viriditas.data.layout_detection import infer_label_info
from viriditas.data.splits import assign_splits
from viriditas.training import dataset as dataset_module


def make_record_for_duplicates(index: int, image_path: Path) -> ImageRecord:
    return ImageRecord(
        image_path=str(image_path),
        dataset_name="dataset",
        dataset_root=str(image_path.parent),
        source_split="",
        original_label="Tomato___healthy",
        plant="Tomato",
        disease="Healthy",
        is_healthy=True,
        task_plant_label="Tomato",
        task_disease_label="Tomato Healthy",
        file_name=image_path.name,
        file_ext=image_path.suffix,
        image_id=f"dataset:{index}",
    )


class DuplicateDetectionTests(unittest.TestCase):
    def test_sha256_file_is_stable(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            image_path = Path(tmp) / "leaf_a.jpg"
            image_path.write_bytes(b"same-image-bytes")

            self.assertEqual(sha256_file(image_path), sha256_file(image_path))

    def test_find_duplicates_groups_exact_duplicate_files(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            first = root / "leaf_a.jpg"
            second = root / "leaf_b.jpg"
            unique = root / "leaf_c.jpg"
            first.write_bytes(b"same-image-bytes")
            second.write_bytes(b"same-image-bytes")
            unique.write_bytes(b"different-image-bytes")

            records = [
                make_record_for_duplicates(1, first),
                make_record_for_duplicates(2, second),
                make_record_for_duplicates(3, unique),
            ]
            duplicate_groups = find_duplicates(records)

        self.assertEqual(len(duplicate_groups), 1)
        duplicate_records = next(iter(duplicate_groups.values()))
        self.assertEqual({record.file_name for record in duplicate_records}, {"leaf_a.jpg", "leaf_b.jpg"})

    def test_find_duplicates_ignores_unreadable_missing_paths(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            missing = Path(tmp) / "missing.jpg"
            records = [make_record_for_duplicates(1, missing)]

            self.assertEqual(find_duplicates(records), {})


class LabelParserTests(unittest.TestCase):
    def test_parses_plantvillage_label(self) -> None:
        parsed = parse_label("Tomato___Early_blight")

        self.assertEqual(parsed.plant, "Tomato")
        self.assertEqual(parsed.disease, "Early Blight")
        self.assertFalse(parsed.is_healthy)

    def test_parses_healthy_label(self) -> None:
        parsed = parse_label("Apple___healthy")

        self.assertEqual(parsed.plant, "Apple")
        self.assertEqual(parsed.disease, "Healthy")
        self.assertTrue(parsed.is_healthy)

    def test_uses_single_crop_dataset_hint_for_disease_only_label(self) -> None:
        parsed = parse_label("Early_Blight", plant_hint="Potato")

        self.assertEqual(parsed.plant, "Potato")
        self.assertEqual(parsed.disease, "Early Blight")
        self.assertFalse(parsed.is_healthy)

    def test_removes_repeated_plant_prefix_with_hint(self) -> None:
        parsed = parse_label("Tomato_Late_blight", plant_hint="Tomato")

        self.assertEqual(parsed.plant, "Tomato")
        self.assertEqual(parsed.disease, "Late Blight")

    def test_infers_plant_hint_from_dataset_name(self) -> None:
        hint = infer_plant_hint("/kaggle/input/datasets/rizwan/potato-disease-leaf-datasetpld")

        self.assertEqual(hint, "Potato")

    def test_replaces_generic_container_folder_with_plant_hint(self) -> None:
        parsed = parse_label("Data___Common_rust", ("Data", "Common_rust"), plant_hint="Corn")

        self.assertEqual(parsed.plant, "Corn")
        self.assertEqual(parsed.disease, "Common Rust")

    def test_collapses_augmented_disease_suffixes(self) -> None:
        parsed = parse_label("Peach___Bacterial_spot_Brightness_Adjusted")

        self.assertEqual(parsed.plant, "Peach")
        self.assertEqual(parsed.disease, "Bacterial Spot")

    def test_removes_repeated_plant_suffix_from_disease(self) -> None:
        parsed = parse_label(
            "Orange___Citrus_Nutrient_Deficiency_Yellow_Leaf_Orange",
            plant_hint="Orange",
        )

        self.assertEqual(parsed.plant, "Orange")
        self.assertEqual(parsed.disease, "Citrus Nutrient Deficiency Yellow Leaf")


class LayoutDetectionTests(unittest.TestCase):
    def test_detects_split_class_folder_layout(self) -> None:
        root = Path("/dataset")
        image_path = root / "train" / "Tomato___Early_blight" / "leaf.jpg"

        info = infer_label_info(image_path, root)

        self.assertEqual(info.source_split, "train")
        self.assertEqual(info.original_label, "Tomato___Early_blight")
        self.assertEqual(info.layout_type, "split_class_folder")

    def test_detects_nested_plant_disease_layout(self) -> None:
        root = Path("/dataset")
        image_path = root / "Apple" / "Black_rot" / "leaf.jpg"

        info = infer_label_info(image_path, root)

        self.assertEqual(info.original_label, "Apple___Black_rot")
        self.assertEqual(info.layout_type, "nested_plant_disease")

    def test_builds_records_from_single_crop_dataset(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "potato-disease-leaf-datasetpld"
            image_dir = root / "Training" / "Early_Blight"
            image_dir.mkdir(parents=True)
            (image_dir / "leaf.jpg").write_bytes(b"fake")

            records = build_dataset_index([root], path_mode="relative")

        self.assertEqual(len(records), 1)
        self.assertEqual(records[0].plant, "Potato")
        self.assertEqual(records[0].disease, "Early Blight")
        self.assertEqual(records[0].source_split, "train")
        self.assertEqual(records[0].image_path, "Training/Early_Blight/leaf.jpg")


class SplitTests(unittest.TestCase):
    def make_record(self, index: int, label: str = "Tomato Early Blight", source_split: str = "") -> ImageRecord:
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

    def test_assigns_stratified_splits(self) -> None:
        records = [self.make_record(index) for index in range(10)]

        split_records = assign_splits(records, preserve_source_splits=False)
        split_counts = {split: sum(record.split == split for record in split_records) for split in ("train", "val", "test")}

        self.assertEqual(split_counts["train"], 8)
        self.assertEqual(split_counts["val"], 1)
        self.assertEqual(split_counts["test"], 1)

    def test_preserves_source_splits_but_splits_unsplit_records(self) -> None:
        records = [
            self.make_record(0, source_split="train"),
            self.make_record(1, source_split="val"),
            *[self.make_record(index) for index in range(2, 7)],
        ]

        split_records = assign_splits(records, preserve_source_splits=True)

        self.assertEqual(next(record for record in split_records if record.image_id.endswith("img_0.jpg")).split, "train")
        self.assertEqual(next(record for record in split_records if record.image_id.endswith("img_1.jpg")).split, "val")
        self.assertTrue(any(record.split == "test" for record in split_records if not record.source_split))


def test_make_dataset_returns_dataset_and_count():
    df = dataset_module.load_metadata()
    label_map = dataset_module.build_label_map(df)
    ds, n = dataset_module.make_dataset(df, label_map, 'train', shuffle=False)
    assert isinstance(ds, tf.data.Dataset)
    assert n >= 0
