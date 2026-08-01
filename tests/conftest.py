import sys
from pathlib import Path
import pytest

# Ensure src is importable
sys.path.append(str(Path(__file__).resolve().parent.parent / "src"))

import os
from viriditas.config import paths

@pytest.fixture(scope="session")
def models_dir(tmp_path_factory):
    # Use project's models directory (already contains models from smoke runs)
    return paths.models_dir

@pytest.fixture(scope="session")
def sample_image():
    # Path to the sample image moved to test fixtures
    return Path("tests/fixtures/img1.jpg")

@pytest.fixture(scope="session")
def metadata_csv():
    return Path("data/metadata/plant_id_dataset.csv")
