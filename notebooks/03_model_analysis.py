"""Kaggle-friendly VIRIDITAS plant identification model error analysis.

Loads the trained plant_id_model.keras, evaluates it on the test set, and
produces a confusion matrix, classification report, per-class accuracy
breakdown, misclassified image samples, and a dataset-source bias check.

Run after 02_train_plant_model.py has produced plant_id_model.keras.
"""

from __future__ import annotations

import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import tensorflow as tf
from sklearn.metrics import classification_report, confusion_matrix

PROJECT_ROOT = Path(__file__).resolve().parent.parent

METADATA_DIR = (
    Path("/kaggle/working/data/metadata")
    if Path("/kaggle").exists()
    else PROJECT_ROOT / "data" / "metadata"
)

MODEL_DIR = (
    Path("/kaggle/working/models")
    if Path("/kaggle").exists()
    else PROJECT_ROOT / "models" / ".v01"
)

OUTPUT_DIR = MODEL_DIR / "analysis"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

MODEL_PATH = MODEL_DIR / "best_plant_model.keras"


def load_test_data() -> tuple[pd.DataFrame, dict[str, int]]:
    df = pd.read_csv(METADATA_DIR / "plant_id_dataset.csv")
    df = df[df["plant"].notna() & (df["plant"] != "")]

    label_map_path = METADATA_DIR / "label_map_plants_used.json"
    if label_map_path.exists():
        label_map = json.loads(label_map_path.read_text())
    else:
        classes = sorted(df["task_plant_label"].unique())
        label_map = {label: index for index, label in enumerate(classes)}

    test_df = df[df["split"] == "test"].reset_index(drop=True)
    return test_df, label_map


def _load_image(path: str) -> tf.Tensor:
    image = tf.io.read_file(path)
    image = tf.image.decode_image(image, channels=3, expand_animations=False)
    image.set_shape([None, None, 3])
    image = tf.image.resize(image, IMAGE_SIZE)
    image = tf.keras.applications.efficientnet_v2.preprocess_input(image)
    return image


def make_test_dataset(test_df: pd.DataFrame, label_map: dict[str, int]) -> tf.data.Dataset:
    paths = test_df["image_path"].tolist()
    labels = [label_map[label] for label in test_df["task_plant_label"]]

    def _load(path, label):
        return _load_image(path), label

    ds = tf.data.Dataset.from_tensor_slices((paths, labels))
    ds = ds.map(_load, num_parallel_calls=tf.data.AUTOTUNE)
    ds = ds.batch(BATCH_SIZE).prefetch(tf.data.AUTOTUNE)
    return ds


def run_predictions(
    model: tf.keras.Model,
    test_ds: tf.data.Dataset,
) -> np.ndarray:
    """
    Run model inference.

    Returns:
        probs (N x num_classes)
    """

    print("\n" + "=" * 70)
    print("Running inference...")
    print("=" * 70)

    probs = model.predict(
        test_ds,
        verbose=1,
    )

    return probs


