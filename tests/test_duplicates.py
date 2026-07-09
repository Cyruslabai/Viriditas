from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from viriditas.data.duplicates import find_duplicates, sha256_file
from viriditas.data.schemas import ImageRecord


def make_record(index: int, image_path: Path) -> ImageRecord:
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
                make_record(1, first),
                make_record(2, second),
                make_record(3, unique),
            ]
            duplicate_groups = find_duplicates(records)

        self.assertEqual(len(duplicate_groups), 1)
        duplicate_records = next(iter(duplicate_groups.values()))
        self.assertEqual({record.file_name for record in duplicate_records}, {"leaf_a.jpg", "leaf_b.jpg"})

    def test_find_duplicates_ignores_unreadable_missing_paths(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            missing = Path(tmp) / "missing.jpg"
            records = [make_record(1, missing)]

            self.assertEqual(find_duplicates(records), {})


if __name__ == "__main__":
    unittest.main()
