from __future__ import annotations

from typing import Dict, List, Any
import numpy as np


def index_to_label_map(label_map: Dict[str, int]) -> Dict[int, str]:
    """Invert label_map {label: idx} -> {idx: label}"""
    return {v: k for k, v in label_map.items()}


def decode_single(probabilities: np.ndarray, label_map: Dict[str, int]) -> Dict[str, Any]:
    """Decode a single prediction probability vector into human-readable result.

    Returns dict with keys: predicted_label, confidence (0-1), probabilities (dict label->prob)
    """
    if probabilities.ndim == 2:
        probs = probabilities[0]
    else:
        probs = probabilities
    idx_to_label = index_to_label_map(label_map)
    pred_idx = int(np.argmax(probs))
    pred_label = idx_to_label[pred_idx]
    confidence = float(probs[pred_idx])
    probs_dict = {idx_to_label[i]: float(p) for i, p in enumerate(probs)}
    return {
        "predicted_label": pred_label,
        "confidence": confidence,
        "probabilities": probs_dict,
    }


def decode_batch(probabilities_batch: np.ndarray, label_map: Dict[str, int]) -> List[Dict[str, Any]]:
    return [decode_single(probs, label_map) for probs in probabilities_batch]
