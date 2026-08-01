# TODO.md

# VIRIDITAS TODO

Last updated: 2026-08-01

## Documentation

- [x] Create `PROJECT_PLAN.md`
- [x] Update `README.md`
- [x] Create `CHANGELOG.md`
- [x] Create `TODO.md`
- [x] Create `docs/JOURNAL.md`
- [x] Create `docs/KAGGLE_RUNBOOK.md`
- [x] Keep documentation updated after every major architecture or implementation change
- [x] Document the production package refactor across PROJECT_PLAN, TODO, CHANGELOG, JOURNAL

## Architecture Refactor

- [x] Remove duplicated `agriai` package as the active namespace (`src/viriditas/` is authoritative)
- [x] Centralize configuration (`src/viriditas/config/`: `settings.py`, `environment.py`)
- [x] Add automatic environment detection (Local / Kaggle / Google Colab)
- [x] Centralize model-input preprocessing (image load, resize, normalize, EfficientNet preprocessing) into a single shared implementation
- [ ] Extract training package (`src/viriditas/training/`)
- [ ] Extract inference package (`src/viriditas/inference/`)
- [ ] Extract evaluation package (`src/viriditas/evaluation/`)
- [ ] Convert remaining notebooks into thin wrappers (orchestration only, no business logic)
- [ ] Introduce lazy model loading in the inference package (avoid loading TensorFlow models at import time)
- [ ] Remove or reconcile the reintroduced legacy `src/agriai/` package so `src/viriditas/` remains the only tracked, active package namespace
- [ ] Build FastAPI service
- [ ] Build Flutter client
- [ ] Integrate recommendation engine
- [ ] Integrate LLM orchestration

## Dataset Pipeline

- [x] Decide to use metadata indexing instead of copying images
- [x] Define staged notebook workflow
- [x] Approve dataset index builder architecture
- [x] Create `src/viriditas/data/` package
- [x] Define canonical metadata schema in code
- [x] Implement recursive image scanning
- [x] Detect flat class-folder datasets
- [x] Detect `train` / `valid` / `validation` / `test` datasets
- [x] Detect nested plant/disease folder layouts
- [x] Parse PlantVillage-style labels
- [x] Normalize plant names
- [x] Normalize disease names
- [x] Build `master_dataset.csv`
- [x] Build `plant_id_dataset.csv`
- [x] Build `disease_dataset.csv`
- [x] Generate train/validation/test split CSV files
- [x] Add duplicate image detection
- [x] Add dataset summary reports
- [x] Add Kaggle dataset index builder notebook
- [x] Add local/Kaggle dataset index builder script
- [x] Run Kaggle preprocessing on the selected 13 datasets
- [x] Inspect generated `dataset_summary.json`
- [x] Review sample rows from `master_dataset.csv`
- [x] Fix generic container folder labels after Kaggle validation
- [x] Collapse augmented disease labels into base disease classes
- [x] Rerun Kaggle preprocessing after parser fixes
- [x] Confirm bad plant labels are zero after rerun
- [x] Review remaining unknown disease rows after rerun
- [x] Add filename-based label fallback for datasets with no class folders
- [x] Strip non-informative nested folders (severity-level subfolders) before parsing
- [x] Fix stray `agriai` import in `scanners.py`
- [x] Review duplicate groups for train/test leakage risk
- [x] Wire duplicate detection into `index_builder.py` pipeline (previously standalone/unused)
- [x] Populate `duplicate_group_id` in `master_dataset.csv` for real
- [x] Resolve cross-split duplicate leakage (6,176 images / 3,057 groups -> 0)
- [x] Add hash cache to speed up repeat dedup runs
- [x] Stop tracking generated metadata/hash-cache artifacts in git; keep metadata folders via `.gitkeep`
- [x] Fix `_replace_split` in `splits.py` to use `dataclasses.replace` (avoid silently dropping future fields)
- [x] Add progress logging to the dataset index builder runner
- [ ] Decide handling for the 7 remaining unlabeled apple images (drop vs. keep as tiny Unknown class)
- [ ] Decide whether the dedup hash cache needs a non-git persistence path, such as a Kaggle Dataset artifact, if rebuild speed becomes painful again

## Configuration

