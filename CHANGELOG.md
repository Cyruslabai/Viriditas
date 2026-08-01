# CHANGELOG.md

# Changelog

## 2026-08-01 — Phase 9: Production Readiness & Final Cleanup (finalized)

### Fixed

- Removed temporary developer artifacts: smoke_test_phase3.py, smoke_test_inference.py, smoke_test_imports.py, smoke_test_full_imports.py, create_smoke_dataset.py, run_evaluator.py.
- Moved synthetic test image to tests/fixtures/img1.jpg and updated data/metadata/plant_id_dataset.csv to reference the fixture.
- Ran full pytest suite: 21 passed, 4 warnings. Import and architecture verification passed; no circular imports detected.

### Notes

- No changes to ML behavior or production datasets were made as part of this cleanup. Documentation and TODOs were updated to reflect completion.

---

## 2026-08-01

### Added

- Introduced `src/viriditas/config/` as the single configuration system for the
  project: `settings.py`, `environment.py`, and an `__init__.py` exporting
  ready-to-use configuration objects (`paths`, `image_config`, `training_config`,
  `dataset_config`).
- Added automatic environment detection (Local / Kaggle / Google Colab). The
  detected environment now determines metadata paths, model paths, and output
  directories instead of hardcoded per-notebook paths.
- Added a centralized model-input preprocessing implementation inside
  `src/viriditas/` (image loading, resizing, normalization, EfficientNet-specific
  preprocessing) intended to be shared by every future consumer: training,
  evaluation, inference, FastAPI, and Flutter.
- Began production package restructuring under `src/viriditas/`:
  `config/`, `data/`, `preprocessing/`, `training/`, `inference/`, `evaluation/`,
  `models/`, `utils/`.
- Ran architectural smoke tests after the configuration and preprocessing
  refactor: import validation, configuration validation, and centralized
  preprocessing validation all passed. Two environment-specific failures were
  observed (missing `pandas` in an isolated sandbox environment, and a missing
  local model artifact) and confirmed to be environmental setup issues rather
  than architectural regressions. An import conflict encountered during testing
  was also resolved.

### Changed

- Replaced direct configuration constants (`IMAGE_SIZE`, `BATCH_SIZE`,
  `MODEL_DIR`, `OUTPUT_DIR`, `METADATA_DIR`) with configuration objects
  (`image_config.SIZE`, `image_config.BATCH_SIZE`, `paths.models_dir`,
  `paths.metadata_dir`, `paths.resolve_model_path()`, etc.) across the codebase.
- Adopted "thin notebook" as an explicit engineering principle: notebooks may
  only load configuration, call reusable functions from `src/viriditas/`, and
  visualize results. Business logic is no longer permitted to live directly in
  notebook cells.
- Reframed VIRIDITAS's long-term architecture as a reusable AI SDK: the same
  core modules (config, preprocessing, training, inference) are intended to be
  consumed by Kaggle notebooks, a future FastAPI backend, a future Flutter
  client, CLI utilities, and future LLM orchestration, without duplicating
  business logic per consumer.
- Narrowed Version 1 scope to software only. Plant identification, disease
  detection, the recommendation engine, the FastAPI backend, and the Flutter
  client are in scope for V1. Arduino, ESP32, IoT sensors, weather stations, and
  other embedded/hardware integrations are moved to an archived / future
  possibilities category and are explicitly out of scope for V1.

### Planned

- Lazy model loading for the inference package: models should be initialized on
  first use rather than loaded at module import time, to improve startup time,
  ease testing, and integrate cleanly with FastAPI's request lifecycle. Not yet
  implemented; tracked as an in-progress architectural decision.

### Reason

The dataset pipeline and Kaggle-notebook-based training workflow (see the
2026-07-04 through 2026-07-19 entries below) successfully proved out the core
preprocessing and baseline-training approach. As the project grew, configuration
constants and preprocessing logic were duplicated across notebooks, which made
testing, reuse across future consumers (FastAPI, Flutter, CLI, LLM
orchestration), and long-term maintenance increasingly difficult. This refactor
moves VIRIDITAS from a notebook-centric research workflow toward a production
Python package with centralized configuration and preprocessing, without
discarding any of the dataset-quality engineering work already completed.

## 2026-07-19

### Added

- Added `notebooks/02_train_plant_model.py`, a Kaggle-friendly EfficientNetV2B0
  plant identification trainer using class weights, data augmentation, frozen-base
  training, fine-tuning, checkpointing, early stopping, and model/history output.
- Added `notebooks/03_model_analysis.py` for plant-model evaluation: prediction
  results, top-k accuracy, confusion matrix, classification report, per-class
  accuracy, confidence analysis, misclassified samples, dataset-source analysis,
  and an analysis summary.
- Added `.gitkeep` placeholders for generated-artifact directories such as
  `data/metadata/`, `models/`, and `src/viriditas/data/metadata/`.

### Changed

- Added progress logging to the dataset index builder runner.
- Removed dataset caching from the plant training input pipeline to reduce memory
  pressure during Kaggle training.
- Refined `.gitignore` so generated metadata, model files, analysis outputs, caches,
  logs, and temporary files stay out of git while the required directory structure
  remains available.

### Removed

