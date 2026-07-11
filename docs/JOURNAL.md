# VIRIDITAS Project Journal

This journal records the engineering history, decisions, run results, blockers, and resume notes for VIRIDITAS. `PROJECT_PLAN.md` remains the source of truth for architecture; this file is the chronological working memory.

## 2026-07-11

### Session Goal

Verify the 2026-07-10 label-parsing fixes actually took effect, resolve any remaining `Unknown` disease rows, and complete the duplicate-group review that was flagged as the next milestone.

### Discovery: Yesterday's Fix Was Never Pushed

Checked the live commit on GitHub `main` via the GitHub API and found the latest commit was `e004f69 Refresh cached modules in Kaggle runner`, dated 2026-07-09 — one day *before* the label-normalization fix was supposedly made. `git status` locally confirmed `main` and `origin/main` had diverged (1 commit ahead locally, 1 commit ahead on the remote). The fix existed locally but had never actually been pushed.

Resolved with:

```bash
git pull origin main   # clean auto-merge, no conflicts
git push origin main
```

After this, refetched `normalizer.py` from `raw.githubusercontent.com` directly and confirmed the fix (`PLANT_ALIASES` entries for `data`, `original dataset`, `pea plant dataset`, `test disease severity level`) was finally live.

### Rerun After Session Restart

Restarted the Kaggle session fully (not just rerun) to rule out stale imports, then reran:

```python
%cd /kaggle/working/Viriditas
%run notebooks/01_dataset_index_builder.py
```

Result:

```text
Indexed 201094 images
```

Validation:

```text
Data 0
Original Dataset 0
Pea Plant Dataset 0
Test Disease Severity Level 0
```

All four bad plant labels confirmed at zero. The 2026-07-10 fix was correct all along — it just hadn't been running.

### Remaining Unknown Disease Rows: Root Cause

With bad plant labels resolved, `Unknown` disease rows were rechecked:

```text
Unknown diseases: 2507
strawberry disease detection dataset    2500
apple disease dataset                      7
```

**Apple (7 rows):** confirmed to be a literal `Unknown/` folder in the source Kaggle dataset — not a parser bug, just unlabeled source data. Left as-is (low priority, negligible size).

**Strawberry (2500 rows):** traced via `image_path` and found two folder-layout patterns the parser didn't handle:

1. Flat split folder with no class subfolder at all, e.g.:
   ```text
   .../strawberry-disease-detection-dataset/test/angular_leafspot351.jpg
   ```
   The disease name was encoded in the filename, not the folder structure.

2. A nested non-informative container, e.g.:
   ```text
   .../strawberry-disease-detection-dataset/Test Disease Severity Level/Level 1/angular_leafspot359.jpg
   ```
   This has folders, but they're meaningless severity buckets, not real class names. The old parser was joining the last two folder names into a fake label like `"Test Disease Severity Level___Level 1"`, producing garbage disease classes `"Level 1"` (537 rows) and `"Level 2"` (206 rows).

Distinct filename prefixes present in the strawberry dataset, checked directly against the raw files:

```text
['angular_leafspot', 'anthracnose_fruit_rot', 'blossom_blight', 'gray_mold',
 'leaf_spot', 'powdery_mildew_fruit', 'powdery_mildew_leaf']
```

### Parser Fixes Implemented (Round 2)

In `layout_detection.py`:

- Added `_label_from_filename()`: strips trailing digits and the file extension from
  a filename to recover the encoded label (e.g. `angular_leafspot351.jpg` ->
  `angular_leafspot`). Triggers whenever `label_parts` ends up empty after existing
  trimming logic.
- Added `_strip_non_informative_parts()`: removes folder segments matching
  `"test disease severity level"` or the pattern `Level \d+`, even if that empties
  the whole `label_parts` tuple (unlike the pre-existing `_trim_non_class_prefix`,
  which always leaves at least one part). This lets the filename fallback trigger
  underneath nested severity-level containers.

In `normalizer.py`:

- Added one `DISEASE_ALIASES` entry: `"angular leafspot": "Angular Leaf Spot"`
  (the only one of the 7 strawberry disease names that didn't title-case correctly
  on its own).

In `scanners.py`:

- Fixed a leftover import bug from the AgriAI -> VIRIDITAS rename:
  `from agriai.data.config import ...` -> `from viriditas.data.config import ...`.
  Found by chance while reviewing the file; unclear whether this was actually
  breaking anything at runtime, but left uncorrected it was a landmine.

