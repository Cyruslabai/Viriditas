"""Evaluation metrics helpers.

Provides small wrappers around sklearn metrics and per-class accuracy
calculations used by the evaluation pipeline.
"""

from __future__ import annotations

from typing import List, Dict, Any
import numpy as np
from sklearn.metrics import classification_report, precision_recall_fscore_support


def classification_report_dict(y_true: np.ndarray, y_pred: np.ndarray, labels: List[str]) -> Dict[str, Any]:
    """Return sklearn classification report as a dict.

    Args:
        y_true: 1D numpy array of integer true labels.
        y_pred: 1D numpy array of integer predicted labels.
        labels: list of class names, ordered by index.
    """
    report = classification_report(y_true, y_pred, target_names=labels, output_dict=True)
    return report


def precision_recall_f1(y_true: np.ndarray, y_pred: np.ndarray, average: str = "weighted") -> Dict[str, float]:
    """Return precision, recall and f1 as floats under the given averaging mode."""
    p, r, f1, _ = precision_recall_fscore_support(y_true, y_pred, average=average, zero_division=0)
    return {"precision": float(p), "recall": float(r), "f1": float(f1)}


def per_class_accuracy(y_true: np.ndarray, y_pred: np.ndarray) -> Dict[int, float]:
    """Compute accuracy for each class present in y_true.

    Returns a mapping from integer label index to accuracy in [0,1].
    """
    unique = np.unique(y_true)
    acc: Dict[int, float] = {}
    for cls in unique:
        idx = y_true == cls
        acc[int(cls)] = float((y_pred[idx] == y_true[idx]).mean()) if idx.any() else 0.0
    return acc
