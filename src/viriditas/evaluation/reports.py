from __future__ import annotations

from pathlib import Path
import pandas as pd
import numpy as np
from typing import List

from viriditas.config import paths


def save_prediction_results(
    test_df: pd.DataFrame,
    probs: np.ndarray,
    class_names: List[str],
    output_dir: Path | None = None,
) -> pd.DataFrame:
    output_dir = output_dir or (paths.models_dir / "analysis")
    output_dir.mkdir(parents=True, exist_ok=True)

    # replicate notebook logic for prediction results
    num_classes = probs.shape[1]
    k = min(3, num_classes)
    topk_indices = np.argsort(probs, axis=1)[:, -k:][:, ::-1]
    predicted_index = topk_indices[:, 0]
    confidence = probs[np.arange(len(probs)), predicted_index]

    analysis_df = test_df.copy()
    analysis_df["true_label"] = analysis_df["task_plant_label"]
    analysis_df["true_index"] = [class_names.index(label) for label in analysis_df["true_label"]]
    analysis_df["predicted_index"] = predicted_index
    analysis_df["predicted_label"] = [class_names[i] for i in predicted_index]
    analysis_df["confidence"] = confidence
    analysis_df["correct"] = analysis_df["true_index"] == analysis_df["predicted_index"]

    # Top-k predictions: fill missing ranks with None/NaN when fewer than 3 classes
    top1 = [class_names[i] for i in topk_indices[:, 0]]
    analysis_df["top1"] = top1
    analysis_df["top1_prob"] = probs[np.arange(len(probs)), topk_indices[:, 0]]

    if k >= 2:
        analysis_df["top2"] = [class_names[i] for i in topk_indices[:, 1]]
        analysis_df["top2_prob"] = probs[np.arange(len(probs)), topk_indices[:, 1]]
    else:
        analysis_df["top2"] = [None] * len(analysis_df)
        analysis_df["top2_prob"] = [float('nan')] * len(analysis_df)

    if k >= 3:
        analysis_df["top3"] = [class_names[i] for i in topk_indices[:, 2]]
        analysis_df["top3_prob"] = probs[np.arange(len(probs)), topk_indices[:, 2]]
    else:
        analysis_df["top3"] = [None] * len(analysis_df)
        analysis_df["top3_prob"] = [float('nan')] * len(analysis_df)

    # per-class probabilities
    prob_df = pd.DataFrame(probs, columns=[f"prob_{label}" for label in class_names])
    analysis_df = pd.concat([analysis_df.reset_index(drop=True), prob_df.reset_index(drop=True)], axis=1)

    out_path = output_dir / "prediction_results.csv"
    analysis_df.to_csv(out_path, index=False)

    return analysis_df


# Misclassified helpers (moved from misclassified.py)

def get_misclassified(analysis_df: pd.DataFrame) -> pd.DataFrame:
    """Return rows where prediction != true label."""
    return analysis_df[~analysis_df["correct"]].reset_index(drop=True)


def sample_misclassified_images(analysis_df: pd.DataFrame, sample_n: int = 20) -> pd.DataFrame:
    mc = get_misclassified(analysis_df)
    return mc.sample(n=min(len(mc), sample_n))
