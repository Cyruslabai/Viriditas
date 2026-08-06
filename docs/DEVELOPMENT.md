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
4. For Kaggle training reruns, export the generated metadata as a `viriditas-artifacts` dataset and attach it to the notebook.

Training
--------
- Use the thin notebook wrapper or programmatic API:
  from viriditas.training import PlantIdentifierTrainer
  trainer = PlantIdentifierTrainer()
  trainer.run()

- Hyperparameters and paths are centralized in `viriditas.config` (training_config, image_config, paths, model_version_config).
- `PlantIdentifierTrainer.run()` requests artifact-backed metadata on Kaggle and loads `label_map_plants.json` through the inference loader so class indices match the generated metadata.
- The best validation checkpoint is automatically saved as the official model using the versioned filename:
  - Example: `viriditas_best_v02.keras` (when MODEL_VERSION = "v02")
  - NO separate "final model" is saved—the checkpoint IS the canonical model.
- Training history is saved with a matching versioned filename:
  - Example: `viriditas_training_history_v02.json`

**To switch model versions:** Edit `src/viriditas/config/settings.py` and change:
```python
MODEL_VERSION = "v03"
```
All training, evaluation, and inference paths update automatically.

Inference
---------
- Use `PlantPredictor` from `viriditas.inference`:
  from viriditas.inference import PlantPredictor
  p = PlantPredictor()
  p.predict(path)

- loader.get_model()/get_label_map() can be used to access underlying resources if needed.
- Model and label-map resources are loaded lazily and cached on first use.

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
