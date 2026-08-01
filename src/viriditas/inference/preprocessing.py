from __future__ import annotations

from viriditas.preprocessing import ImagePreprocessor

# Reuse the centralized preprocessor to ensure identical preprocessing to training
_PREPROCESSOR: ImagePreprocessor | None = None


def get_preprocessor() -> ImagePreprocessor:
    global _PREPROCESSOR
    if _PREPROCESSOR is None:
        _PREPROCESSOR = ImagePreprocessor()
    return _PREPROCESSOR


def preprocess_path_to_batch(path: str):
    pre = get_preprocessor()
    return pre.preprocess_path_to_batch(path)


def preprocess_bytes_to_batch(data: bytes):
    pre = get_preprocessor()
    return pre.preprocess_bytes_to_batch(data)
