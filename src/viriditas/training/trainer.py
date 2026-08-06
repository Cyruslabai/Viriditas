from __future__ import annotations

import json
from pathlib import Path
import tensorflow as tf

from viriditas.config import paths, training_config
from viriditas.training import dataset as dataset_module
from viriditas.training import model as model_module
from viriditas.training import callbacks as callbacks_module
from viriditas.inference.loader import get_label_map


class PlantIdentifierTrainer:
    """Orchestrates dataset loading, model building and training for plant id."""

    def __init__(self, output_dir: Path | None = None):
        self.output_dir = output_dir or paths.models_dir
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def run(self) -> None:
        print("GPUs available:", tf.config.list_physical_devices("GPU"))

        df = dataset_module.load_metadata(use_artifact=True)

        # Load the label map from the artifact dataset
        label_map = get_label_map()
        num_classes = len(label_map)
        print("=" * 60)
        print(f"Dataset rows: {len(df):,}")
        print(f"Unique plant classes: {num_classes}")
        print("Classes:")
        print(sorted(label_map.keys()))
        print("=" * 60)


        train_ds, n_train = dataset_module.make_dataset(df, label_map, "train", shuffle=True)
        val_ds, n_val = dataset_module.make_dataset(df, label_map, "val", shuffle=False)
        test_ds, n_test = dataset_module.make_dataset(df, label_map, "test", shuffle=False)
        print(f"Train: {n_train}  Val: {n_val}  Test: {n_test}")

        class_weights = dataset_module.compute_weights(df, label_map)

        model, base = model_module.build_model(num_classes)
        print("Model output shape:", model.output_shape)
        model.compile(
            optimizer=tf.keras.optimizers.Adam(learning_rate=training_config.LEARNING_RATE_FROZEN),
            loss="sparse_categorical_crossentropy",
            metrics=["accuracy"],
        )
        model.summary()

        checkpoint = callbacks_module.get_checkpoint_callback(self.output_dir)
        early_stop = callbacks_module.get_early_stopping()

        print("\n--- Phase 1: frozen base ---")
        history1 = model.fit(
            train_ds,
            validation_data=val_ds,
            epochs=training_config.FROZEN_EPOCHS,
            class_weight=class_weights,
            callbacks=[checkpoint, early_stop],
        )

        print("\n--- Phase 2: fine-tuning ---")
        base.trainable = True
        for layer in base.layers[: training_config.FINE_TUNE_AT_LAYER]:
            layer.trainable = False

        model.compile(
            optimizer=tf.keras.optimizers.Adam(learning_rate=training_config.LEARNING_RATE_FINE_TUNE),
            loss="sparse_categorical_crossentropy",
            metrics=["accuracy"],
        )
        history2 = model.fit(
            train_ds,
            validation_data=val_ds,
            epochs=training_config.FINE_TUNE_EPOCHS,
            class_weight=class_weights,
            callbacks=[checkpoint, early_stop],
        )

        print("\n--- Test evaluation ---")
        test_loss, test_acc = model.evaluate(test_ds)
        print(f"Test loss: {test_loss:.4f}  Test accuracy: {test_acc:.4f}")

        model.save(self.output_dir / "plant_id_model.keras")
        print(f"Model saved to {self.output_dir / 'plant_id_model.keras'}")

        history = {
            "frozen": {k: [float(v) for v in vals] for k, vals in history1.history.items()},
            "fine_tune": {k: [float(v) for v in vals] for k, vals in history2.history.items()},
            "test_loss": float(test_loss),
            "test_accuracy": float(test_acc),
        }
        (self.output_dir / "plant_id_training_history.json").write_text(json.dumps(history, indent=2))
