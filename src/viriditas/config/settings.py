"""Configuration settings using lightweight dataclasses."""

from dataclasses import dataclass, field
from pathlib import Path
from typing import ClassVar

from viriditas.config.environment import Environment, detect_environment


@dataclass
class PathConfig:
    """Path configuration resolved based on environment."""

    environment: Environment = field(default_factory=detect_environment)

    @property
    def base_data_dir(self) -> Path:
        """Base directory for data."""
        if self.environment == Environment.KAGGLE:
            return Path("/kaggle/working/data")
        elif self.environment == Environment.COLAB:
            return Path("/content/data")
        else:
            return Path("data")

    @property
    def base_models_dir(self) -> Path:
        """Base directory for models."""
        if self.environment == Environment.KAGGLE:
            return Path("/kaggle/working/models")
        elif self.environment == Environment.COLAB:
            return Path("/content/models")
        else:
            return Path("models")

    @property
    def metadata_dir(self) -> Path:
        """Metadata subdirectory."""
        return self.base_data_dir / "metadata"

    @property
    def models_dir(self) -> Path:
        """Models subdirectory."""
        return self.base_models_dir

    def resolve_model_path(self, model_name: str = "plant_id_model.keras") -> Path:
        """Get specific model path."""
        return self.models_dir / model_name

    def resolve_metadata_file(self, filename: str) -> Path:
        """Get specific metadata file path."""
        path = self.metadata_dir / filename
        path.parent.mkdir(parents=True, exist_ok=True)
        return path


@dataclass
class ImageConfig:
    """Image processing constants."""

    SIZE: tuple[int, int] = (224, 224)
    CHANNELS: int = 3
    BATCH_SIZE: int = 32
    EXTENSIONS: frozenset = field(
        default_factory=lambda: frozenset({
            ".jpg", ".jpeg", ".png", ".bmp", ".webp", ".tif", ".tiff"
        })
    )


@dataclass
class TrainingConfig:
    """Model training hyperparameters."""

    FROZEN_EPOCHS: int = 5
    FINE_TUNE_EPOCHS: int = 5
    FINE_TUNE_AT_LAYER: int = 100
    LEARNING_RATE_FROZEN: float = 1e-3
    LEARNING_RATE_FINE_TUNE: float = 1e-5
    RANDOM_SEED: int = 42
    PATIENCE: int = 2


@dataclass
class DatasetConfig:
    """Dataset configuration."""

    # Kaggle dataset roots
    ROOTS: ClassVar[list[str]] = [
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
    PRESERVE_SOURCE_SPLITS: bool = True
    DEDUP_PREFER_SPLIT: str = "train"


# Global singleton instances
paths = PathConfig()
image_config = ImageConfig()
training_config = TrainingConfig()
dataset_config = DatasetConfig()
