from __future__ import annotations

from pathlib import Path
import tensorflow as tf
from viriditas.config import paths, training_config, model_version_config


def get_checkpoint_callback(output_dir: Path | None = None) -> tf.keras.callbacks.ModelCheckpoint:
    """Create a ModelCheckpoint callback that saves the best model with versioned filename.

    Uses the centralized MODEL_VERSION to determine the official model filename
    (viriditas_best_vXX.keras). This is the canonical model—no separate "final model" is saved.

    Args:
        output_dir: Directory to save the model. Defaults to paths.models_dir.

    Returns:
        ModelCheckpoint callback that saves the best validation checkpoint as the official model.
    """
    output_dir = output_dir or paths.models_dir
    output_dir.mkdir(parents=True, exist_ok=True)
    model_filename = model_version_config.BEST_MODEL_FILENAME
    return tf.keras.callbacks.ModelCheckpoint(
        output_dir / model_filename,
        monitor="val_loss",
        save_best_only=True,
        verbose=1,
    )


def get_early_stopping(patience: int | None = None) -> tf.keras.callbacks.EarlyStopping:
    patience = patience if patience is not None else training_config.PATIENCE
    return tf.keras.callbacks.EarlyStopping(
        monitor="val_loss",
        patience=patience,
        restore_best_weights=True,
        verbose=1,
    )
