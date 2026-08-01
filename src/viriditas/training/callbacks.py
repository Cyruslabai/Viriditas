from __future__ import annotations

from pathlib import Path
import tensorflow as tf
from viriditas.config import paths, training_config


def get_checkpoint_callback(output_dir: Path | None = None, filename: str = "best_plant_model.keras") -> tf.keras.callbacks.ModelCheckpoint:
    output_dir = output_dir or paths.models_dir
    output_dir.mkdir(parents=True, exist_ok=True)
    return tf.keras.callbacks.ModelCheckpoint(
        output_dir / filename,
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
