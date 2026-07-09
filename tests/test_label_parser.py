from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from viriditas.data.label_parser import parse_label
from viriditas.data.normalizer import infer_plant_hint


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


if __name__ == "__main__":
    unittest.main()