def save_prediction_results(
    test_df: pd.DataFrame,
    probs: np.ndarray,
    class_names: list[str],
) -> pd.DataFrame:
    """
    Build the master analysis dataframe.

    This dataframe becomes the single source of truth for
    every analysis performed after inference.
    """

    print("\n" + "=" * 70)
    print("Building analysis dataframe...")
    print("=" * 70)

    # --------------------------------------------------
    # Top-K Predictions
    # --------------------------------------------------
    top3_indices = np.argsort(probs, axis=1)[:, -3:][:, ::-1]

    predicted_index = top3_indices[:, 0]

    confidence = probs[
        np.arange(len(probs)),
        predicted_index,
    ]

    # --------------------------------------------------
    # Build Analysis DataFrame
    # --------------------------------------------------
    analysis_df = test_df.copy()

    analysis_df["true_label"] = analysis_df["task_plant_label"]

    analysis_df["true_index"] = [
        class_names.index(label)
        for label in analysis_df["true_label"]
    ]

    analysis_df["predicted_index"] = predicted_index

    analysis_df["predicted_label"] = [
        class_names[i]
        for i in predicted_index
    ]

    analysis_df["confidence"] = confidence

    analysis_df["correct"] = (
        analysis_df["true_index"]
        == analysis_df["predicted_index"]
    )

    # --------------------------------------------------
    # Top-3 Predictions
    # --------------------------------------------------
    analysis_df["top1"] = [
        class_names[i]
        for i in top3_indices[:, 0]
    ]

    analysis_df["top2"] = [
        class_names[i]
        for i in top3_indices[:, 1]
    ]

    analysis_df["top3"] = [
        class_names[i]
        for i in top3_indices[:, 2]
    ]

    analysis_df["top1_prob"] = probs[
        np.arange(len(probs)),
        top3_indices[:, 0]
    ]

    analysis_df["top2_prob"] = probs[
        np.arange(len(probs)),
        top3_indices[:, 1]
    ]

    analysis_df["top3_prob"] = probs[
        np.arange(len(probs)),
        top3_indices[:, 2]
    ]

    # --------------------------------------------------
    # Probability Columns (Research Ready)
    # --------------------------------------------------
    print("Saving per-class probabilities...")

    probability_df = pd.DataFrame(
        probs,
        columns=[
            f"prob_{label}"
            for label in class_names
        ],
    )

    analysis_df = pd.concat(
        [
            analysis_df.reset_index(drop=True),
            probability_df.reset_index(drop=True),
        ],
        axis=1,
    )

    # --------------------------------------------------
    # Save
    # --------------------------------------------------
    output_path = OUTPUT_DIR / "prediction_results.csv"

    analysis_df.to_csv(
        output_path,
        index=False,
    )

    print(f"Saved analysis dataframe to:\n{output_path}")

    print(f"Rows    : {len(analysis_df)}")
    print(f"Columns : {len(analysis_df.columns)}")

    return analysis_df



def compute_topk_accuracy(
    probs: np.ndarray,
    y_true: np.ndarray,
    k: int = 3,
) -> float:
    """
    Compute Top-K Accuracy.
    """

    topk = np.argsort(probs, axis=1)[:, -k:]

    correct = np.any(topk == y_true[:, None], axis=1)

    accuracy = float(correct.mean())

    print(f"Top-{k} Accuracy: {accuracy:.4f}")

    return accuracy


def save_confusion_matrix(y_true: np.ndarray, y_pred: np.ndarray, class_names: list[str]) -> np.ndarray:
    cm = confusion_matrix(y_true, y_pred, labels=range(len(class_names)))

    fig, ax = plt.subplots(figsize=(10, 8))
    im = ax.imshow(cm, cmap="Blues")
    ax.set_xticks(range(len(class_names)))
    ax.set_yticks(range(len(class_names)))
    ax.set_xticklabels(class_names, rotation=45, ha="right")
    ax.set_yticklabels(class_names)
    ax.set_xlabel("Predicted")
    ax.set_ylabel("True")
    ax.set_title("Plant Identification Confusion Matrix (Test Set)")

    for i in range(len(class_names)):
        for j in range(len(class_names)):
            value = cm[i, j]
            if value > 0:
                ax.text(
                    j, i, str(value),
                    ha="center", va="center",
                    color="white" if value > cm.max() / 2 else "black",
                    fontsize=7,
                )

    fig.colorbar(im, ax=ax)
    fig.tight_layout()
    out_path = OUTPUT_DIR / "confusion_matrix.png"
    fig.savefig(out_path, dpi=150)
    plt.close(fig)
    print(f"Saved confusion matrix to {out_path}")

    np.savetxt(OUTPUT_DIR / "confusion_matrix.csv", cm, fmt="%d", delimiter=",",
               header=",".join(class_names), comments="")
    return cm


def save_classification_report(y_true: np.ndarray, y_pred: np.ndarray, class_names: list[str]) -> dict:
    report = classification_report(
        y_true, y_pred, target_names=class_names, output_dict=True, zero_division=0
    )
    report_text = classification_report(
        y_true, y_pred, target_names=class_names, zero_division=0
    )
    print("\n--- Classification Report ---")
    print(report_text)

    (OUTPUT_DIR / "classification_report.json").write_text(json.dumps(report, indent=2))
    (OUTPUT_DIR / "classification_report.txt").write_text(report_text)
    return report


