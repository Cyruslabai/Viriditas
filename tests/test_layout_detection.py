from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from viriditas.data.index_builder import build_dataset_index
from viriditas.data.layout_detection import infer_label_info


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


if __name__ == "__main__":
    unittest.main()
