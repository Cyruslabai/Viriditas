# VIRIDITAS

VIRIDITAS is an AI platform for plant identification, disease detection, and agricultural recommendations. The repository provides modular components for dataset indexing, preprocessing, model training, inference, and evaluation.

Features
- Metadata-first dataset indexing (no image duplication)
- Centralized preprocessing compatible with EfficientNetV2
- Modular training pipeline using transfer learning (EfficientNetV2B0)
- Reusable inference API with cached model loading
- Kaggle artifact-aware metadata, label-map, and model loading
- Reusable evaluation package for reports and visualizations
- Automated tests and example notebooks for development

Quickstart
1. Install dependencies:
   pip install -r requirements.txt

2. Add dataset metadata (or use provided sample fixtures):
   Place `plant_id_dataset.csv` under `data/metadata/` and images at paths referenced by the CSV.
   On Kaggle, attach the generated `viriditas-artifacts` dataset so training can read metadata and label maps from `/kaggle/input`.

3. Training (notebook or CLI):
   - Notebook entrypoint: `notebooks/02_train_plant_model.py` (thin wrapper calling the trainer)
   - The trainer reads `plant_id_dataset.csv` and `label_map_plants.json` from the attached artifact dataset when available.
   - Programmatic usage:
     from viriditas.training import PlantIdentifierTrainer
     trainer = PlantIdentifierTrainer()
     trainer.run()

4. Inference:
   - Use the reusable predictor:
     from viriditas.inference import PlantPredictor
     p = PlantPredictor()
     p.predict(path)
   - Inference lazily loads the official versioned model (e.g., `viriditas_best_v02.keras`)
     and `label_map_plants.json` from Kaggle artifacts or local `models/` / `data/metadata/` paths.
   - The model filename is automatically resolved from the centralized MODEL_VERSION configuration.

5. Evaluation:
   - Use the evaluator to run analysis and save reports:
     from viriditas.evaluation import Evaluator
     ev = Evaluator()
     ev.run()

Running tests
- Tests live under `tests/`. Run with:
  pytest -q

Project layout
- src/viriditas/: core package
  - config/: environment-aware configuration and constants
  - preprocessing.py: centralized ImagePreprocessor
  - training/: dataset, model, callbacks, trainer
  - inference/: loader, predictor, preprocessing adapter, postprocessing
  - evaluation/: evaluator, metrics, reports, visualizations
- notebooks/: thin wrappers for training and analysis
- tests/: automated unit and integration tests

Roadmap
- Consolidate disease and plant inference APIs
- Add CI with unit+integration tests
- Production FastAPI backend and Docker deployment

For architecture details, developer setup, and testing guidance see `ARCHITECTURE.md`, `DEVELOPMENT.md`, and `TESTING.md`.


VIRIDITAS is an AI software platform focused on plant identification, disease detection, and AI-powered recommendations. The project provides robust data engineering, training, evaluation, and an extensible recommendation engine for agricultural guidance.

The current engineering milestone is stabilizing the first plant identification baseline after completing the metadata-driven dataset pipeline. Instead of copying images into new folders, VIRIDITAS indexes existing Kaggle datasets in place and creates standardized CSV metadata for training plant identification and disease classification models.

## Current Status

This repository contains an earlier Flask prototype for plant disease prediction and the newer VIRIDITAS data and training pipeline. The project is being refactored into separate dataset indexing, model training, analysis, inference, and recommendation components. The hardware- and sensor-focused experiments have been archived and are out-of-scope for Version 1.

Latest checkpoint:

- Preprocessing is validated at `197,975` images after duplicate-leakage resolution.
- Bad generic plant labels are resolved; only 7 genuinely unlabeled apple images remain.
- The plant identification trainer exists at `notebooks/02_train_plant_model.py`.
- Training now prefers attached Kaggle artifact metadata and the saved plant label map, keeping class indices aligned across preprocessing, training, and inference.
- Inference uses lazy cached loading for the plant model and plant label map.
- Local plant model artifacts exist under `models/.v01/`, but generated artifacts are ignored by git.
- The analysis runner exists at `notebooks/03_model_analysis.py` and needs a small cleanup pass before its outputs are treated as reliable.

## Target Features

- Plant identification from leaf images
- Plant-specific disease diagnosis
- Metadata-based multi-dataset indexing
- Standardized plant and disease labels across Kaggle datasets
- Train, validation, and test split generation without image duplication
- Local inference on consumer devices
- AI-generated treatment recommendations
- Fertilizer and prevention guidance
- Offline assistant and future voice interaction
- LLM-powered explanations and agricultural guidance
- FastAPI backend and Flutter mobile client (planned)

