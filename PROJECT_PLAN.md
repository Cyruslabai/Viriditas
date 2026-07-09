# VIRIDITAS Project Plan

Last updated: 2026-07-04

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
- `notebooks/01_dataset_index_builder.ipynb`: Kaggle preprocessing notebook
- `tests/`: Unit tests for preprocessing behavior

The Flask prototype is useful but does not yet match the planned scalable VIRIDITAS inference architecture. The preprocessing layer is now the first implemented part of the new VIRIDITAS architecture.

## Planned Folder Structure

```text
VIRIDITAS/
|-- data/
|   |-- raw/                       External datasets, usually ignored by git
|   |-- metadata/                  Generated dataset indexes and split CSVs
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
|       |-- data/                  Scanners, parsers, label normalization
|       |-- models/                Training and model utilities
|       |-- inference/             End-to-end prediction pipeline
|       |-- recommendations/       Treatment and guidance generation
|-- tests/                         Unit and integration tests
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

## Canonical Metadata Schema

Initial recommended schema:

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

In progress:

- Rerun Kaggle preprocessing after parser fixes and inspect generated metadata

Not started:

- Plant identification model training
- Disease classification model training
- Recommendation engine

## Current Task

Run `notebooks/01_dataset_index_builder.ipynb` in Kaggle using the configured dataset roots, then validate `dataset_summary.json`, `master_dataset.csv`, and label maps before training.

## Implemented Dataset Index Builder Architecture

Recommended modules:

```text
src/viriditas/data/
|-- __init__.py
|-- config.py              Dataset paths and supported image extensions
|-- schemas.py             Metadata dataclasses or typed dictionaries
|-- scanners.py            Recursive image discovery
|-- layout_detection.py    Detect class-folder and split-folder layouts
|-- label_parser.py        Extract plant and disease labels
|-- normalizer.py          Canonical label normalization
|-- index_builder.py       Build master dataframe
|-- splits.py              Train/validation/test split generation
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

1. Rerun the dataset index builder in Kaggle with the latest parser fixes.
2. Inspect `dataset_summary.json` for unexpected plants, diseases, or split imbalance.
3. Review `master_dataset.csv` samples for each dataset.
4. Confirm no incorrect plant classes such as `Data`, `Original Dataset`, or `Test Disease Severity Level` remain.
5. Review exact duplicate groups if repeated images are visible across datasets.
6. Create `02_train_plant_model.ipynb`.
7. Train baseline plant identification model.
8. Create `03_train_disease_model.ipynb`.
9. Train baseline disease classification model.

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
