# VIRIDITAS Project Plan

Last updated: 2026-07-11

## Project Vision

VIRIDITAS is a local-first AI agricultural assistant. Its core mission is to identify plants from leaf images, diagnose plant-specific diseases, and provide practical treatment, fertilizer, prevention, and farming guidance. The long-term product direction includes offline inference, local AI explanations, weather-aware recommendations, voice interaction, desktop and mobile apps, and optional cloud synchronization.

## Current Architecture

The target system is split into independent layers:

```text
Leaf Image
    |
    v
Plant Identification Model
    |
    v
Disease Classification Model
    |
    v
AI Recommendation Engine
    |
    v
Treatment | Fertilizer | Prevention | Future AI Chat
```

### Model 1: Plant Identification

- Input: Leaf image
- Output: Plant species
- Role: Identify the crop before disease diagnosis and future recommendations

### Model 2: Disease Classification

- Input: Leaf image and plant context
- Output: Disease label for that plant, including healthy classes
- Role: Diagnose the plant-specific condition

### Recommendation Engine

- Planned input: Plant, disease, confidence, image-derived signals, weather, user context, and sensor data
- Planned output: Treatment steps, fertilizer suggestions, prevention guidance, and AI explanations

## Current Repository State

The repository currently contains an earlier Flask prototype:

- `app.py`: Flask API for disease prediction and sensor data
- `index.html`: Web dashboard
- `arduino_sensor_sender.ino`: ESP32 sensor sender sketch
- `test.py`: Local manual image prediction script
- `requirements.txt`: Prototype dependencies
- `images/`: Training graph images
- `src/viriditas/data/`: Metadata-based preprocessing package
- `scripts/build_dataset_index.py`: Dataset index builder CLI
- `notebooks/01_dataset_index_builder.ipynb` / `.py`: Kaggle preprocessing notebook and runner
- `data/metadata/`: Generated metadata CSVs plus the committed `hash_cache.csv` dedup cache
- `tests/`: Unit tests for preprocessing behavior

The Flask prototype is useful but does not yet match the planned scalable VIRIDITAS inference architecture. The preprocessing layer is now the first implemented part of the new VIRIDITAS architecture, and is now considered feature-complete and validated for the initial 13 datasets.

## Planned Folder Structure

```text
VIRIDITAS/
|-- data/
|   |-- raw/                       External datasets, usually ignored by git
|   |-- metadata/                  Generated dataset indexes, split CSVs, and hash_cache.csv
|-- notebooks/
|   |-- 01_dataset_index_builder.ipynb
|   |-- 01_dataset_index_builder.py
|   |-- 02_train_plant_model.ipynb
|   |-- 03_train_disease_model.ipynb
|   |-- 04_inference.ipynb
|-- scripts/
|   |-- build_dataset_index.py
|-- src/
|   |-- viriditas/
|       |-- data/                  Scanners, parsers, label normalization, dedup
|       |-- models/                Training and model utilities
|       |-- inference/             End-to-end prediction pipeline
|       |-- recommendations/       Treatment and guidance generation
|-- tests/                         Unit and integration tests
|-- docs/
|   |-- JOURNAL.md                 Chronological project memory
|   |-- KAGGLE_RUNBOOK.md          Kaggle restart and rerun guide
|-- PROJECT_PLAN.md
|-- README.md
|-- CHANGELOG.md
|-- TODO.md
```

## Dataset Strategy

The project will use metadata indexing instead of physically reorganizing images.

### Old Approach

Images were copied into new folders such as:

```text
PlantID/
DiseaseID/
train/
validation/
test/
```

### Problem

- Huge storage duplication
- Kaggle disk space exhaustion
- Slow preprocessing
- Training layout tightly coupled to one folder structure

### Current Approach

Keep original images in place and build CSV indexes:

```text
image_path, dataset_name, original_label, plant, disease, is_healthy, split
```

Recommended metadata files:

- `master_dataset.csv`: One row per image
- `plant_id_dataset.csv`: Plant classification view
- `disease_dataset.csv`: Disease classification view
- `train.csv`, `val.csv`, `test.csv`: Split metadata
- `label_map_plants.json`: Plant class mapping
- `label_map_diseases.json`: Disease class mapping
- `dataset_summary.json`: Quick counts by dataset, plant, disease, and split
- `hash_cache.csv`: SHA-256 hash cache used for duplicate detection and dedup speedup

