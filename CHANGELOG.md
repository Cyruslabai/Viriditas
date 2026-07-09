# Changelog

## 2026-07-10

### Fixed

- Improved label parsing after Kaggle metadata validation.
- Replaced generic container folder labels such as `Data`, `Original Dataset`, `Pea Plant Dataset`, and `Test Disease Severity Level` with plant hints inferred from dataset names.
- Collapsed augmentation operation suffixes such as `Brightness Adjusted`, `Gaussian Noise`, and `Rotated` back into the base disease label.
- Removed repeated plant names from disease labels when they appear as disease suffixes.
- Cleared cached `viriditas` modules in the Kaggle runner so reruns use freshly downloaded parser code.

## 2026-07-10

### Added

- Added exact duplicate image detection with SHA-256 hashing in `src/viriditas/data/duplicates.py`.
- Added unit tests for duplicate hashing and duplicate group detection.

### Changed

- Added `.idea/` to `.gitignore` so IDE project files do not get published.
- Replaced the manual duplicate-check script with a deterministic unit test.

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
