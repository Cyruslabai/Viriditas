from __future__ import annotations

from pathlib import Path
from typing import Tuple

import numpy as np
import pandas as pd
import tensorflow as tf
from sklearn.utils.class_weight import compute_class_weight

from viriditas.config import paths, image_config, training_config
from viriditas.preprocessing import ImagePreprocessor

preprocessor = ImagePreprocessor()
BATCH_SIZE = image_config.BATCH_SIZE
SEED = training_config.RANDOM_SEED


def load_metadata(use_artifact: bool = False) -> pd.DataFrame:
    import time
    print("use_artifact:", use_artifact)
    print("artifact_dir:", paths.artifact_dir)
    print("artifact_metadata_dir:", paths.artifact_metadata_dir)
    print("metadata_dir:", paths.metadata_dir)

    print("Resolving path...")
    t = time.time()

    path = paths.resolve_metadata_file(
        "plant_id_dataset.csv",
        use_artifact=use_artifact
    )

    print("Path:", path)
    print("Resolved in", time.time() - t)

    print("Reading CSV...")
    t = time.time()

    df = pd.read_csv(path)

    print("CSV loaded in", time.time() - t)
    print("Rows:", len(df))

    print("Filtering...")
    t = time.time()

    df = df[df["plant"].notna() & (df["plant"] != "")]

    print("Filtered in", time.time() - t)

    return df

def build_label_map(df: pd.DataFrame) -> dict[str, int]:
    classes = sorted(df["task_plant_label"].unique())
    return {label: index for index, label in enumerate(classes)}


def make_dataset(df: pd.DataFrame, label_map: dict[str, int], split: str, shuffle: bool) -> tuple[tf.data.Dataset, int]:
    subset = df[df["split"] == split].reset_index(drop=True)
    paths_list = subset["image_path"].tolist()
    labels = [label_map[label] for label in subset["task_plant_label"]]

    def _load(path, label):
        image = preprocessor.load_from_path(path)
        return image, label

    ds = tf.data.Dataset.from_tensor_slices((paths_list, labels))
    if shuffle:
        ds = ds.shuffle(buffer_size=min(len(paths_list), 10000), seed=SEED)
    ds = ds.map(_load, num_parallel_calls=tf.data.AUTOTUNE)
    ds = ds.batch(BATCH_SIZE).prefetch(tf.data.AUTOTUNE)
    return ds, len(paths_list)


def compute_weights(df: pd.DataFrame, label_map: dict[str, int]) -> dict[int, float]:
    train_labels = df[df["split"] == "train"]["task_plant_label"].map(label_map)
    weights = compute_class_weight(
        class_weight="balanced",
        classes=np.unique(train_labels),
        y=train_labels,
    )
    return dict(zip(np.unique(train_labels), weights))
