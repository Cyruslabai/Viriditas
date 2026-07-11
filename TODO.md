# VIRIDITAS TODO

Last updated: 2026-07-11

## Documentation

- [x] Create `PROJECT_PLAN.md`
- [x] Update `README.md`
- [x] Create `CHANGELOG.md`
- [x] Create `TODO.md`
- [x] Create `docs/JOURNAL.md`
- [x] Create `docs/KAGGLE_RUNBOOK.md`
- [x] Keep documentation updated after every major architecture or implementation change

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
- [x] Commit hash cache to GitHub with a `.gitignore` exception
- [x] Fix `_replace_split` in `splits.py` to use `dataclasses.replace` (avoid silently dropping future fields)
- [ ] Decide handling for the 7 remaining unlabeled apple images (drop vs. keep as tiny Unknown class)

## Testing

- [x] Add tests for label parsing
- [x] Add tests for layout detection
- [x] Add tests for split generation
- [x] Add tests for duplicate detection
- [x] Add tests for generic folder and augmentation label parsing
- [ ] Add tests for filename-based label fallback
- [ ] Add tests for non-informative folder stripping (severity-level subfolders)
- [ ] Add tests for `deduplicate_records()` and cross-split resolution
- [ ] Add tests for the hash cache (cache hit/miss behavior)
- [ ] Add tests for metadata schema validation

## Training

- [ ] Create `02_train_plant_model.ipynb`
- [ ] Train baseline plant identification model
- [ ] Create `03_train_disease_model.ipynb`
- [ ] Train baseline disease classification model
- [ ] Save label maps with trained models
- [ ] Track metrics and confusion matrices

## Inference

- [ ] Create `04_inference.ipynb`
- [ ] Build plant identification inference step
- [ ] Build disease classification inference step
- [ ] Combine both models into one inference pipeline
- [ ] Return confidence scores and top predictions

## Recommendation Engine

- [ ] Define treatment recommendation schema
- [ ] Add rule-based recommendations for baseline diseases
- [ ] Add fertilizer guidance
- [ ] Add prevention guidance
- [ ] Add AI-generated explanations
- [ ] Add weather-aware recommendations

## Application

- [ ] Refactor current Flask prototype around the new inference pipeline
- [ ] Preserve useful sensor and irrigation functionality
- [ ] Build desktop application prototype
- [ ] Plan mobile application architecture
- [ ] Add offline model packaging

## Future Expansion

- [ ] Local LLM integration
- [ ] Voice interaction
- [ ] Cloud synchronization
- [ ] Explainable AI visualizations
- [ ] Dataset update workflow
