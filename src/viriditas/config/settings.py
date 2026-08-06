"""Configuration settings using lightweight dataclasses."""

from dataclasses import dataclass, field
from pathlib import Path
from typing import ClassVar, Optional

from viriditas.config.environment import Environment, detect_environment


@dataclass
class ModelVersionConfig:
    """Centralized model versioning configuration.

    This is the single source of truth for model versioning. Change MODEL_VERSION
    once and all model paths update automatically:
    - BEST_MODEL_FILENAME: Official model name (e.g., viriditas_best_v02.keras)
    - TRAINING_HISTORY_FILENAME: Versioned training history (e.g., viriditas_training_history_v02.json)

    The best validation checkpoint is the canonical model. No separate "final model" is saved.
    """
    MODEL_VERSION: str = "v02"

    @property
    def BEST_MODEL_FILENAME(self) -> str:
        """Official model filename (saved during training, loaded for inference)."""
        return f"viriditas_best_{self.MODEL_VERSION}.keras"

    @property
    def TRAINING_HISTORY_FILENAME(self) -> str:
        """Versioned training history filename."""
        return f"viriditas_training_history_{self.MODEL_VERSION}.json"


@dataclass
class PathConfig:
    """Path configuration resolved based on environment.

    This class distinguishes between writable output directories (used during
    indexing and training) and read-only artifact directories (available when
    an artifacts dataset is attached in Kaggle under /kaggle/input).
    """

    environment: Environment = field(default_factory=detect_environment)
    model_version: ModelVersionConfig = field(default_factory=ModelVersionConfig)

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
        """Recursively search /kaggle/input for an artifacts dataset named 'viriditas-artifacts'.

        Looks for directories whose name equals (preferred) or contains 'viriditas-artifacts'
        (case-insensitive). If multiple matches are found for the preferred or fallback search,
        raises RuntimeError to avoid ambiguity. Returns None when not on Kaggle or no match.
        """
        if self.environment != Environment.KAGGLE:
            return None
        input_root = Path("/kaggle/input")
        if not input_root.exists():
            return None
        target = "viriditas-artifacts"
        exact_matches: list[Path] = []
        contains_matches: list[Path] = []
        print("Starting artifact search...")
        # Recursively search all subdirectories without assuming fixed depth
        # Search only dataset directories (avoid traversing every image file)
        for top in input_root.iterdir():
            if not top.is_dir():
                continue

            for owner in top.iterdir():
                if not owner.is_dir():
                    continue

                for dataset in owner.iterdir():
                    if not dataset.is_dir():
                        continue

                    name = dataset.name.lower()

                    if name == target:
                        exact_matches.append(dataset)
                    elif target in name:
                        contains_matches.append(dataset)
        if len(exact_matches) == 1:
            return exact_matches[0]
        if len(exact_matches) > 1:
            raise RuntimeError(
                f"Multiple exact artifact directories found under {input_root}: {', '.join(str(p) for p in exact_matches)}"
            )
        # No exact match — prefer a single contains match
        if len(contains_matches) == 1:
            return contains_matches[0]
        if len(contains_matches) > 1:
            raise RuntimeError(
                f"Multiple artifact directories matching '{target}' found under {input_root}: {', '.join(str(p) for p in contains_matches)}"
            )
        return None

    @property
    def artifact_metadata_dir(self) -> Optional[Path]:
        """Metadata directory inside the attached artifact dataset, if present.

        Detection order:
        1. If artifact root contains metadata files (plant_id_dataset.csv, disease_dataset.csv,
           master_dataset.csv, or label_map_plants_used.json), return artifact root immediately.
        2. Check common layouts: <artifact>/metadata, <artifact>/data/metadata
        3. Scan one level deep for nested metadata directories
        """
        artifact = self.artifact_dir
        if artifact is None:
            return None

        # Expected metadata files that indicate artifact root is the metadata directory
        metadata_indicators = {
            "plant_id_dataset.csv",
            "disease_dataset.csv",
            "master_dataset.csv",
            "label_map_plants_used.json",
        }

        # Check if artifact root itself contains metadata files
        if any((artifact / filename).exists() for filename in metadata_indicators):
            return artifact

        # Check common subdirectory layouts
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

    def resolve_best_model_path(self) -> Path:
        """Resolve the path to the canonical model (versioned best checkpoint).

        Uses the centralized MODEL_VERSION from ModelVersionConfig to determine the official
        model filename. Supports:
        - Kaggle model artifacts: recursively searches /kaggle/input/models
        - Kaggle working directory: checks models/ subdirectory
        - Local development: returns models/viriditas_best_vXX.keras

        The best validation checkpoint is the canonical model. There is no separate "final model".

        Returns:
            Path to viriditas_best_vXX.keras

        Raises:
            FileNotFoundError: If the model cannot be found.
        """
        model_filename = self.model_version.BEST_MODEL_FILENAME

        # Try Kaggle artifact first if on Kaggle
        if self.environment == Environment.KAGGLE:
            model_input_root = Path("/kaggle/input/models")
            if model_input_root.exists():
                # Recursively search for the versioned model
                matches = list(model_input_root.rglob(model_filename))
                if matches:
                    return matches[0]

        # Fallback: local models directory
        local_model = self.models_dir / model_filename
        if local_model.exists():
            return local_model

        # Model not found anywhere
        raise FileNotFoundError(
            f"Model '{model_filename}' not found. "
            f"Checked: Kaggle artifact (/kaggle/input/models) and local ({self.models_dir})"
        )

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
model_version_config = ModelVersionConfig()
paths = PathConfig()
image_config = ImageConfig()
training_config = TrainingConfig()
dataset_config = DatasetConfig()
