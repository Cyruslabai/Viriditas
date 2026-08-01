from __future__ import annotations

"""Model construction for VIRIDITAS training.

Provides a single function `build_model(num_classes)` that returns a compiled
Keras model (without compiling) and the base backbone. The architecture uses
EfficientNetV2B0 as the feature extractor and a small head with BatchNorm and
Dropout.
"""

import tensorflow as tf
from viriditas.config import image_config


def build_model(num_classes: int) -> tuple[tf.keras.Model, tf.keras.Model]:
    """Build the EfficientNetV2B0 model and classification head.

    Args:
        num_classes: number of output classes for the Dense softmax head.

    Returns:
        (model, base) tuple where `model` is the full Keras Model and `base` is
        the EfficientNetV2B0 backbone (useful for fine-tuning).
    """
    base = tf.keras.applications.EfficientNetV2B0(
        include_top=False,
        weights="imagenet",
        input_shape=image_config.SIZE + (3,),
        pooling="avg",
    )

    base.trainable = False

    data_augmentation = tf.keras.Sequential([
        tf.keras.layers.RandomFlip("horizontal"),
        tf.keras.layers.RandomRotation(0.10),
        tf.keras.layers.RandomZoom(0.10),
        tf.keras.layers.RandomContrast(0.10),
    ], name="data_augmentation")

    inputs = tf.keras.Input(shape=image_config.SIZE + (3,))
    x = data_augmentation(inputs)
    x = base(x, training=False)
    x = tf.keras.layers.BatchNormalization()(x)
    x = tf.keras.layers.Dropout(0.2)(x)

    outputs = tf.keras.layers.Dense(num_classes, activation="softmax")(x)
    model = tf.keras.Model(inputs, outputs)
    return model, base
