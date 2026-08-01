"""Thin wrapper to call the refactored PlantIdentifierTrainer.

This module preserves Kaggle compatibility by appending src to sys.path when
run as a standalone script (same behaviour as the original notebook).
"""

from __future__ import annotations

from pathlib import Path
import sys

# Preserve the original notebook behaviour when executed from notebooks/ dir
sys.path.append(str(Path(__file__).resolve().parent.parent / "src"))

from viriditas.training import PlantIdentifierTrainer


if __name__ == "__main__":
    trainer = PlantIdentifierTrainer()
    trainer.run()