def per_class_accuracy(cm: np.ndarray, class_names: list[str]) -> pd.DataFrame:
    correct = np.diag(cm)
    totals = cm.sum(axis=1)
    accuracy = np.divide(correct, totals, out=np.zeros_like(correct, dtype=float), where=totals != 0)

    df = pd.DataFrame({
        "plant": class_names,
        "test_images": totals,
        "correct": correct,
        "accuracy": accuracy,
    }).sort_values("accuracy")

    print("\n--- Per-Class Accuracy (worst to best) ---")
    print(df.to_string(index=False))

    df.to_csv(OUTPUT_DIR / "per_class_accuracy.csv", index=False)
    return df


def plot_per_class_accuracy(
    df: pd.DataFrame,
) -> None:
    """
    Plot per-class accuracy.
    """

    print("\nCreating per-class accuracy plot...")

    plt.figure(figsize=(10, 6))

    plt.barh(
        df["plant"],
        df["accuracy"],
    )

    plt.xlabel("Accuracy")

    plt.ylabel("Plant Class")

    plt.title("Per-Class Accuracy (Worst → Best)")

    plt.xlim(0, 1)

    plt.tight_layout()

    plt.savefig(
        OUTPUT_DIR / "per_class_accuracy.png",
        dpi=150,
    )

    plt.close()

    print("Saved per_class_accuracy.png")


def report_most_confused_pairs(
    cm: np.ndarray,
    class_names: list[str],
    top_n: int = 10,
) -> pd.DataFrame:
    """
    Report the most common misclassification pairs.

    Example:
        Apple -> Pear : 42
        Bean -> Pea   : 37
    """

    rows = []

    for true_idx in range(len(class_names)):
        for pred_idx in range(len(class_names)):

            if true_idx == pred_idx:
                continue

            count = cm[true_idx, pred_idx]

            if count > 0:
                rows.append({
                    "true_class": class_names[true_idx],
                    "predicted_class": class_names[pred_idx],
                    "count": int(count),
                })

    df = (
        pd.DataFrame(rows)
        .sort_values("count", ascending=False)
        .reset_index(drop=True)
    )

    print("\n")
    print("=" * 70)
    print("TOP CONFUSED CLASS PAIRS")
    print("=" * 70)

    print(df.head(top_n).to_string(index=False))

    df.to_csv(
        OUTPUT_DIR / "most_confused_pairs.csv",
        index=False,
    )

    return df

def confidence_analysis(
    analysis_df: pd.DataFrame,
) -> None:
    """
    Analyze model confidence.

    Produces:

    - histogram
    - summary statistics
    - most confident mistakes
    """

    print("\n")
    print("=" * 70)
    print("CONFIDENCE ANALYSIS")
    print("=" * 70)

    correct = analysis_df[
        analysis_df["correct"]
    ]

    wrong = analysis_df[
        ~analysis_df["correct"]
    ]

    print(f"Correct predictions : {len(correct)}")
    print(f"Wrong predictions   : {len(wrong)}")

    print()

    print(
        "Average confidence (correct):",
        f"{correct['confidence'].mean():.4f}"
    )

    print(
        "Average confidence (wrong):",
        f"{wrong['confidence'].mean():.4f}"
    )

    plt.figure(figsize=(8,5))

    plt.hist(
        correct["confidence"],
        bins=30,
        alpha=0.6,
        label="Correct",
    )

    plt.hist(
        wrong["confidence"],
        bins=30,
        alpha=0.6,
        label="Wrong",
    )

    plt.xlabel("Prediction Confidence")

    plt.ylabel("Images")

    plt.title("Confidence Distribution")

    plt.legend()

    plt.tight_layout()

    plt.savefig(
        OUTPUT_DIR / "confidence_histogram.png",
        dpi=150,
    )

    plt.close()

    wrong.sort_values(
        "confidence",
        ascending=False,
    ).head(20).to_csv(
        OUTPUT_DIR /
        "most_confident_mistakes.csv",
        index=False,
    )

    print(
        "\nSaved confidence analysis."
    )


