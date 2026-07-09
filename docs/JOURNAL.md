# VIRIDITAS Project Journal

This journal records the engineering history, decisions, run results, blockers, and resume notes for VIRIDITAS. `PROJECT_PLAN.md` remains the source of truth for architecture; this file is the chronological working memory.

## 2026-07-10

### Project Identity

- The project is named `VIRIDITAS`.
- Repository: `https://github.com/Cyruslabai/Viriditas`.
- The earlier project name was AgriAI, but VIRIDITAS is now the active product and code identity.
- The Python package was renamed from `agriai` to `viriditas`.

### Current Goal

Build a metadata-driven preprocessing system that combines many Kaggle plant disease datasets into one standardized training index without copying images.

The immediate output target is:

```text
/kaggle/working/data/metadata/
|-- master_dataset.csv
|-- plant_id_dataset.csv
|-- disease_dataset.csv
|-- train.csv
|-- val.csv
|-- test.csv
|-- label_map_plants.json
|-- label_map_diseases.json
|-- dataset_summary.json
```

### Architecture Decisions Captured

- Use metadata CSVs instead of physically copying images.
- Keep preprocessing, plant-model training, disease-model training, and inference in separate notebooks.
- Use two models first:
  - Model 1: plant identification.
  - Model 2: disease classification.
- Keep notebooks thin and move reusable logic into `src/viriditas/`.
- Store generated metadata under Kaggle working storage, not in git.
- Use GitHub as the durable source of code truth so Kaggle sessions can be recreated.

### Main Mistakes Avoided Going Forward

- Do not copy image files into new train/validation/test folders.
- Do not mix preprocessing and training in one notebook.
- Do not assume all Kaggle datasets share the same folder structure.
- Do not trust initial labels until `master_dataset.csv` and `dataset_summary.json` are inspected.

### Implemented Code Structure

```text
src/viriditas/data/
|-- config.py
|-- duplicates.py
|-- index_builder.py
|-- io.py
|-- label_parser.py
|-- layout_detection.py
|-- normalizer.py
|-- scanners.py
|-- schemas.py
|-- splits.py
|-- __init__.py

notebooks/
|-- 01_dataset_index_builder.ipynb
|-- 01_dataset_index_builder.py

scripts/
|-- build_dataset_index.py

tests/
|-- test_duplicates.py
|-- test_label_parser.py
|-- test_layout_detection.py
|-- test_splits.py
```

### Kaggle Dataset Roots

The current Kaggle preprocessing notebook is configured for these 13 dataset roots:

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

### Successful Kaggle Run

Kaggle successfully indexed:

```text
Indexed 201094 images
Metadata directory: /kaggle/working/data/metadata
Files: master_dataset.csv, plant_id_dataset.csv, disease_dataset.csv, split CSVs, label maps, dataset_summary.json
```

This confirmed the metadata-first pipeline can process the selected Kaggle data without image copying.

### Validation Findings From First Kaggle Output

The first metadata validation found unexpected plant labels:

```text
Data                         4188
Original Dataset             2000
Pea Plant Dataset            1432
Test Disease Severity Level   743
```

It also showed augmented labels being treated as new diseases, for example:

```text
Peach Bacterial Spot Brightness Adjusted
Pepper Bell Bacterial Spot Gaussian Noise
```

Unknown disease rows were also observed:

```text
Unknown diseases: 2507
```

Known split from the validation:

- Apple contributed 7 unknown disease rows.
- Strawberry contributed 2500 unknown disease rows.

These findings mean the index builder worked, but label normalization needed another refinement pass before model training.

### Parser Fixes Implemented

The parser was updated to:

- Treat generic dataset containers as non-label folders.
- Use dataset-name plant hints for labels such as `Data`, `Original Dataset`, `Pea Plant Dataset`, and `Test Disease Severity Level`.
- Strip augmentation operation suffixes from disease labels.
- Remove repeated plant names from the end of disease labels.
- Add unit tests for generic folder labels and augmentation suffix collapse.

Relevant commits:

```text
38037fb Fix dataset label normalization
e004f69 Refresh cached modules in Kaggle runner
```

### Kaggle Module Cache Issue

Kaggle can keep old imported Python modules alive after downloading new repo code. The notebook runner now clears cached `viriditas` modules before importing:

```python
for module_name in list(sys.modules):
    if module_name == "viriditas" or module_name.startswith("viriditas."):
        del sys.modules[module_name]
```

This avoids rerunning stale parser code after a fresh GitHub download.

### GitHub and Kaggle Access Notes

- Git clone over HTTPS asked for a username in Kaggle even when the repo was made public.
- GitHub codeload ZIP returned 404 while the repo was private or inaccessible.
- The working solution was GitHub API ZIP download using a Kaggle secret.
- The Kaggle secret label used by the user is `github`.
- A GitHub token was exposed in a screenshot during troubleshooting; it should stay revoked and replaced.
- Never paste tokens directly into notebooks. Use Kaggle Secrets.

### Current Resume Point

The next Kaggle action is to download the latest GitHub code, run the dataset index builder again, and verify that the bad plant labels are gone.

Proof checks to run after downloading:

```bash
grep -R "GENERIC_PLANT_LABELS" -n /kaggle/working/Viriditas/src/viriditas/data
grep -R "AUGMENTATION_SUFFIXES" -n /kaggle/working/Viriditas/src/viriditas/data
grep -R "sys.modules" -n /kaggle/working/Viriditas/notebooks/01_dataset_index_builder.py
```

Then run:

```python
%cd /kaggle/working/Viriditas
%run notebooks/01_dataset_index_builder.py
```

Then validate:

```python
bad_plants = ["Data", "Original Dataset", "Pea Plant Dataset", "Test Disease Severity Level"]
for plant in bad_plants:
    print(plant, (df["plant"] == plant).sum())
```

Expected result:

```text
Data 0
Original Dataset 0
Pea Plant Dataset 0
Test Disease Severity Level 0
```

### Current Risks

- Need to rerun Kaggle after the latest parser and cache-clearing fixes.
- Need to inspect whether the 2507 unknown disease rows are legitimate unlabeled classes or parser misses.
- Need to review duplicate groups before training to reduce leakage risk.
- Need to decide whether augmented datasets should be split by original image lineage where possible.

### Next Engineering Milestone

Finish the dataset validation milestone:

1. Rerun Kaggle preprocessing with the latest repo.
2. Inspect `dataset_summary.json`.
3. Confirm bad plant labels are zero.
4. Review unknown disease rows.
5. Review class balance.
6. Commit the final validation results.
7. Start `02_train_plant_model.ipynb`.

