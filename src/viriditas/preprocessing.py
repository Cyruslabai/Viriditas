"""Reusable image preprocessing for Viriditas.

Provides a single ImagePreprocessor class that handles loading,
resizing and EfficientNet-specific preprocessing.

Placed as a module to be importable via `from viriditas.preprocessing import ImagePreprocessor`.
"""

from __future__ import annotations

import tensorflow as tf
import numpy as np
from typing import Tuple

from viriditas.config import image_config


class ImagePreprocessor:
    """Load and preprocess images for model training and inference.

    Methods operate on TensorFlow tensors so they can be used inside
    tf.data pipelines (ds.map) and in eager mode for app/test usage.
    """

    def __init__(self, image_size: Tuple[int, int] | None = None):
        self.image_size = tuple(image_size) if image_size is not None else image_config.SIZE
        # EfficientNetV2 specific preprocess input
        self._preprocess_fn = tf.keras.applications.efficientnet_v2.preprocess_input

    def load_from_path(self, path: tf.Tensor) -> tf.Tensor:
        """Read image from a path (string Tensor) and return a preprocessed tensor."""
        img = tf.io.read_file(path)
        img = tf.image.decode_image(img, channels=3, expand_animations=False)
        img.set_shape([None, None, 3])
        img = tf.image.resize(img, self.image_size)
        img = self._preprocess_fn(img)
        return img

    def load_from_bytes(self, data: bytes | tf.Tensor) -> tf.Tensor:
        """Read image from raw bytes and return a preprocessed tensor (no batch dim)."""
        if not isinstance(data, tf.Tensor):
            data = tf.constant(data)
        img = tf.image.decode_image(data, channels=3, expand_animations=False)
        img.set_shape([None, None, 3])
        img = tf.image.resize(img, self.image_size)
        img = self._preprocess_fn(img)
        return img

    def preprocess_path_to_batch(self, path: str) -> np.ndarray:
        """Convenience: return a numpy array with batch dim from a filesystem path."""
        img = self.load_from_path(path)
        # img may be a Tensor or a numpy array depending on execution mode
        if hasattr(img, "numpy"):
            return img.numpy()[None, ...]
        else:
            return np.expand_dims(img, axis=0)

    def preprocess_bytes_to_batch(self, data: bytes) -> np.ndarray:
        """Convenience: return a numpy array with batch dim from raw image bytes."""
        img = self.load_from_bytes(data)
        if hasattr(img, "numpy"):
            return img.numpy()[None, ...]
        else:
            return np.expand_dims(img, axis=0)