## Current Kaggle Dataset Roots

The first preprocessing pass is configured for these Kaggle datasets:

```text
/kaggle/input/datasets/rizwan123456789/potato-disease-leaf-datasetpld
/kaggle/input/datasets/showravdhar/apple-disease-dataset
/kaggle/input/datasets/shuvokumarbasak2030/cherry-leaf-diseases-plant-village-augmented-data
/kaggle/input/datasets/smaranjitghose/corn-or-maize-leaf-disease-dataset
/kaggle/input/datasets/rm1000/grape-disease-dataset-original
/kaggle/input/datasets/zunorain/pea-plant-dataset
/kaggle/input/datasets/shuvokumarbasak2030/peach-leaf-diseases-plant-village-augmented-data
/kaggle/input/datasets/shuvokumarbasak4004/orange-leaf-disease-dataset
/kaggle/input/datasets/ashishmotwani/tomato
/kaggle/input/datasets/usmanafzaal/strawberry-disease-detection-dataset
/kaggle/input/datasets/sivm205/soybean-diseased-leaf-dataset
/kaggle/input/datasets/tahmidmir/pumpkin-leaf-diseases-dataset-from-bangladesh
/kaggle/input/datasets/shuvokumarbasak2030/pepper-leaf-diseases-plant-village-augmented-data
```

## Dataset Format Detection

The index builder should support:

- Flat class folders
- Existing `train`, `valid`, `validation`, and `test` folders
- Nested plant and disease folders
- PlantVillage-style labels such as `Tomato___Early_blight`
- Dataset-specific label naming variations
- Flat split folders with no class subfolder, where the label is encoded in the filename
  (e.g. `test/angular_leafspot351.jpg`)
- Nested non-informative container folders (e.g. `Test Disease Severity Level/Level 1/`)
  that must be stripped before falling back to filename-based labels

## Canonical Metadata Schema

Current schema (implemented and populated end to end as of 2026-07-11):

```text
image_path
dataset_name
dataset_root
source_split
original_label
plant
disease
is_healthy
task_plant_label
task_disease_label
file_name
file_ext
image_id
duplicate_group_id
split
```

`image_path` should be absolute or dataset-root-relative depending on notebook portability needs. For Kaggle notebooks, root-relative paths are usually safer.

`duplicate_group_id` is the first 16 hex characters of each image's SHA-256 hash. Every
row has one, whether or not it is part of a duplicate group, so duplicate groups can be
inspected directly from `master_dataset.csv` without rerunning detection.

## Model Architecture Direction

Initial recommendation:

- Use transfer learning for both models.
- Start with EfficientNetV2B0, MobileNetV3, or ConvNeXt-Tiny depending on device target.
- Keep the plant model and disease model separate at first for cleaner debugging.
- Later evaluate a multi-task model only after the dataset is stable.

## Design Decisions

### Decision: Use metadata instead of copying images

Date: 2026-07-04

Reason:

- Avoids storage duplication
- Works better on Kaggle disk limits
- Allows new datasets to be added without rewriting training code
- Keeps preprocessing independent from training

### Decision: Split notebooks by pipeline stage

Date: 2026-07-04

Notebook plan:

- `01_dataset_index_builder.ipynb`
- `02_train_plant_model.ipynb`
- `03_train_disease_model.ipynb`
- `04_inference.ipynb`

Reason:

- Keeps preprocessing, training, and inference independent
- Makes notebooks easier to rerun and debug
- Supports future refactoring into scripts and packages

### Decision: Use two models first

Date: 2026-07-04

Reason:

- Clearer separation between plant identification and disease classification
- Easier to debug dataset labeling errors
- Easier to expand plant coverage before disease coverage
- Future multi-task or hierarchical models remain possible

### Decision: Normalize dataset container and augmentation labels

Date: 2026-07-10

Reason:

- Kaggle metadata validation showed plant labels such as `Data`, `Original Dataset`, `Pea Plant Dataset`, and `Test Disease Severity Level`.
- Augmented datasets created separate labels such as `Peach Bacterial Spot Brightness Adjusted`.
- These labels would incorrectly increase the number of plant and disease classes.

Action:

- Use dataset-name plant hints when folder labels are generic containers.
- Strip augmentation operation suffixes from disease labels.
- Remove repeated plant names from disease labels when they appear as suffixes.

### Decision: Add filename-based label fallback and non-informative folder stripping

Date: 2026-07-11

Reason:

- The 2026-07-10 fix resolved bad plant labels, but the fix had not actually been
  pushed to GitHub `main` (local/remote branches had diverged), so Kaggle kept running
  stale code until this was caught and corrected.
- After confirming the push, 2,507 `Unknown` disease rows remained, almost entirely
  (2,500 of 2,507) from `strawberry-disease-detection-dataset`.
- That dataset uses two folder layouts the parser didn't handle: a flat `test/` split
  folder with no class subfolder (disease name encoded in the filename instead, e.g.
  `angular_leafspot351.jpg`), and a nested `Test Disease Severity Level/Level 1/`
  container that was being misparsed into fake "Level 1"/"Level 2" disease classes.

Action:

- Added a filename-based label extraction fallback in `layout_detection.py`, triggered
  when no usable class folder exists.
- Added stripping of non-informative folder names (severity-level containers) so the
  parser falls through to the filename fallback instead of using the container name
  as the label.
- Added one disease alias (`angular leafspot` -> `Angular Leaf Spot`) for consistent casing.

### Decision: Wire duplicate detection into the pipeline and resolve cross-split leakage

Date: 2026-07-11

Reason:

- `duplicates.py` had SHA-256 hashing logic and unit tests, but was never actually
  called from `index_builder.py`. `duplicate_group_id` existed in the planned schema
  but was never populated in real output.
- A manual duplicate-group review found 7,571 duplicate groups (15,209 images) across
  the dataset. 3,057 of those groups (6,176 images) spanned more than one split
  (train/val/test), almost entirely from the augmented plant-village-style datasets
  (peach, pepper, cherry) and the strawberry and tomato datasets. This is a real
  train/test leakage risk that would inflate evaluation metrics during model training.

Action:

- Added `deduplicate_records()` to `duplicates.py`, tagging every image with a
  `duplicate_group_id` and, for any group spanning multiple splits, keeping exactly
  one copy (preferring `train`) and dropping the rest.
- Added a hash cache (`data/metadata/hash_cache.csv`) so repeat builds skip re-hashing
  unchanged files, and committed it to the repo (with a `.gitignore` exception) so the
  speedup persists across fresh Kaggle sessions, not just within one session.
- Wired the new function into `01_dataset_index_builder.py`, run immediately after
  `assign_splits()` and before any CSV is written.
- Fixed `splits.py`'s `_replace_split` to use `dataclasses.replace` instead of manually
  listing every field, so it won't silently drop future schema additions the way it
  would have dropped `duplicate_group_id` if left as-is.

Result: dataset size went from 201,094 to 197,975 images (3,119 rows dropped), with
0 cross-split leakage confirmed via a fresh pipeline rebuild (not just a manual patch).

## Current Progress

Completed:

- Identified storage problem caused by image copying
- Chose metadata-first dataset strategy
- Chose staged notebooks for preprocessing, training, and inference
- Established project documentation rules
- Created project source-of-truth documentation
- Approved dataset index builder architecture
- Implemented `src/viriditas/data/` preprocessing package
- Implemented Kaggle/local dataset index builder entrypoints
- Added tests for label parsing, layout detection, and split generation
- Added exact duplicate image detection using SHA-256 hashes
- Validated Kaggle metadata output for 201,094 images
- Improved parser rules for generic dataset folders and augmented class folders
- Added a project journal and Kaggle runbook so progress can be resumed after Kaggle session resets
- Verified 2026-07-10 parser fixes were live on GitHub after resolving a local/remote branch divergence
- Reran the full dataset index builder in Kaggle and confirmed 0 rows for all four bad plant labels
- Added filename-based label extraction fallback for datasets with no class folders
- Added non-informative folder stripping for nested severity-level subfolders
- Resolved 2,507 Unknown disease rows down to 7 (a genuinely unlabeled folder in the apple dataset)
- Fixed a stray `agriai` import left over from the project rename
- Wired duplicate detection into the pipeline (`deduplicate_records()`), populating
  `duplicate_group_id` on every row for the first time