Verified via session restart + full rerun:

```text
Unknown diseases: 7
```

Only the genuine apple `Unknown` folder remains. Strawberry disease breakdown after
the fix (totals 3243, matching the dataset's known size):

```text
Leaf Spot                777
Powdery Mildew Leaf      684
Gray Mold                622
Angular Leaf Spot        582
Blossom Blight           270
Powdery Mildew Fruit     178
Anthracnose Fruit Rot    130
```

### Duplicate Group Review

Moved to the next TODO item. Discovered `duplicates.py` had SHA-256 hashing logic and
unit tests, but was **never actually called** from `index_builder.py` —
`duplicate_group_id` existed in the planned schema (`PROJECT_PLAN.md`) but had never
been populated in real output. Ran hashing manually as a stopgap against the existing
`master_dataset.csv`:

```text
Duplicate groups: 7571
Images involved in duplicates: 15209
Images involved in cross-split leakage: 6176
Duplicate groups spanning multiple splits: 3057
```

Leakage broken down by dataset:

```text
peach leaf diseases plant village augmented data    1496
pepper leaf diseases plant village augmented data   1370
strawberry disease detection dataset                1346
cherry leaf diseases plant village augmented data   1084
tomato                                                784
pea plant dataset                                      70
apple disease dataset                                  18
potato disease leaf datasetpld                          6
pumpkin leaf diseases dataset from bangladesh           2
```

Heaviest in the pre-augmented plant-village-style datasets (peach, pepper, cherry)
plus tomato and strawberry — consistent with these datasets shipping already split
by their original authors, with the same source image ending up duplicated across
splits (sometimes via augmentation) before VIRIDITAS ever sees them.

Manually resolved as a one-off first (keep one copy per cross-split duplicate group,
preferring `train`, drop the rest):

```text
Rows to drop due to cross-split leakage: 3119
New total: 197975
Remaining cross-split leakage after fix: 0
```

### Making Duplicate Resolution Permanent

Rather than leave this as a manual notebook patch, wired it into the pipeline for
real:

- `schemas.py`: added `duplicate_group_id: str = ""` to `ImageRecord` and to
  `CSV_FIELDNAMES`.
- `duplicates.py`: added `deduplicate_records(records, prefer_split="train",
  cache_path=...)`. Hashes every record, tags all of them with a
  `duplicate_group_id` (first 16 hex chars of the SHA-256 hash) regardless of
  whether they're duplicated, and for any group spanning more than one split, keeps
  exactly one record (preferring `prefer_split`) and drops the rest. Also added
  `hash_with_cache()` plus CSV-based cache load/save helpers, so files whose size
  and mtime haven't changed since the last run are not re-hashed.
- `splits.py`: fixed `_replace_split()`, which was manually reconstructing every
  `ImageRecord` field by hand — a fragile pattern that would have silently dropped
  `duplicate_group_id` (or any future field) since it wasn't in the manual list. Now
  uses `dataclasses.replace(record, split=split)` instead.
- `01_dataset_index_builder.py`: added the import and called
  `deduplicate_records()` immediately after `assign_splits()` and before any CSV is
  written, with `cache_path=OUTPUT_DIR / "hash_cache.csv"`.

Verified with a full clean rebuild (fresh session restart, not incremental):

```text
Deduplication: {'total_input': 201094, 'total_output': 197975, ...,
 'duplicate_groups_total': ~7571, 'cross_split_groups': ~3057,
 'rows_dropped_for_leakage': ~3119, 'cache_hits': 0}
Total images: 197975
Has duplicate_group_id column: True
Non-empty duplicate_group_id count: 197975
Cross-split leakage in fresh build: 0
```

Fresh pipeline output matches the manual fix exactly, with `duplicate_group_id`
finally populated for every row as the schema always intended.

### Hash Cache Persistence

The hash cache (`data/metadata/hash_cache.csv`, ~48 MB for 197,975 entries) only
persists within a Kaggle session by default (`/kaggle/working` is wiped on restart).
To make the speedup durable across fresh sessions, downloaded it from Kaggle and
committed it to GitHub.

This required a `.gitignore` fix. The existing rule `/data/` fully excluded the
`data/` directory, and git's negation (`!`) rules cannot re-include a path whose
*parent directory* is already fully excluded — confirmed via:

```bash
git check-ignore -v data/metadata/hash_cache.csv
# .gitignore:38:/data/    data/metadata/hash_cache.csv
```

First attempt (`/data/` + `!/data/metadata/` + `!/data/metadata/**`) still failed for
this reason. Fixed by ignoring only the *contents* of `data/` rather than the folder
itself:

```text
/data/*
!/data/metadata/
```

This leaves `data/` itself un-excluded, so git evaluates rules inside it, and the
negation for `data/metadata/` now works. Verified with `git check-ignore` (no
output = not ignored), then committed and pushed.

### Relevant Commits

```text
(pull/merge of diverged label-fix commit)
Strip severity-level folders and fall back to filename labels
Track metadata dedup hash cache, refine .gitignore data/ exception
```

### Current Resume Point

Preprocessing, label normalization, and duplicate-leakage resolution are complete
and permanently wired into the pipeline — not manual patches. Dataset is stable at
197,975 images.

Remaining before training starts:

1. Decide handling for the 7 remaining unlabeled apple images (drop vs. keep as a
   tiny `Unknown` class — dropping is the simpler default, no urgency either way).
2. Create `notebooks/02_train_plant_model.ipynb`.
3. Train a baseline plant identification model.

To rebuild from a fresh Kaggle session at any point:

```python
%cd /kaggle/working/Viriditas
%run notebooks/01_dataset_index_builder.py
```

This now runs label parsing, split assignment, and duplicate resolution in one pass,
and reuses the committed `data/metadata/hash_cache.csv` for any file it's already
hashed before.

### Current Risks

- No unit tests yet for the filename-based label fallback or non-informative folder
  stripping added today, despite both being load-bearing for 3,243 strawberry
  images. Worth adding before touching `layout_detection.py` again.
- No unit tests yet for `deduplicate_records()` or the hash cache's hit/miss logic.
- The hash cache is committed as a flat CSV (~48 MB currently); worth watching repo
  size as more datasets are added — may eventually want a smarter storage format or
  to move it out of git entirely (e.g. Kaggle Dataset output) if it keeps growing.
- Cross-split leakage resolution currently always prefers keeping the `train` copy.
  Have not verified this doesn't meaningfully shrink val/test for any single
  plant/disease class to an unhealthy size — worth a quick class-balance check
  before training.

### Next Engineering Milestone

Start model training:

1. Decide on the 7 unlabeled apple images.
2. Create `02_train_plant_model.ipynb`.
3. Train a baseline plant identification model (EfficientNetV2B0 / MobileNetV3 /
   ConvNeXt-Tiny per `PROJECT_PLAN.md`'s Model Architecture Direction).
4. Once stable, create `03_train_disease_model.ipynb` and repeat for disease
   classification.

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

Note (added 2026-07-11): the "not in git" rule for generated metadata was
deliberately broken for `data/metadata/hash_cache.csv` specifically, to make
duplicate-detection speedups durable across fresh Kaggle sessions. See the
2026-07-11 entry above for the reasoning and the `.gitignore` change this required.

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

Note (added 2026-07-11): this "another refinement pass" is exactly what the
2026-07-11 entry above covers — turned out to require two separate rounds of
fixes, since the first round (below) fixed the plant labels but not the
underlying strawberry Unknown rows.

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

Note (added 2026-07-11): commit `38037fb` above was made locally but not actually
pushed to `origin/main` at the time this note was originally written — `e004f69`
was the actual tip of `main` on GitHub until 2026-07-11. See that day's entry for
how this was caught and fixed.

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

### Historical Resume Point (superseded — see 2026-07-11 entry for current state)

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

### Historical Risks (superseded — see 2026-07-11 entry for current risks)

- Need to rerun Kaggle after the latest parser and cache-clearing fixes.
- Need to inspect whether the 2507 unknown disease rows are legitimate unlabeled classes or parser misses.
- Need to review duplicate groups before training to reduce leakage risk.
- Need to decide whether augmented datasets should be split by original image lineage where possible.

### Historical Next Milestone (superseded — see 2026-07-11 entry for current milestone)

Finish the dataset validation milestone:

1. Rerun Kaggle preprocessing with the latest repo.
2. Inspect `dataset_summary.json`.
3. Confirm bad plant labels are zero.
4. Review unknown disease rows.
5. Review class balance.
6. Commit the final validation results.
7. Start `02_train_plant_model.ipynb`.
