"""Configuration module for VIRIDITAS.

This module provides environment-aware configuration without external dependencies.
All constants are centralized here to avoid hardcoding in notebooks and modules.

Usage:
    from viriditas.config import paths, image_config, training_config, dataset_config

    # Get paths (auto-resolved based on environment)
    print(paths.metadata_dir)
    print(paths.models_dir)

    # Get constants
    print(image_config.SIZE)
    print(training_config.FROZEN_EPOCHS)
    print(dataset_config.ROOTS)
"""

from viriditas.config.environment import Environment, detect_environment
from viriditas.config.settings import (
    PathConfig,
    ImageConfig,
    TrainingConfig,
    DatasetConfig,
    paths,
    image_config,
    training_config,
    dataset_config,
)

__all__ = [
    "Environment",
    "detect_environment",
    "PathConfig",
    "ImageConfig",
    "TrainingConfig",
    "DatasetConfig",
    "paths",
    "image_config",
    "training_config",
    "dataset_config",
]
