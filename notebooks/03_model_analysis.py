"""Model analysis entrypoint (thin wrapper).

Delegates all evaluation logic to viriditas.evaluation.Evaluator. This script
performs no business logic of its own; it only wires the evaluation package
into a Kaggle-runnable entrypoint.

Run after notebooks/02_train_plant_model.py has produced a trained model.
"""

from __future__ import annotations

from pathlib import Path
import sys

# Ensure src/ is importable when this script is run directly (e.g. from
# notebooks/ in a Kaggle session) rather than via an installed package.
SRC_ROOT = Path(__file__).resolve().parent.parent / "src"
if SRC_ROOT.exists() and str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from viriditas.evaluation import Evaluator


def run() -> None:
    evaluator = Evaluator()
    evaluator.run()


if __name__ == "__main__":
    run()