def save_misclassified_samples(
    analysis_df: pd.DataFrame,
    class_names: list[str],
) -> None:
    """
    Save a complete list of misclassified samples and create
    image grids for each true class.
    """

    print("\n" + "=" * 70)
    print("Sampling misclassified images")
    print("=" * 70)

    misclassified_df = analysis_df.loc[
        ~analysis_df["correct"]
    ].copy()

    misclassified_df.rename(
        columns={
            "predicted_label": "pred_label",
        },
        inplace=True,
    )

    misclassified_df.to_csv(
        OUTPUT_DIR / "misclassified_full_list.csv",
        index=False,
    )

    for true_label in class_names:

        subset = misclassified_df[
            misclassified_df["true_label"] == true_label
        ]

        if subset.empty:
            continue

        sample = subset.sample(
            min(
                NUM_MISCLASSIFIED_SAMPLES_PER_CLASS,
                len(subset),
            ),
            random_state=42,
        )

        n = len(sample)
        cols = min(n, 3)
        rows = (n + cols - 1) // cols

        fig, axes = plt.subplots(
            rows,
            cols,
            figsize=(cols * 3, rows * 3),
        )

        axes = np.atleast_1d(axes).flatten()

        for ax, (_, row) in zip(
            axes,
            sample.iterrows(),
        ):

            try:
                raw = tf.io.read_file(
                    row["image_path"]
                )

                img = tf.image.decode_image(
                    raw,
                    channels=3,
                    expand_animations=False,
                )

                ax.imshow(img.numpy())

            except Exception:

                ax.text(
                    0.5,
                    0.5,
                    "Unreadable",
                    ha="center",
                    va="center",
                )

            ax.set_title(
                (
                    f"True : {row['true_label']}\n"
                    f"Pred : {row['pred_label']}\n"
                    f"Conf : {row['confidence']:.2%}"
                ),
                fontsize=8,
            )

            ax.axis("off")

        for ax in axes[n:]:
            ax.axis("off")

        fig.tight_layout()

        safe_name = (
            true_label
            .replace(" ", "_")
            .replace("/", "_")
        )

        fig.savefig(
            OUTPUT_DIR / f"misclassified_{safe_name}.png",
            dpi=120,
        )

        plt.close(fig)

    print(
        f"Saved misclassified samples to:\n{OUTPUT_DIR}"
    )


def dataset_source_bias_check(
    analysis_df: pd.DataFrame,
) -> pd.DataFrame:
    """
    Analyze model performance across different dataset sources.
    """

    print("\n" + "=" * 70)
    print("Dataset Source Analysis")
    print("=" * 70)

    dataset_df = (
        analysis_df
        .groupby("dataset_name")
        .agg(
            samples=("correct", "size"),
            correct=("correct", "sum"),
            accuracy=("correct", "mean"),
            avg_confidence=("confidence", "mean"),
        )
        .reset_index()
    )

    dataset_df["accuracy"] *= 100

    dataset_df = dataset_df.sort_values(
        "accuracy",
        ascending=True,
    )

    output_path = OUTPUT_DIR / "dataset_accuracy.csv"

    dataset_df.to_csv(
        output_path,
        index=False,
    )

    print(dataset_df)

    print(f"\nSaved dataset analysis to:\n{output_path}")

    return dataset_df



def plot_dataset_accuracy(
    dataset_df: pd.DataFrame,
) -> None:

    dataset_df = dataset_df.sort_values("accuracy")

    plt.figure(figsize=(10,6))

    plt.barh(
        dataset_df.index,
        dataset_df["accuracy"],
    )

    plt.xlabel("Accuracy")

    plt.ylabel("Dataset")

    plt.title("Accuracy by Dataset Source")

    plt.xlim(0,1)

    plt.tight_layout()

    plt.savefig(
        OUTPUT_DIR / "dataset_accuracy.png",
        dpi=150,
    )

    plt.close()

    print("Saved dataset_accuracy.png")



