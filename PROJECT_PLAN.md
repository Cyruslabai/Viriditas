# PROJECT_PLAN.md

# VIRIDITAS Project Plan

Last updated: 2026-08-01 (finalized: 2026-08-01 22:34:21 IST)

Organization: Cyrus Labs AI
Version: Pre-V1

## Project Vision

VIRIDITAS is Cyrus Labs AI's flagship AI software platform for agriculture. Its
core mission is to identify plants from leaf images, diagnose plant-specific
diseases, and provide practical treatment, fertilizer, and prevention guidance
through an AI recommendation engine. VIRIDITAS is designed as a reusable AI SDK:
the same core modules (configuration, preprocessing, training, inference) are
intended to support multiple future consumers — a FastAPI backend, a Flutter
mobile client, CLI utilities, Kaggle notebooks, and future LLM-powered
agricultural assistant orchestration — without duplicating business logic per
consumer.

### Version 1 Scope (Software Only)

Version 1 is explicitly software-only. In scope:

- Plant identification
- Disease detection (plant-specific disease classification)
- AI recommendation engine
- FastAPI backend
- Flutter mobile application
- Future LLM-powered agricultural assistant

Arduino, ESP32, IoT sensors, weather stations, and other embedded/hardware
integrations are **not** part of Version 1. They are retained only as archived
ideas / future possibilities (see Section "Archived Ideas / Future
Possibilities" below) and must not be treated as active architecture.

## Current Architecture

### 1. Model Pipeline (AI Layer)

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

#### Model 1: Plant Identification

- Input: Leaf image
- Output: Plant species
- Role: Identify the crop before disease diagnosis and future recommendations
- Status: Baseline trained (EfficientNetV2B0 transfer learning)

#### Model 2: Disease Classification

- Input: Leaf image and plant context
- Output: Disease label for that plant, including healthy classes
- Role: Diagnose the plant-specific condition
- Status: Not started

#### Recommendation Engine

- Planned input: Plant, disease, confidence, image-derived signals, user context
- Planned output: Treatment steps, fertilizer suggestions, prevention guidance,
  and AI explanations
- Status: Not started

### 2. Production Software Architecture (Engineering Layer)

As of 2026-08-01, the project has moved from a notebook-centric research
workflow toward a production Python package. The active and target package
layout is:

```text
src/
`-- viriditas/
    |-- config/            Centralized configuration (settings, environment detection)
    |-- data/               Scanners, parsers, label normalization, dedup (implemented)
    |-- preprocessing/      Centralized image preprocessing (implemented)
    |-- training/           Training package (in progress; logic currently still in notebooks/02_train_plant_model.py)
    |-- inference/          Inference package (planned; not started)
    |-- evaluation/         Evaluation package (planned; currently notebooks/03_model_analysis.py)
    |-- models/             Model definitions / artifacts handling
    `-- utils/              Shared utilities
```

`src/agriai/` is a **historical package only**. It was the original pre-rename
codebase (see Design Decision, 2026-07-04) and was briefly and unintentionally
reintroduced as a tracked legacy package around 2026-07-19 (see CHANGELOG,
"Known Follow-Ups"). It is not part of the active architecture and is tracked
for removal/reconciliation in `TODO.md`.

## Engineering Principles

### Thin Notebook Philosophy

Notebooks are no longer the location of business logic. Business logic belongs
inside `src/viriditas/`. Notebooks are responsible only for:

- Loading configuration
- Calling reusable functions from `src/viriditas/`
- Orchestration (calling steps in the right order)
- Visualizing results

This keeps the codebase reusable by FastAPI, Flutter, CLI tools, unit tests, and
future LLM orchestration, instead of locking logic inside a Kaggle-only
notebook cell that nothing else can import.

### SDK Vision

VIRIDITAS's long-term architecture goal is to function as a reusable AI SDK.
The same core modules should be usable by:

- Kaggle notebooks (current primary training environment)
- A future FastAPI backend
- A future Flutter mobile application
- CLI utilities
- Future LLM orchestration

without rewriting preprocessing or inference logic per consumer. This is the
central reason configuration and preprocessing were centralized (see Design
Decisions below) before extracting the training, inference, and evaluation
packages.

## Current Repository State

The repository contains:

- `app.py`, `index.html`, `arduino_sensor_sender.ino`, `test.py`,
  `requirements.txt`, `images/` — the earlier Flask-based prototype. This
  prototype predates the current architecture and is not aligned with the
  production package direction; its hardware/sensor pieces (`arduino_sensor_sender.ino`)
  are explicitly archived, not part of V1 (see "Archived Ideas" below).
- `src/viriditas/config/` — centralized configuration (`settings.py`,
  `environment.py`), implemented.
- `src/viriditas/data/` — metadata-based dataset preprocessing package,
  implemented and validated (see Dataset Strategy below).
- `src/viriditas/preprocessing/` — centralized model-input preprocessing
  (image load, resize, normalize, EfficientNet-specific preprocessing),
  implemented, intended as the single implementation shared by training,
  evaluation, and future inference.
- `scripts/build_dataset_index.py` — dataset index builder CLI.
- `notebooks/01_dataset_index_builder.ipynb` / `.py` — dataset preprocessing,
  implemented and validated.
- `notebooks/02_train_plant_model.py` — plant identification training,
  implemented; business logic not yet extracted into `src/viriditas/training/`.
- `notebooks/03_model_analysis.py` — plant model evaluation, implemented with
  known issues (see TODO.md, Training section).
- `data/metadata/`, `models/` — generated-artifact directories, tracked via
  `.gitkeep` only; generated contents are gitignored (see Design Decision,
  2026-07-19 era cleanup).
- `tests/` — unit tests for preprocessing behavior.

## Dataset Strategy

The project uses metadata indexing instead of physically reorganizing images.

### Old Approach (rejected)

Images were copied into new folders such as:

```text
PlantID/
DiseaseID/
train/
validation/
test/
```

Problems: huge storage duplication, Kaggle disk space exhaustion, slow
preprocessing, and training layout tightly coupled to one folder structure.

### Current Approach

Keep original images in place and build CSV indexes:

```text
image_path, dataset_name, original_label, plant, disease, is_healthy, split
```

Metadata files produced by `notebooks/01_dataset_index_builder.py`:

- `master_dataset.csv` — one row per image
- `plant_id_dataset.csv` — plant classification view
- `disease_dataset.csv` — disease classification view
- `train.csv`, `val.csv`, `test.csv` — split metadata
- `label_map_plants.json`, `label_map_diseases.json` — class mappings
- `dataset_summary.json` — quick counts by dataset, plant, disease, and split
- `hash_cache.csv` — SHA-256 hash cache for duplicate detection and rebuild speed

### Current Kaggle Dataset Roots

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

### Dataset Format Detection

The index builder supports:

- Flat class folders
- Existing `train`, `valid`, `validation`, and `test` folders
- Nested plant and disease folders
- PlantVillage-style labels such as `Tomato___Early_blight`
- Dataset-specific label naming variations
- Flat split folders with no class subfolder, where the label is encoded in the
  filename (e.g. `test/angular_leafspot351.jpg`)
- Nested non-informative container folders (e.g.
  `Test Disease Severity Level/Level 1/`) that must be stripped before falling
  back to filename-based labels

### Canonical Metadata Schema

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

`duplicate_group_id` is the first 16 hex characters of each image's SHA-256
hash. Every row has one, whether or not it is part of a duplicate group, so
duplicate groups can be inspected directly from `master_dataset.csv`.

## Model Architecture Direction

- Use transfer learning for both models.
- Plant identification baseline: EfficientNetV2B0, ImageNet pretrained, two-phase
  training (frozen base, then fine-tune with a lower learning rate).
- Keep the plant model and disease model separate at first for cleaner
  debugging.
- Later evaluate a multi-task model only after both individual models are
  stable.
- Model architecture choices should favor formats convertible to TensorFlow
  Lite or ONNX to support the planned offline / on-device inference roadmap
  item.

## Design Decisions

### Decision: Use metadata instead of copying images
Date: 2026-07-04

Reason: avoids storage duplication; works better on Kaggle disk limits; allows
new datasets to be added without rewriting training code; keeps preprocessing
independent from training.

### Decision: Split notebooks by pipeline stage
Date: 2026-07-04

Notebook plan: `01_dataset_index_builder`, `02_train_plant_model`,
`03_train_disease_model`, `04_inference`.

Reason: keeps preprocessing, training, and inference independent; makes
notebooks easier to rerun and debug; supports future refactoring into scripts
and packages.

### Decision: Use two models first
Date: 2026-07-04

Reason: clearer separation between plant identification and disease
classification; easier to debug dataset labeling errors; easier to expand
plant coverage before disease coverage; future multi-task or hierarchical
models remain possible.

### Decision: Normalize dataset container and augmentation labels
Date: 2026-07-10

Reason: Kaggle metadata validation showed plant labels such as `Data`,
`Original Dataset`, `Pea Plant Dataset`, and `Test Disease Severity Level`, and
augmented datasets created separate labels such as
`Peach Bacterial Spot Brightness Adjusted`, which would incorrectly increase
the number of plant and disease classes.

Action: use dataset-name plant hints when folder labels are generic
containers; strip augmentation operation suffixes from disease labels; remove
repeated plant names from disease labels when they appear as suffixes.

### Decision: Add filename-based label fallback and non-informative folder stripping
Date: 2026-07-11

Reason: the 2026-07-10 fix resolved bad plant labels, but had not actually been
pushed to GitHub `main` (local/remote branches had diverged) until this was
caught and corrected. After confirming the push, 2,507 `Unknown` disease rows
remained, almost entirely (2,500 of 2,507) from
`strawberry-disease-detection-dataset`, which uses two folder layouts the
parser didn't handle: a flat `test/` split folder with no class subfolder
(label encoded in the filename, e.g. `angular_leafspot351.jpg`), and a nested
`Test Disease Severity Level/Level 1/` container that was being misparsed into
fake "Level 1"/"Level 2" disease classes.

Action: added a filename-based label extraction fallback in
`layout_detection.py`; added stripping of non-informative folder names so the
parser falls through to the filename fallback; added one disease alias
(`angular leafspot` -> `Angular Leaf Spot`).

### Decision: Wire duplicate detection into the pipeline and resolve cross-split leakage
Date: 2026-07-11

Reason: `duplicates.py` had SHA-256 hashing logic and unit tests, but was never
actually called from `index_builder.py`; `duplicate_group_id` existed in the
planned schema but was never populated. A manual review found 7,571 duplicate
groups (15,209 images), of which 3,057 groups (6,176 images) spanned more than
one split — a real train/test leakage risk that would inflate evaluation
metrics.

Action: added `deduplicate_records()` to `duplicates.py`, tagging every image
with a `duplicate_group_id` and resolving any group spanning multiple splits
by keeping one copy (preferring `train`); added a hash cache for rebuild
speed; wired the new function into `01_dataset_index_builder.py` immediately
after `assign_splits()` and before any CSV is written; fixed `splits.py`'s
`_replace_split` to use `dataclasses.replace` so it can't silently drop future
schema fields.

Result: dataset size went from 201,094 to 197,975 images (3,119 rows dropped),
with 0 cross-split leakage confirmed via a fresh pipeline rebuild.

### Decision: Stop tracking generated artifacts in git
Date: 2026-07-19

Reason: generated metadata, model files, analysis outputs, caches, logs, and
temporary files do not belong in version control; they bloat the repository
and can silently go stale relative to the code that produced them.

Action: removed tracked generated training/metadata artifacts from the
repository; kept only `.gitkeep` placeholders for the required directory
structure (`data/metadata/`, `models/`, `src/viriditas/data/metadata/`);
refined `.gitignore` accordingly. Local generated model files still exist
under `models/.v01/` but are intentionally gitignored.

### Decision: Transition from notebook-centric development to a production Python package
Date: 2026-08-01

Reason: the original implementation successfully proved the dataset pipeline
and training workflow using Kaggle notebooks. As the project matured, business
logic became spread across notebooks, making testing, reuse, API integration,
and long-term maintenance increasingly difficult.

Action: move reusable logic into `src/viriditas/`; keep notebooks as thin
wrappers responsible only for orchestration; treat `src/viriditas/` as the
production codebase.

Outcome: the repository now follows a production-oriented architecture rather
than a research-only notebook workflow.

### Decision: Centralize configuration
Date: 2026-08-01

Reason: configuration values such as image size, batch size, dataset paths,
training parameters, and output directories were duplicated across multiple
notebooks, creating maintenance problems and making environment portability
difficult.

Action: introduced `src/viriditas/config/` including `settings.py`,
`environment.py`, and `__init__.py`. Configuration is now accessed through
`paths`, `image_config`, `training_config`, and `dataset_config` objects,
replacing direct constants (`IMAGE_SIZE`, `BATCH_SIZE`, `MODEL_DIR`,
`OUTPUT_DIR`, `METADATA_DIR`) with `image_config.SIZE`,
`image_config.BATCH_SIZE`, `paths.models_dir`, `paths.metadata_dir`,
`paths.resolve_model_path()`, etc.

Benefits: single source of truth; Kaggle, local, and Google Colab
compatibility; easier testing.

### Decision: Automatic environment detection
Date: 2026-08-01

Reason: the project should run without manually modifying paths for each
environment.

Action: implemented environment detection in `src/viriditas/config/environment.py`
supporting Local, Kaggle, and Google Colab. The detected environment now
determines metadata paths, model paths, and output directories instead of
hardcoded per-notebook paths.

### Decision: Centralize model-input preprocessing
Date: 2026-08-01

Reason: training, evaluation, future inference, the future FastAPI backend,
and the future Flutter client must all preprocess images identically (image
loading, resizing, normalization, EfficientNet-specific preprocessing).
Previously this logic was duplicated per notebook, risking preprocessing drift
between training and inference.

Action: created a single preprocessing implementation inside
`src/viriditas/preprocessing/`, shared by every current and future consumer.

Benefits: eliminates preprocessing drift; guarantees consistent inference;
easier maintenance; a single place for future preprocessing improvements.

### Decision: Adopt the "thin notebook" engineering principle
Date: 2026-08-01

Reason: business logic embedded in notebooks cannot be reused by FastAPI,
Flutter, CLI tools, or unit tests, and is harder to test in isolation.

Action: business logic now belongs in `src/viriditas/`; notebooks are limited
to loading configuration, calling reusable functions, and visualizing results.

### Decision: Version 1 scope is software-only; archive hardware/IoT integrations
Date: 2026-08-01

Reason: the original prototype included ESP32 sensor integration and an
Arduino sensor sender sketch. To ship a focused V1 (plant identification,
disease detection, recommendation engine, FastAPI, Flutter), hardware and IoT
work needs to be explicitly out of scope rather than an ambient, unscoped
possibility.

Action: reclassified Arduino, ESP32, IoT sensors, weather stations, and other
embedded/hardware integrations as "Archived Ideas / Future Possibilities,"
separate from the active V1 roadmap. `arduino_sensor_sender.ino` remains in
the repository as a historical artifact from the original prototype only.

## Current Progress

Completed:

- Identified storage problem caused by image copying; chose metadata-first
  dataset strategy.
- Chose staged notebooks for preprocessing, training, and inference.
- Established project documentation rules; created source-of-truth
  documentation.
- Implemented `src/viriditas/data/` preprocessing package and Kaggle/local
  dataset index builder entrypoints.
- Added tests for label parsing, layout detection, split generation, and
  duplicate detection.
- Validated Kaggle metadata output for 201,094 scanned images.
- Fixed generic dataset-container plant labels, augmented-class disease
  labels, filename-encoded labels, and non-informative nested folders. Unknown
  disease rows reduced from 2,507 to 7 (a genuine source-data gap).
- Wired duplicate detection into the indexing pipeline; resolved cross-split
  leakage from 6,176 affected images down to zero, verified on a clean
  rebuild; added a persisted hash cache.
- Trained a baseline plant identification model (EfficientNetV2B0 transfer
  learning): 80.98% test accuracy, with a validation-test accuracy gap of
  approximately 1 percentage point after adding data augmentation, batch
  normalization, and early stopping.
- Built `notebooks/03_model_analysis.py` for plant-model evaluation (known
  cleanup issues remain; see TODO.md).
- Stopped tracking generated artifacts in git; added `.gitkeep` placeholders.
- Centralized configuration (`src/viriditas/config/`: `settings.py`,
  `environment.py`) with automatic Local / Kaggle / Colab environment
  detection.
- Centralized model-input preprocessing into a single shared implementation.
- Began production package restructuring under `src/viriditas/`.
- Ran architectural smoke tests after the configuration/preprocessing
  refactor (import, configuration, and preprocessing validation passed;
  two environment-specific issues found and confirmed non-architectural).

In progress:

- Extracting training logic out of `notebooks/02_train_plant_model.py` into
  `src/viriditas/training/`.
- Building `src/viriditas/inference/`.
- Building `src/viriditas/evaluation/` (migrating `03_model_analysis.py`
  logic once its known issues are fixed).
- Converting remaining notebooks into thin wrappers.

Not started:

- Disease classification model training.
- Combined plant + disease inference pipeline.
- AI recommendation engine.
- FastAPI backend.
- Flutter mobile client.
- LLM orchestration layer.

## Current Task

1. Remove or reconcile the reintroduced legacy `src/agriai/` package so that
   `src/viriditas/` remains the only tracked, active package namespace.
2. Fix known issues in `notebooks/03_model_analysis.py` (local metadata path,
   undefined misclassified-sample count, dataset-accuracy plot axis) before
   treating its output as reliable.
3. Decide handling for the 7 remaining unlabeled apple images.
4. Continue extracting `src/viriditas/training/`, `src/viriditas/inference/`,
   and `src/viriditas/evaluation/` out of the current notebook scripts.
5. Implement lazy model loading ahead of FastAPI integration.

## Implemented Dataset Index Builder Architecture

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

## Trade-Offs

### Notebook-only implementation
Pros: fast to prototype; easy to inspect in Kaggle.
Cons: harder to test; harder to reuse; more likely to become messy as the
project grows — this is exactly the pressure that motivated the 2026-08-01
production package refactor.

### Script/package implementation with notebook wrapper
Pros: testable; reusable; cleaner training notebooks; easier to maintain as
VIRIDITAS grows and gains new consumers (FastAPI, Flutter, CLI).
Cons: slightly more setup upfront.

Decision: use a small Python package under `src/viriditas/` and keep notebooks
thin. Implemented for the data pipeline; in progress for training, inference,
and evaluation.

## Next Tasks

1. Reconcile / remove the legacy `src/agriai/` package.
2. Fix and rerun `notebooks/03_model_analysis.py`; save summary metrics.
3. Decide on the 7 unlabeled apple images.
4. Extract `src/viriditas/training/`.
5. Extract `src/viriditas/inference/` with lazy model loading.
6. Extract `src/viriditas/evaluation/`.
7. Create `03_train_disease_model.ipynb` and train the disease classification
   model.
8. Begin FastAPI backend design around the (eventual) inference package.
9. Begin Flutter client planning.

## Future Roadmap

Phase 1 — Configuration: done
Phase 2 — Centralized Preprocessing: done
Phase 3 — Training Package: in progress
Phase 4 — Inference Package: not started
Phase 5 — Evaluation Package: not started
Phase 6 — Notebook Cleanup (thin wrappers): in progress
Phase 7 — FastAPI Backend: not started
Phase 8 — Flutter Client: not started
Phase 9 — Recommendation Engine: not started
Phase 10 — LLM Integration: not started

Also planned, not yet phased: explainable AI visualizations; dataset update
workflow; cloud synchronization; voice interaction.

## Archived Ideas / Future Possibilities (Not Version 1)

These were part of the earlier Flask/ESP32 prototype's ambitions or were
previously listed as roadmap items. They are retained here for historical
context and possible future exploration, but are explicitly **not** part of
Version 1 and should not be treated as active architecture:

- Arduino / ESP32 sensor integration (`arduino_sensor_sender.ino` remains in
  the repository as a historical artifact of the original prototype only)
- Physical weather stations / weather-aware recommendations
- Other embedded or IoT hardware integrations
- Sensor-aware irrigation recommendations