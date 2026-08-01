from __future__ import annotations

import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path
from typing import Sequence


def plot_topk_distribution(probs: np.ndarray, k: int = 3, output_path: Path | None = None):
    topk = np.argsort(probs, axis=1)[:, -k:][:, ::-1]
    counts = np.bincount(topk[:, 0].flatten())
    plt.figure(figsize=(10,4))
    plt.bar(np.arange(len(counts)), counts)
    plt.xlabel('Class index')
    plt.ylabel('Top-1 count')
    plt.tight_layout()
    if output_path:
        plt.savefig(output_path)
    plt.close()


# Confusion utilities (moved from confusion.py)
from typing import Sequence
from sklearn.metrics import confusion_matrix
import seaborn as sns


def compute_confusion(y_true: np.ndarray, y_pred: np.ndarray) -> np.ndarray:
    return confusion_matrix(y_true, y_pred)


def plot_confusion_matrix(cm: np.ndarray, labels: Sequence[str], output_path=None, figsize=(10,10)) -> None:
    plt.figure(figsize=figsize)
    sns.heatmap(cm, annot=True, fmt="d", xticklabels=labels, yticklabels=labels, cmap="Blues")
    plt.xlabel("Predicted")
    plt.ylabel("True")
    plt.tight_layout()
    if output_path:
        plt.savefig(output_path)
    plt.close()
