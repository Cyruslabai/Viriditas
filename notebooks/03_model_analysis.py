"""Thin wrapper for model analysis using the new evaluation package.

This script preserves the previous notebook's interface but delegates
work to viriditas.evaluation.Evaluator for reproducible, testable runs.
'"@

# Build the rest of the file content
$content += @'

from __future__ import annotations

from pathlib import Path
import sys

# Ensure src is importable when running from notebooks/
sys.path.append(str(Path(__file__).resolve().parent.parent / "src"))

from viriditas.evaluation import Evaluator

if __name__ == "__main__":
    evaluator = Evaluator()
    evaluator.run()
