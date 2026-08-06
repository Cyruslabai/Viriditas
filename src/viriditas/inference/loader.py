from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, Any

import tensorflow as tf

from viriditas.config import paths, model_version_config

_MODEL: tf.keras.Model | None = None
_LABEL_MAP: dict[str, int] | None = None


def get_model() -> tf.keras.Model:
    """Lazily load and cache the canonical official model.

    Uses the centralized MODEL_VERSION to locate and load viriditas_best_vXX.keras.
    The best validation checkpoint is the canonical model (no separate "final model").

    On Kaggle, automatically locates the model in attached artifacts.
    On local development, uses models/viriditas_best_vXX.keras.

    Returns:
        Cached Keras model instance.

    Raises:
        FileNotFoundError: If the official model cannot be found.
    """
    global _MODEL
    if _MODEL is not None:
        return _MODEL

    model_path = paths.resolve_best_model_path()
    _MODEL = tf.keras.models.load_model(model_path)
    return _MODEL


def get_label_map() -> dict[str, int]:
    global _LABEL_MAP
    if _LABEL_MAP is not None:
        return _LABEL_MAP

    label_path = paths.resolve_metadata_file(
        "label_map_plants.json",
        use_artifact=True,
    )

    print("Loading label map from:", label_path)

    if not label_path.exists():
        raise FileNotFoundError(f"Label map not found at {label_path}")

    _LABEL_MAP = json.loads(label_path.read_text())

    print("Number of classes:", len(_LABEL_MAP))
    print("First keys:", list(_LABEL_MAP.keys())[:10])

    return _LABEL_MAP


def clear_cache() -> None:
    """Clear cached resources (for testing)."""
    global _MODEL, _LABEL_MAP
    _MODEL = None
    _LABEL_MAP = None
