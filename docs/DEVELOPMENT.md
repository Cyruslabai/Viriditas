# Development Guide

This guide helps contributors add datasets, train models, and extend inference/evaluation.

Environment
-----------
- Python 3.11+
- Install dependencies: `pip install -r requirements.txt`
- Optional: use a virtual environment or Conda.

Adding datasets
---------------
1. Place data under `data/` following existing Kaggle layouts or raw folders.
2. Run the dataset index builder (notebook or CLI) which generates metadata CSVs:
   - Notebook: `notebooks/01_dataset_index_builder.ipynb`
   - CLI: `python scripts/build_dataset_index.py --dataset-root <path> --output-dir data/metadata`
3. Verify `data/metadata/plant_id_dataset.csv` contains correct `image_path`, `task_plant_label`, and `split` columns.

Training
--------
- Use the thin notebook wrapper or programmatic API:
  from viriditas.training import PlantIdentifierTrainer
  trainer = PlantIdentifierTrainer()
  trainer.run()

- Hyperparameters and paths are centralized in `viriditas.config` (training_config, image_config, paths).
- Outputs: best model (`best_plant_model.keras`), final model (`plant_id_model.keras`), and `plant_id_training_history.json`.

Inference
---------
- Use `PlantPredictor` from `viriditas.inference`:
  from viriditas.inference import PlantPredictor
  p = PlantPredictor()
  p.predict(path)

- loader.get_model()/get_label_map() can be used to access underlying resources if needed.

Evaluation
----------
- Use `Evaluator`:
  from viriditas.evaluation import Evaluator
  ev = Evaluator()
  ev.run()

- Reports and visualizations are saved under `models/analysis/` by default.

Coding guidelines
-----------------
- Prefer using `viriditas.config` values over hardcoded paths.
- Reuse `ImagePreprocessor` to ensure training/inference parity.
- Add unit tests under `tests/` and use fixtures in `tests/conftest.py`.
- Document public APIs with concise docstrings and type hints.

Contributions
-------------
- Create small, focused PRs that include tests for new behavior.
- Preserve backward compatibility for notebook entrypoints.
- Do not commit large model files into the repository.