- [x] Design centralized configuration objects (`paths`, `image_config`, `training_config`, `dataset_config`)
- [x] Implement `src/viriditas/config/settings.py`
- [x] Implement `src/viriditas/config/environment.py` (Local / Kaggle / Colab detection)
- [x] Migrate away from direct constants (`IMAGE_SIZE`, `BATCH_SIZE`, `MODEL_DIR`, `OUTPUT_DIR`, `METADATA_DIR`)
- [ ] Migrate all remaining notebooks/scripts fully onto the config objects (audit for leftover hardcoded constants)
- [ ] Add unit tests for environment detection across all three supported environments

## Testing

- [x] Add tests for label parsing
- [x] Add tests for layout detection
- [x] Add tests for split generation
- [x] Add tests for duplicate detection
- [x] Add tests for generic folder and augmentation label parsing
- [x] Run architectural smoke tests (import validation, configuration validation, preprocessing validation)
- [ ] Add tests for filename-based label fallback
- [ ] Add tests for non-informative folder stripping (severity-level subfolders)
- [ ] Add tests for `deduplicate_records()` and cross-split resolution
- [ ] Add tests for the hash cache (cache hit/miss behavior)
- [ ] Add tests for metadata schema validation
- [ ] Add a smoke/static check for `notebooks/03_model_analysis.py`
- [ ] Add unit tests for the centralized preprocessing module

## Training

- [x] Create `notebooks/02_train_plant_model.py`
- [ ] Populate or remove the empty `notebooks/02_train_plant_model.ipynb` placeholder
- [x] Train and save local plant identification baseline artifacts
- [x] Add EfficientNetV2B0 transfer-learning baseline
- [x] Add data augmentation, class weights, checkpointing, and early stopping
- [x] Remove `tf.data` caching from training to reduce memory pressure
- [x] Save the plant label map used by training
- [ ] Recover or rerun the plant training history and record baseline metrics in docs
- [x] Create `notebooks/03_model_analysis.py`
- [ ] Fix analysis script issues before relying on it: local metadata path, undefined misclassified-sample count, and dataset-accuracy plot axis
- [ ] Run plant model analysis and save summary metrics
- [ ] Begin extracting training logic out of `notebooks/02_train_plant_model.py` into `src/viriditas/training/`
- [ ] Create `03_train_disease_model.ipynb`
- [ ] Train baseline disease classification model
- [ ] Save disease label maps with trained models
- [ ] Track metrics and confusion matrices
- [ ] Remove or reconcile the reintroduced legacy `src/agriai/` package so `src/viriditas/` remains the only active package namespace *(duplicated here intentionally — tracked under both Architecture Refactor and Training since it currently blocks a clean training-package extraction)*

## Inference

- [ ] Create `src/viriditas/inference/` package
- [ ] Implement lazy model loading (do not load TensorFlow models at import time)
- [ ] Build plant identification inference step
- [ ] Build disease classification inference step
- [ ] Combine both models into one inference pipeline
- [ ] Return confidence scores and top predictions
- [ ] Create `04_inference.ipynb` as a thin wrapper over `src/viriditas/inference/`

## Evaluation

- [ ] Create `src/viriditas/evaluation/` package
- [ ] Migrate `03_model_analysis.py` logic into the evaluation package once its known issues are fixed
- [ ] Standardize evaluation outputs (confusion matrix, classification report, per-class accuracy) for both plant and disease models

## Recommendation Engine

- [ ] Define treatment recommendation schema
- [ ] Add rule-based recommendations for baseline diseases
- [ ] Add fertilizer guidance
- [ ] Add prevention guidance
- [ ] Add AI-generated explanations

## Application (Version 1 — Software)

- [ ] Build FastAPI backend service around the inference pipeline
- [ ] Build a cross-platform mobile application (Flutter)
- [ ] Plan mobile application architecture and offline model packaging
- [ ] Add offline model packaging

## Future Expansion

- [ ] Local LLM integration / LLM orchestration layer
- [ ] Voice interaction
- [ ] Cloud synchronization
- [ ] Explainable AI visualizations
- [ ] Dataset update workflow

## Archived Ideas / Future Possibilities (Not Version 1)

- [ ] Weather-aware recommendations *(archived for V1; revisit once the recommendation engine exists)*
- [ ] Arduino / ESP32 sensor integration
- [ ] Physical weather stations
- [ ] Other embedded / IoT hardware integrations