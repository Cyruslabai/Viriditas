from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, Any

import tensorflow as tf

from viriditas.config import paths

_MODEL: tf.keras.Model | None = None
_LABEL_MAP: dict[str, int] | None = None


def get_model(model_name: str | None = None) -> tf.keras.Model:
    """Lazily load and cache the Keras model from paths.models_dir.

    Args:
        model_name: optional model filename. Defaults to 'plant_id_model.keras'.
    """
    global _MODEL
    if _MODEL is not None:
        return _MODEL

    model_name = model_name or "plant_id_model.keras"
    model_path = paths.resolve_model_path(model_name)
    if not model_path.exists():
        # Try best model name as fallback
        alt = paths.resolve_model_path("best_plant_model.keras")
        if alt.exists():
            model_path = alt
    _MODEL = tf.keras.models.load_model(model_path)
    return _MODEL


def get_label_map() -> dict[str, int]:
    """Load and cache label_map_plants_used.json from metadata dir."""
    global _LABEL_MAP
    if _LABEL_MAP is not None:
        return _LABEL_MAP

    # Centralized resolution: prefer artifact metadata when available
    label_path = paths.resolve_metadata_file("label_map_plants_used.json", use_artifact=True)
    if not label_path.exists():
        raise FileNotFoundError(f"Label map not found at {label_path}")
    _LABEL_MAP = json.loads(label_path.read_text())
    return _LABEL_MAP


def clear_cache() -> None:
    """Clear cached resources (for testing)."""
    global _MODEL, _LABEL_MAP
    _MODEL = None
    _LABEL_MAP = None
