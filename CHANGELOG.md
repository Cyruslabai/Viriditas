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
  time) so repeat runs skip re-hashing unchanged files. Committed to the repo with a
  `.gitignore` exception (`/data/*` plus `!/data/metadata/`) so it survives fresh
  Kaggle sessions instead of being rebuilt from scratch every time.
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