## Target Architecture

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
Treatment | Fertilizer | Prevention | Farming Guidance
```

## Dataset Strategy

VIRIDITAS uses a metadata-first data engineering approach:

- Keep original Kaggle images in place.
- Scan dataset folders automatically.
- Detect dataset layout types, including flat class folders and train/valid/test folders.
- Extract plant names and disease names from class folder names.
- Normalize inconsistent labels into canonical labels.
- Build a master dataset CSV containing image paths and labels.
- Generate train, validation, and test splits as metadata, not copied image folders.

This avoids duplicate image storage and makes it possible to add new datasets without rewriting training code.

## Planned Repository Structure

```text
VIRIDITAS/
|-- app.py                         Existing Flask prototype
|-- index.html                     Existing web dashboard prototype
|-- arduino_sensor_sender.ino      (archived hardware experiment)
|-- requirements.txt               Python dependencies
|-- data/
|   |-- raw/                       External datasets, usually not committed
|   |-- metadata/                  Generated CSV indexes and split files
|-- notebooks/
|   |-- 01_dataset_index_builder.ipynb
|   |-- 01_dataset_index_builder.py
|   |-- 02_train_plant_model.ipynb
|   |-- 02_train_plant_model.py
|   |-- 03_model_analysis.ipynb
|   |-- 03_model_analysis.py
|   |-- 03_train_disease_model.ipynb
|   |-- 04_inference.ipynb
|-- scripts/
|   |-- build_dataset_index.py       Local/Kaggle metadata builder CLI
|-- src/
|   |-- viriditas/
|       |-- data/                  Dataset scanning, parsing, indexing
|       |-- models/                Model definitions and training helpers
|       |-- inference/             Local inference pipeline
|       |-- recommendations/       Treatment and guidance engine
|-- tests/                         Automated tests for preprocessing
|-- models/                        Generated model artifacts; ignored except .gitkeep
|-- docs/
|   |-- README.md                  Project overview
|   |-- PROJECT_PLAN.md            Single source of truth
|   |-- CHANGELOG.md               Chronological project history
|   |-- TODO.md                    Engineering task list
|   |-- JOURNAL.md                 Chronological engineering journal
|   |-- KAGGLE_RUNBOOK.md          Kaggle restart and rerun guide
|   |-- MODELS.md                  Model artifact notes
|   |-- METADATA.md                Metadata artifact notes
```

## Dataset Preprocessing

The dataset index builder is implemented under `src/viriditas/data/`. It scans existing dataset folders and writes metadata files without copying images.

Kaggle notebook entrypoint:

```text
notebooks/01_dataset_index_builder.ipynb
```

Script entrypoint:

```bash
python scripts/build_dataset_index.py \
  --dataset-root /kaggle/input/datasets/rizwan123456789/potato-disease-leaf-datasetpld \
  --output-dir /kaggle/working/data/metadata