def run() -> None:
    print("GPUs available:", tf.config.list_physical_devices("GPU"))

    print(f"Loading model from {MODEL_PATH}")
    model = tf.keras.models.load_model(MODEL_PATH)

    test_df, label_map = load_test_data()
    class_names = [
        label
        for label, _ in sorted(label_map.items(), key=lambda kv: kv[1])
    ]

    print(f"Test images: {len(test_df)}")
    print(f"Classes: {len(class_names)}")

    # --------------------------------------------------
    # Build Dataset
    # --------------------------------------------------
    test_ds = make_test_dataset(test_df, label_map)


    # --------------------------------------------------
    # Run Inference
    # --------------------------------------------------
    probs = run_predictions(
        model,
        test_ds,
    )

    # --------------------------------------------------
    # Build Analysis DataFrame
    # --------------------------------------------------
    analysis_df = save_prediction_results(
        test_df,
        probs,
        class_names,
    )

    # --------------------------------------------------
    # Ground Truth & Predictions
    # --------------------------------------------------
    y_true = analysis_df["true_index"].to_numpy()
    y_pred = analysis_df["predicted_index"].to_numpy()


    # --------------------------------------------------
    # Accuracy
    # --------------------------------------------------
    test_accuracy = float((y_true == y_pred).mean())

    top3_accuracy = compute_topk_accuracy(
        probs,
        y_true,
        k=3,
    )

    print(f"\nOverall Test Accuracy : {test_accuracy:.4f}")
    print(f"Top-3 Accuracy        : {top3_accuracy:.4f}")

    # --------------------------------------------------
    # Confidence Analysis
    # --------------------------------------------------
    confidence_analysis(
        analysis_df,
    )

    # --------------------------------------------------
    # Confusion Matrix
    # --------------------------------------------------
    cm = save_confusion_matrix(
        y_true,
        y_pred,
        class_names,
    )

    # --------------------------------------------------
    # Most Confused Pairs
    # --------------------------------------------------
    confused_pairs = report_most_confused_pairs(
        cm,
        class_names,
    )

    # --------------------------------------------------
    # Classification Report
    # --------------------------------------------------
    save_classification_report(
        y_true,
        y_pred,
        class_names,
    )

    # --------------------------------------------------
    # Per-Class Accuracy
    # --------------------------------------------------
    per_class_df = per_class_accuracy(
        cm,
        class_names,
    )

    plot_per_class_accuracy(
        per_class_df,
    )


    # --------------------------------------------------
    # Misclassified Images
    # --------------------------------------------------
    save_misclassified_samples(
        analysis_df,
        class_names,
    )

    # --------------------------------------------------
    # Dataset Bias Analysis
    # --------------------------------------------------
    dataset_df = dataset_source_bias_check(
        analysis_df,
    )

    plot_dataset_accuracy(
        dataset_df,
    )

    # --------------------------------------------------
    # Executive Summary
    # --------------------------------------------------
    summary = {
        "test_accuracy": test_accuracy,
        "top3_accuracy": top3_accuracy,
        "num_test_images": len(test_df),
        "num_classes": len(class_names),
        "most_confused_pair": (
            confused_pairs.iloc[0].to_dict()
            if not confused_pairs.empty
            else None
        ),
    }

    (OUTPUT_DIR / "analysis_summary.json").write_text(
        json.dumps(summary, indent=2)
    )

    print("\n" + "=" * 70)
    print("VIRIDITAS MODEL ANALYSIS COMPLETE")
    print("=" * 70)
    print(f"Overall Accuracy : {test_accuracy:.4f}")
    print(f"Top-3 Accuracy   : {top3_accuracy:.4f}")

    print("\n")
    print("=" * 70)
    print("EXECUTIVE SUMMARY")
    print("=" * 70)

    print(f"Top-1 Accuracy : {test_accuracy:.4f}")
    print(f"Top-3 Accuracy : {top3_accuracy:.4f}")

    print("\nWorst 5 Classes")
    print(
        per_class_df.head(5)[
            ["plant", "accuracy"]
        ].to_string(index=False)
    )

    print("\nBest 5 Classes")
    print(
        per_class_df.tail(5)[
            ["plant", "accuracy"]
        ].to_string(index=False)
    )

    print("\nWorst Dataset Sources")
    print(
        dataset_df.head(5).to_string()
    )



    print(f"Results saved to : {OUTPUT_DIR}")

if __name__ == "__main__":
    run()