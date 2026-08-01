from __future__ import annotations

from typing import List, Dict, Any
import numpy as np

from viriditas.inference import loader, preprocessing, postprocessing
from viriditas.config import image_config
from pathlib import Path
from typing import Iterable


# Small helper utilities (moved from utils.py)

def validate_image_path(path: str) -> bool:
    p = Path(path)
    return p.exists() and p.is_file()


def partition_batch(items: Iterable, batch_size: int):
    items = list(items)
    return [items[i:i+batch_size] for i in range(0, len(items), batch_size)]


class PlantPredictor:
    """High-level predictor that loads model, preprocesses inputs and returns decoded outputs."""

    def __init__(self, model_name: str | None = None):
        self.model_name = model_name
        self._model = None
        self._label_map = None

    def _ensure_loaded(self) -> None:
        if self._model is None:
            self._model = loader.get_model(self.model_name)
        if self._label_map is None:
            self._label_map = loader.get_label_map()

    def predict(self, image_path: str) -> Dict[str, Any]:
        """Predict a single image file path. Returns decoded result."""
        if not validate_image_path(image_path):
            raise FileNotFoundError(f"Image not found: {image_path}")
        self._ensure_loaded()
        arr = preprocessing.preprocess_path_to_batch(image_path)
        probs = self._model.predict(arr)
        decoded = postprocessing.decode_single(probs, self._label_map)
        return decoded

    def predict_batch(self, image_paths: List[str]) -> List[Dict[str, Any]]:
        """Predict a batch of image paths. Uses batching helpers to avoid memory spikes."""
        self._ensure_loaded()
        # validate
        for p in image_paths:
            if not validate_image_path(p):
                raise FileNotFoundError(f"Image not found: {p}")
        # Use model's batch predict directly — allow variable batch sizes
        arrs = [preprocessing.preprocess_path_to_batch(p) for p in image_paths]
        batch = np.vstack(arrs)
        probs_batch = self._model.predict(batch)
        decoded = postprocessing.decode_batch(probs_batch, self._label_map)
        return decoded