- Resolved 6,176 cross-split leaked images (3,057 duplicate groups) down to 0, dataset
  now 197,975 images
- Added and committed a hash cache to speed up future rebuilds

In progress:

- None — preprocessing/label-quality/duplicate-leakage milestones are complete

Not started:

- Plant identification model training
- Disease classification model training
- Recommendation engine

## Current Task

Start model training. Preprocessing is validated and stable: 197,975 images, 0 bad
plant labels, 7 residual genuinely-unlabeled images (apple dataset, low priority),
0 cross-split duplicate leakage, all wired permanently into the pipeline (not manual
patches). Next concrete steps, in order:

1. Decide handling for the 7 remaining unlabeled apple images (drop from
   `master_dataset.csv` before training, or leave as a tiny `Unknown` class — dropping
   is the simpler and lower-risk default).
2. Create `notebooks/02_train_plant_model.ipynb`.
3. Train a baseline plant identification model (see Model Architecture Direction above
   for the recommended starting architectures).

Resume guide:

- To rebuild the dataset index from a fresh Kaggle session: pull the repo via the
  GitHub API cell, `%cd` into it, then `%run notebooks/01_dataset_index_builder.py`.
  This now runs label parsing, split assignment, and duplicate resolution in one pass
  and reuses `data/metadata/hash_cache.csv` for already-hashed files.
- Use `docs/KAGGLE_RUNBOOK.md` to redownload the repo and rerun preprocessing in Kaggle.
- Use `docs/JOURNAL.md` for the chronological record of what happened and why.

## Implemented Dataset Index Builder Architecture

Recommended modules:

```text
src/viriditas/data/
|-- __init__.py
|-- config.py              Dataset paths and supported image extensions
|-- schemas.py             Metadata dataclasses, including duplicate_group_id
|-- scanners.py            Recursive image discovery
|-- layout_detection.py    Detect class-folder, split-folder, and filename-based layouts
|-- label_parser.py        Extract plant and disease labels
|-- normalizer.py          Canonical label normalization
|-- index_builder.py       Build master dataframe
|-- splits.py              Train/validation/test split generation
|-- duplicates.py          SHA-256 hashing, duplicate grouping, cross-split dedup
|-- io.py                  CSV and JSON output helpers
```

Recommended notebook:

```text
notebooks/01_dataset_index_builder.ipynb
```

The notebook should call reusable Python modules instead of containing all logic inline.

## Trade-Offs

### Notebook-only implementation

Pros:

- Fast to prototype
- Easy to inspect in Kaggle

Cons:

- Harder to test
- Harder to reuse
- More likely to become messy as datasets grow

### Script/package implementation with notebook wrapper

Pros:

- Testable
- Reusable
- Cleaner training notebooks
- Easier to maintain as VIRIDITAS grows

Cons:

- Slightly more setup upfront

Decision: Use a small Python package under `src/viriditas/` and keep notebooks thin. This has been implemented for the first preprocessing milestone.

## Next Tasks

1. Decide handling for the 7 remaining unlabeled apple images.
2. Create `02_train_plant_model.ipynb`.
3. Train baseline plant identification model.
4. Create `03_train_disease_model.ipynb`.
5. Train baseline disease classification model.
6. Add unit tests for the filename-based label fallback and non-informative folder
   stripping (both currently untested despite being load-bearing for the strawberry
   dataset's 3,243 images).
7. Add unit tests for `deduplicate_records()` and the hash cache.

## Future Roadmap

- Local model optimization with TensorFlow Lite or ONNX
- AI recommendation engine
- Weather integration
- Fertilizer guidance
- Offline local LLM assistant
- Desktop app
- Mobile app
- Cloud sync and dataset update workflow
- Explainable AI visualizations
- Sensor-aware irrigation recommendations