```

Pass `--dataset-root` multiple times to combine datasets.

Generated files:

```text
master_dataset.csv
plant_id_dataset.csv
disease_dataset.csv
train.csv
val.csv
test.csv
label_map_plants.json
label_map_diseases.json
dataset_summary.json
```

When running on Kaggle after metadata has already been generated, attach the exported `viriditas-artifacts` dataset. The configuration layer can resolve `plant_id_dataset.csv`, `label_map_plants.json`, and related metadata from that read-only artifact while still writing new model outputs under `/kaggle/working/models`.

Run preprocessing tests locally:

```bash
python -m unittest discover -s tests
```

## Project Memory

- `PROJECT_PLAN.md`: source of truth for architecture, decisions, current task, and roadmap.
- `JOURNAL.md`: chronological record of progress, Kaggle findings, blockers, and resume state.
- `KAGGLE_RUNBOOK.md`: exact Kaggle cells for downloading the repo, rerunning preprocessing, and validating metadata.
- `CHANGELOG.md`: chronological list of major repository changes.
- `TODO.md`: active engineering checklist.

## Next Milestone

Fix and run `notebooks/03_model_analysis.py`, recover or rerun the plant training history, and record the baseline plant identification metrics before starting the disease classification model.

For the detailed engineering plan, see `PROJECT_PLAN.md`.

## Existing Prototype

The original prototype documentation is preserved below.

# Plant Disease Identifier with Sensor-Based Irrigation Monitoring

This repository contains a legacy prototype (archived) that demonstrated leaf-image disease prediction and a simple dashboard. Hardware- and sensor-related features from the prototype are archived and are not part of the Version 1 product.

## Overview

The prototype demonstrated a deep learning image classification pipeline for leaf images and a simple dashboard. Hardware and sensor-related functionality is archived; the core product focus is on model-driven inference and recommendation.

## Key Features

- Leaf image-based plant disease detection
- Top prediction with confidence score and top 3 probable classes
- Soil moisture monitoring
- Temperature and humidity monitoring using DHT11
- Automatic irrigation recommendation based on sensor values
- Web dashboard with automatic sensor data refresh
- Sensor integration over Wi-Fi using ESP32-CAM

## Tech Stack

### Backend

- Python
- FastAPI (target for production service)
- TensorFlow / Keras
- NumPy
- Pillow
- Docker (deployment)

### Frontend

- HTML
- CSS
- JavaScript

### Hardware

- ESP32-CAM
- Soil moisture sensor
- DHT11 temperature and humidity sensor

## How the System Works

### Disease Detection Flow

1. The user uploads a leaf image through the web interface.
2. The service backend (FastAPI in the target architecture) preprocesses the image to `224 x 224`.
3. The trained TensorFlow model predicts the disease class.
4. The application returns the plant name, predicted disease, confidence score, and top 3 predictions.

### Sensor Monitoring Flow

1. The soil moisture sensor and DHT11 are connected to the ESP32-CAM.
2. The ESP32-CAM reads soil moisture, temperature, and humidity values.
3. The board sends the readings to the Flask backend using a `POST /sensor-data` request over Wi-Fi.
4. The web application fetches the latest sensor data automatically and updates the dashboard.
5. The backend evaluates the readings and returns irrigation advice such as:
   - `Irrigate now`
   - `Irrigate soon`
   - `Hold irrigation`
   - `Stop irrigation`

## Model Information

- Model type: CNN-based plant disease classifier
- Input size: `224 x 224`
- Total classes: `38`
- Plants covered: `14`

The disease classes currently configured in the application include crops such as apple, blueberry, cherry, corn, grape, orange, peach, bell pepper, potato, raspberry, soybean, squash, strawberry, and tomato.

## Project Structure

```text
Plant-disease-identifier/
|-- app.py                        Flask backend and prediction API
|-- index.html                    Frontend dashboard
|-- arduino_sensor_sender.ino     (archived hardware experiment)
|-- test.py                       Local image testing script
|-- requirements.txt              Python dependencies
|-- images/                       Training graph images
|-- docs/README.md                Project documentation
```

## Setup Instructions

### 1. Clone the repository

```bash
git clone https://github.com/Pushpak-Cyrus/Plant-disease-identifier.git
cd Plant-disease-identifier
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Add the trained model file

Place the trained model file below in the project root:

```text
plant_disease_model_finetuned.h5
```

The application will not start correctly unless this file is present.

### 4. Running the prototype service (legacy)

The repository contains a legacy Flask prototype (`app.py`) used during early exploration. It is retained for historical reference. The target production service will be implemented with FastAPI.

To run the prototype locally (not required for V1 work):

```bash
python app.py
# then open http://localhost:5000 in your browser
```


## Archived hardware experiments

Legacy hardware and sensor experiments (ESP32 sketches, Arduino prototypes, and simple dashboard integrations) are preserved in the repository for historical reference only. These experiments are intentionally archived and are out-of-scope for the Version 1 software platform. See `JOURNAL.md` for notes and rationale.
## API Endpoints

### `POST /predict`

Accepts a leaf image file and returns:

- plant name
- disease name
- confidence score
- healthy/diseased status
- top 3 predictions

### Legacy sensor endpoints (archived)

The repository previously exposed simple sensor endpoints for prototype experiments. These endpoints are part of archived hardware work and are not part of the Version 1 product. See `JOURNAL.md` for details.
## Training Graphs

Training graphs used in the project are stored in the `images/` folder.

<p align="center">
  <img src="images/acc%20impv.png" width="45%" alt="Model accuracy graph" />
  <img src="images/losss%20impv.png" width="45%" alt="Model loss graph" />
</p>

## Educational Value

This project demonstrates how artificial intelligence can be applied to plant identification and disease detection. It covers:

- image preprocessing for deep learning
- model inference with TensorFlow
- Flask API development
- frontend and backend integration
- sensor-based data collection
- simple rule-based irrigation support

## Disclaimer

This project was built for learning and demonstration purposes. The predictions and irrigation advice should not be treated as a replacement for professional agricultural guidance.

## License

Copyright (c) 2025 Pushpak-Cyrus.
All rights reserved.
