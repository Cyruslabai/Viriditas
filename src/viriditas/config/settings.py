"""Configuration settings using lightweight dataclasses."""

from dataclasses import dataclass, field
from pathlib import Path
from typing import ClassVar, Optional

from viriditas.config.environment import Environment, detect_environment


@dataclass
class PathConfig:
    """Path configuration resolved based on environment.

    This class distinguishes between writable output directories (used during
    indexing and training) and read-only artifact directories (available when
    an artifacts dataset is attached in Kaggle under /kaggle/input).
    """

    environment: Environment = field(default_factory=detect_environment)

    @property
    def base_data_dir(self) -> Path:
        """Base directory for data (writable)."""
        if self.environment == Environment.KAGGLE:
            return Path("/kaggle/working/data")
        elif self.environment == Environment.COLAB:
            return Path("/content/data")
        else:
            return Path("data")

    @property
    def base_models_dir(self) -> Path:
        """Base directory for models (writable)."""
        if self.environment == Environment.KAGGLE:
            return Path("/kaggle/working/models")
        elif self.environment == Environment.COLAB:
            return Path("/content/models")
        else:
            return Path("models")

    @property
    def metadata_dir(self) -> Path:
        """Writable metadata directory (used for training and indexing)."""
        return self.base_data_dir / "metadata"

    @property
    def artifact_dir(self) -> Optional[Path]:
        """Path to an attached artifacts dataset named 'viriditas-artifacts', if any.

        Searches /kaggle/input for a dataset whose directory name contains
        'viriditas-artifacts' (case-insensitive). Returns None when not on
        Kaggle or when no artifact dataset is attached.
        """
        if self.environment != Environment.KAGGLE:
            return None
        input_root = Path("/kaggle/input")
        if not input_root.exists():
            return None
        for entry in input_root.iterdir():
            if not entry.is_dir():
                continue
            if "viriditas-artifacts" in entry.name.lower():
                return entry
        return None

    @property
    def artifact_metadata_dir(self) -> Optional[Path]:
        """Metadata directory inside the attached artifact dataset, if present.

        Common layouts checked:
        - <artifact>/metadata
        - <artifact>/data/metadata
        - single-level metadata dir anywhere under the artifact root
        """
        artifact = self.artifact_dir
        if artifact is None:
            return None
        # Common candidate locations
        candidates = [artifact / "metadata", artifact / "data" / "metadata"]
        for c in candidates:
            if c.exists() and c.is_dir():
                return c
        # Scan one level deep for 'metadata' or '*/metadata'
        for entry in artifact.iterdir():
            if entry.is_dir() and entry.name.lower() == "metadata":
                return entry
            nested = entry / "metadata"
            if nested.exists() and nested.is_dir():
                return nested
        return None

    @property
    def models_dir(self) -> Path:
        """Models subdirectory (writable)."""
        return self.base_models_dir

    def resolve_model_path(self, model_name: str = "plant_id_model.keras") -> Path:
        """Get specific model path (writable)."""
        return self.models_dir / model_name

    def resolve_metadata_file(self, filename: str, use_artifact: bool = False) -> Path:
        """Get specific metadata file path.

        By default returns a path in the writable metadata_dir (for writing).
        When use_artifact=True and an artifact metadata dir exists, returns a
        path inside the artifact metadata directory (read-only).
        """
        if use_artifact and self.artifact_metadata_dir is not None:
            return self.artifact_metadata_dir / filename
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

    PRESERVE_SOURCE_SPLITS: bool = True
    DEDUP_PREFER_SPLIT: str = "train"


# Global singleton instances
paths = PathConfig()
image_config = ImageConfig()
training_config = TrainingConfig()
dataset_config = DatasetConfig()