- Removed tracked generated training/metadata artifacts from the repository in favor
  of keeping only placeholder directories. Local generated model files still exist
  under `models/.v01/`, but are intentionally ignored by git.

### Known Follow-Ups

- `notebooks/03_model_analysis.py` needs cleanup before being treated as reliable:
  the local metadata fallback points at `src/viriditas/data/metadata`, the
  misclassified-sample count constant is undefined, and the dataset accuracy plot
  uses percentage values with a 0-1 x-axis limit.
- `src/agriai/` has been reintroduced as a tracked legacy package even though
  `src/viriditas/` is the active namespace; remove or reconcile it. (Note, added
  2026-08-01: this legacy package is historical only and must not be treated as
  an active part of the architecture going forward — see the 2026-08-01 entry.)
- The notebook placeholders for `02_train_plant_model.ipynb` and
  `03_model_analysis.ipynb` are still empty.

## 2026-07-11

### Fixed

- Fixed `scanners.py` importing from the old `agriai` package instead of `viriditas`.
- Added filename-based label extraction fallback in `layout_detection.py` for datasets
  with no class folders (e.g. `strawberry-disease-detection-dataset`), where disease
  names are encoded in filenames like `angular_leafspot351.jpg` instead of folder structure.
- Added stripping of non-informative nested folders (`Test Disease Severity Level`,
  `Level 1`, `Level 2`) so the parser falls through to filename-based labels instead of
  producing garbage disease labels like "Level 1" / "Level 2".
- Added `"angular leafspot": "Angular Leaf Spot"` to `DISEASE_ALIASES` in `normalizer.py`.
- Fixed `splits.py`'s `_replace_split` to use `dataclasses.replace` instead of manually
  listing every `ImageRecord` field, so new fields are carried through automatically
  instead of silently dropped on future schema changes.

### Added

- Added `duplicate_group_id` field to the `ImageRecord` schema and `CSV_FIELDNAMES`
  in `schemas.py` (previously defined in the planned schema but never actually populated).
- Added `deduplicate_records()` to `duplicates.py`, which hashes every image, tags it
  with a `duplicate_group_id`, and resolves any duplicate group that spans more than
  one split (train/val/test) by keeping a single copy — preferring the `train` copy —
  and dropping the rest, eliminating train/test leakage from exact-duplicate images.
- Added a hash cache (`data/metadata/hash_cache.csv`, keyed by file size + modification
  time) so repeat runs skip re-hashing unchanged files.
- Wired `deduplicate_records()` into `notebooks/01_dataset_index_builder.py`, running
  immediately after `assign_splits()` and before any CSV is written, so
  `master_dataset.csv` is leak-free and duplicate-tagged on every build going forward.

### Verified

- Confirmed the 2026-07-10 label-parsing fixes (generic plant folder mapping) were
  actually live on GitHub `main` after discovering a local/remote branch divergence
  had left them unpushed.
- Reran `01_dataset_index_builder.py` on Kaggle after a full session restart; confirmed
  via `master_dataset.csv`:
  - Bad plant labels (`Data`, `Original Dataset`, `Pea Plant Dataset`,
    `Test Disease Severity Level`) are now 0 rows.
  - `Unknown` disease rows dropped from 2,507 to 7 (only a genuinely unlabeled
    `Unknown` folder in the apple dataset remains, 7 images).
  - Strawberry dataset (3,243 images) now fully labeled across its 7 real disease
    classes, with no residual Unknown or Level 1/Level 2 mislabels.
- Manually verified cross-split duplicate leakage: 7,571 duplicate groups (15,209
  images) found via SHA-256 hashing; 3,057 of those groups (6,176 images) spanned
  more than one split. Resolved by dropping 3,119 rows, bringing the dataset from
  201,094 to 197,975 images with zero cross-split leakage.
- Reran the full pipeline after wiring `deduplicate_records()` in permanently;
  confirmed the fresh build independently reproduces the same result (197,975 images,
  `duplicate_group_id` populated on all rows, 0 cross-split leakage) without any
  manual notebook patching.

### Reason

Kaggle metadata validation on 2026-07-10 flagged bad plant labels and Unknown disease
rows, but the parser fixes committed that day were never pushed to GitHub `main` —
Kaggle kept pulling stale code. Additionally, the strawberry dataset uses two
label-free folder layouts (flat split folders, and nested severity-level folders) not
handled by the existing folder-based parser, requiring a new filename-based fallback.
Separately, `duplicates.py` had duplicate-hashing logic implemented and unit-tested,
but was never actually called from `index_builder.py`, so `duplicate_group_id` existed
only as a planned schema field. Investigating this found that several source Kaggle
datasets (particularly augmented plant-village-style datasets and the strawberry
dataset) contain exact-duplicate images split across their own train/val/test folders,
which were being preserved as separate rows in different splits — a train/test leakage
risk that would have inflated model evaluation metrics during training.

## 2026-07-10

### Added

- Added `docs/JOURNAL.md` to record the full VIRIDITAS engineering timeline, Kaggle findings, current risks, and resume point.
- Added `docs/KAGGLE_RUNBOOK.md` with the GitHub API ZIP download cell, preprocessing command, and validation checks for Kaggle restarts.

### Changed

- Updated `README.md`, `PROJECT_PLAN.md`, and `TODO.md` with the current Kaggle preprocessing checkpoint and next validation tasks.

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