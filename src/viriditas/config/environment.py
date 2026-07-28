"""Environment detection for VIRIDITAS."""

from enum import Enum
from pathlib import Path


class Environment(Enum):
    """Supported execution environments."""

    KAGGLE = "kaggle"
    LOCAL = "local"
    DOCKER = "docker"
    COLAB = "colab"


def detect_environment() -> Environment:
    """Auto-detect current execution environment.

    Returns:
        Environment: Detected environment (KAGGLE, COLAB, DOCKER, or LOCAL)
    """
    if Path("/kaggle").exists():
        return Environment.KAGGLE
    elif Path("/content").exists():  # Google Colab
        return Environment.COLAB
    elif Path("/.dockerenv").exists():
        return Environment.DOCKER
    else:
        return Environment.LOCAL
