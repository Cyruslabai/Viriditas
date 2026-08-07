from __future__ import annotations

from pathlib import Path
import json
import numpy as np
import pandas as pd
import tensorflow as tf

from viriditas.config import paths, image_config
from viriditas.training import dataset as dataset_module
from viriditas.inference import loader
from viriditas.evaluation import metrics, reports, visualization


class Evaluator:
    """Run full evaluation pipeline and produce reports/visualizations."""

    def __init__(self, output_dir: Path | None = None):
        self.output_dir = output_dir or (paths.models_dir / "analysis")
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def load_test_data(self):
        import time

        t = time.time()
        print("Reading metadata...")
        df = dataset_module.load_metadata(use_artifact=True)
        print(f"Metadata loaded in {time.time() - t:.2f}s")
        print(f"Rows: {len(df)}")

        t = time.time()
        print("Loading label map...")
        label_map = loader.get_label_map()
        print(f"Label map loaded in {time.time() - t:.2f}s")

        return df, label_map
    def build_test_dataset(self, test_df: pd.DataFrame, label_map: dict[str,int]):
        ds, n = dataset_module.make_dataset(test_df, label_map, "test", shuffle=False) if False else (None, 0)
        # reuse notebook logic: build tf.data.Dataset directly
        paths_list = test_df["image_path"].tolist()
        labels = [label_map[label] for label in test_df["task_plant_label"]]

        def _load(path, label):
            image = dataset_module.preprocessor.load_from_path(path) if hasattr(dataset_module, 'preprocessor') else None
            # fallback to viriditas.preprocessing
            from viriditas.preprocessing import ImagePreprocessor
            pre = ImagePreprocessor()
            return pre.load_from_path(path), label

        ds = tf.data.Dataset.from_tensor_slices((paths_list, labels))
        ds = ds.map(lambda p, l: (_load(p,l)[0], _load(p,l)[1]), num_parallel_calls=tf.data.AUTOTUNE)
        ds = ds.batch(image_config.BATCH_SIZE).prefetch(tf.data.AUTOTUNE)
        return ds, len(paths_list)

    def run(self) -> pd.DataFrame:
        print("Loading test data...")
        test_df, label_map = self.load_test_data()
        print(f"Test rows: {len(test_df)}")

        class_names = sorted(label_map, key=lambda k: label_map[k])

        print("Loading model...")
        model = loader.get_model()

        print("Running inference...")
        test_ds, n = self.build_test_dataset(test_df, label_map)
        probs = model.predict(test_ds, verbose=1)

        print("✓ Inference complete")

        print("Saving prediction results...")
        analysis_df = reports.save_prediction_results(
            test_df,
            probs,
            class_names,
            output_dir=self.output_dir,
        )
        print("✓ Prediction results saved")

        print("Computing metrics...")
        y_true = analysis_df["true_index"].to_numpy()
        y_pred = analysis_df["predicted_index"].to_numpy()

        report = metrics.classification_report_dict(y_true, y_pred, class_names)
        prf = metrics.precision_recall_f1(y_true, y_pred)
        per_class_acc = metrics.per_class_accuracy(y_true, y_pred)
        print("✓ Metrics computed")

        print("Generating confusion matrix...")
        cm = visualization.compute_confusion(y_true, y_pred)
        visualization.plot_confusion_matrix(
            cm,
            class_names,
            output_path=self.output_dir / "confusion_matrix.png",
        )
        print("✓ Confusion matrix saved")

        print("Generating Top-K visualization...")
        visualization.plot_topk_distribution(
            probs,
            k=3,
            output_path=self.output_dir / "topk_distribution.png",
        )
        print("✓ Top-K visualization saved")

        print("Saving evaluation summary...")
        summary = {
            "classification_report": report,
            "precision_recall_f1": prf,
            "per_class_accuracy": per_class_acc,
        }
        (self.output_dir / "evaluation_summary.json").write_text(json.dumps(summary, indent=2))
        print("✓ Evaluation complete!")

        return analysis_df