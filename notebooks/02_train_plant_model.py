"""Kaggle-friendly VIRIDITAS baseline plant identification model trainer.

Trains an EfficientNetV2B0 transfer-learning model on plant_id_dataset.csv.
Run after 01_dataset_index_builder.py has produced the metadata CSVs.
"""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd
import tensorflow as tf
from sklearn.utils.class_weight import compute_class_weight

METADATA_DIR = Path("/kaggle/working/data/metadata") if Path("/kaggle").exists() else Path("data/metadata")
OUTPUT_DIR = Path("/kaggle/working/models") if Path("/kaggle").exists() else Path("models")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

IMAGE_SIZE = (224, 224)
BATCH_SIZE = 32
FROZEN_EPOCHS = 5
FINE_TUNE_EPOCHS = 5
FINE_TUNE_AT_LAYER = 100  # unfreeze layers from this index onward during fine-tuning
SEED = 42


def load_metadata() -> pd.DataFrame:
    df = pd.read_csv(METADATA_DIR / "plant_id_dataset.csv")
    df = df[df["plant"].notna() & (df["plant"] != "")]
    return df


def build_label_map(df: pd.DataFrame) -> dict[str, int]:
    classes = sorted(df["task_plant_label"].unique())
    return {label: index for index, label in enumerate(classes)}


def make_dataset(df: pd.DataFrame, label_map: dict[str, int], split: str, shuffle: bool) -> tf.data.Dataset:
    subset = df[df["split"] == split].reset_index(drop=True)
    paths = subset["image_path"].tolist()
    labels = [label_map[label] for label in subset["task_plant_label"]]

    def _load(path, label):
        image = tf.io.read_file(path)
        image = tf.image.decode_image(
            image,
            channels=3,
            expand_animations=False,
        )
        image.set_shape([None, None, 3])
        image = tf.image.resize(image, IMAGE_SIZE)
        image = tf.keras.applications.efficientnet_v2.preprocess_input(image)
        return image, label

    ds = tf.data.Dataset.from_tensor_slices((paths, labels))
    if shuffle:
        ds = ds.shuffle(buffer_size=min(len(paths), 10000), seed=SEED)
    ds = ds.map(_load, num_parallel_calls=tf.data.AUTOTUNE)
    ds = ds.batch(BATCH_SIZE).prefetch(tf.data.AUTOTUNE)
    return ds, len(paths)

def build_model(num_classes: int) -> tf.keras.Model:

    base = tf.keras.applications.EfficientNetV2B0(
        include_top=False,
        weights="imagenet",
        input_shape=IMAGE_SIZE + (3,),
        pooling="avg",
    )

    base.trainable = False

    data_augmentation = tf.keras.Sequential([
        tf.keras.layers.RandomFlip("horizontal"),
        tf.keras.layers.RandomRotation(0.10),
        tf.keras.layers.RandomZoom(0.10),
        tf.keras.layers.RandomContrast(0.10),
    ], name="data_augmentation")

    inputs = tf.keras.Input(shape=IMAGE_SIZE + (3,))

    x = data_augmentation(inputs)
    x = base(x, training=False)
    x = tf.keras.layers.BatchNormalization()(x)
    x = tf.keras.layers.Dropout(0.2)(x)

    outputs = tf.keras.layers.Dense(
        num_classes,
        activation="softmax"
    )(x)

    model = tf.keras.Model(inputs, outputs)

    return model, base

def compute_weights(df: pd.DataFrame, label_map: dict[str, int]) -> dict[int, float]:
    train_labels = df[df["split"] == "train"]["task_plant_label"].map(label_map)
    weights = compute_class_weight(
        class_weight="balanced",
        classes=np.unique(train_labels),
        y=train_labels,
    )
    return dict(zip(np.unique(train_labels), weights))


checkpoint = tf.keras.callbacks.ModelCheckpoint(
    OUTPUT_DIR / "best_plant_model.keras",
    monitor="val_loss",
    save_best_only=True,
    verbose=1,
)

early_stop = tf.keras.callbacks.EarlyStopping(
    monitor="val_loss",
    patience=2,
    restore_best_weights=True,
    verbose=1,
)

def run() -> None:
    print("GPUs available:", tf.config.list_physical_devices("GPU"))

    df = load_metadata()
    label_map = build_label_map(df)
    num_classes = len(label_map)
    print(f"Classes ({num_classes}):", list(label_map.keys()))

    (METADATA_DIR / "label_map_plants_used.json").write_text(json.dumps(label_map, indent=2))

    train_ds, n_train = make_dataset(df, label_map, "train", shuffle=True)
    val_ds, n_val = make_dataset(df, label_map, "val", shuffle=False)
    test_ds, n_test = make_dataset(df, label_map, "test", shuffle=False)
    print(f"Train: {n_train}  Val: {n_val}  Test: {n_test}")

    class_weights = compute_weights(df, label_map)

    model, base = build_model(num_classes)
    model.compile(
        optimizer=tf.keras.optimizers.Adam(learning_rate=1e-3),
        loss="sparse_categorical_crossentropy",
        metrics=["accuracy"],
    )
    model.summary()

    print("\n--- Phase 1: frozen base ---")
    history1 = model.fit(
        train_ds,
        validation_data=val_ds,
        epochs=FROZEN_EPOCHS,
        class_weight=class_weights,
        callbacks=[checkpoint, early_stop],
    )

    print("\n--- Phase 2: fine-tuning ---")
    base.trainable = True
    for layer in base.layers[:FINE_TUNE_AT_LAYER]:
        layer.trainable = False

    model.compile(
        optimizer=tf.keras.optimizers.Adam(learning_rate=1e-5),
        loss="sparse_categorical_crossentropy",
        metrics=["accuracy"],
    )
    history2 = model.fit(
        train_ds,
        validation_data=val_ds,
        epochs=FINE_TUNE_EPOCHS,
        class_weight=class_weights,
        callbacks=[checkpoint, early_stop],
    )

    print("\n--- Test evaluation ---")
    test_loss, test_acc = model.evaluate(test_ds)
    print(f"Test loss: {test_loss:.4f}  Test accuracy: {test_acc:.4f}")

    model.save(OUTPUT_DIR / "plant_id_model.keras")
    print(f"Model saved to {OUTPUT_DIR / 'plant_id_model.keras'}")

    history = {
        "frozen": {k: [float(v) for v in vals] for k, vals in history1.history.items()},
        "fine_tune": {k: [float(v) for v in vals] for k, vals in history2.history.items()},
        "test_loss": float(test_loss),
        "test_accuracy": float(test_acc),
    }
    (OUTPUT_DIR / "plant_id_training_history.json").write_text(json.dumps(history, indent=2))


if __name__ == "__main__":
    run()