# Changelog

## 2026-07-04

### Added

- Renamed the project from AgriAI to VIRIDITAS.
- Renamed the Python package from `agriai` to `viriditas`.
- Implemented metadata preprocessing package under `src/viriditas/data/`.
- Added Kaggle preprocessing notebook: `notebooks/01_dataset_index_builder.ipynb`.
- Added Kaggle-friendly Python runner: `notebooks/01_dataset_index_builder.py`.
- Added local/Kaggle CLI runner: `scripts/build_dataset_index.py`.
- Added unit tests for label parsing, layout detection, single-crop dataset hints, and split generation.
- Added support for the initial 13 Kaggle dataset roots selected for VIRIDITAS preprocessing.
- Added generation for `plant_id_dataset.csv` and `disease_dataset.csv` task views.
- Updated `.gitignore` so root dataset folders stay ignored while `src/viriditas/data/` remains trackable.

### Changed

- Established VIRIDITAS as the forward architecture for the project.
- Documented the move from physical image copying to metadata-based dataset indexing.
- Defined the two-model pipeline: plant identification followed by plant-specific disease classification.
- Defined the staged notebook plan:
  - `01_dataset_index_builder.ipynb`
  - `02_train_plant_model.ipynb`
  - `03_train_disease_model.ipynb`
  - `04_inference.ipynb`
- Updated `README.md` to describe VIRIDITAS, the current prototype, and the planned scalable pipeline.
- Fixed README training graph image links to match the existing image filenames.
- Updated project docs to make the dataset index builder the active preprocessing milestone.

### Earlier Added

- Added `PROJECT_PLAN.md` as the project source of truth.
- Added `TODO.md` as the engineering task list.
- Added this changelog.

### Reason

The previous copy-based preprocessing approach duplicated images, consumed too much storage, and made Kaggle workflows fragile. The metadata-driven approach is more scalable, easier to maintain, and better aligned with future plant identification, disease diagnosis, recommendation, and offline inference goals.
