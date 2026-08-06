# JOURNAL.md

# VIRIDITAS Project Journal

## 2026-08-06

### Artifact-Backed Training And Inference Alignment

Updated the project records after the latest training/configuration changes.
The plant trainer now asks `load_metadata(use_artifact=True)` for
`plant_id_dataset.csv` so Kaggle training can consume an attached
`viriditas-artifacts` dataset instead of depending on regenerated files in
`/kaggle/working`.

The trainer also loads `label_map_plants.json` through the shared inference
loader before building the model. This keeps the model output dimension and
class indices aligned with the generated metadata artifact, rather than
recomputing a label map from whichever dataframe happens to be loaded.

Path configuration now distinguishes writable working outputs from read-only
artifact inputs, and inference resources are lazily cached on first use. The
legacy `src/agriai/` blocker is no longer present in the active source tree;
`src/viriditas/` is the sole active namespace.

## 2026-08-01 22:34:21 — Phase 9: Final Cleanup (completed)

Summary:

- Completed Phase 9: Production Readiness & Final Cleanup.
- Deleted temporary developer artifacts and moved the synthetic test image to tests/fixtures/img1.jpg.
- Updated repository metadata to point tests to the fixture image and removed temporary smoke-test scripts.
- Ran full test suite: 21 passed, 4 expected warnings. Import and architecture checks passed; no circular imports found.
- Updated TODO.md and PROJECT_PLAN.md to mark the training, inference, and evaluation package extractions as completed.

This entry finalizes the refactor work and marks the architecture stable and ready for development tasks (datasets, model improvements, deployment).

This journal records the engineering history, decisions, run results,
blockers, and resume notes for VIRIDITAS. `PROJECT_PLAN.md` remains the source
of truth for architecture; this file is the chronological working memory.

## 2026-08-01

### Session Goal

Transition VIRIDITAS from a notebook-centric research workflow to a
production-oriented Python package, and bring project documentation in line
with the current organizational scope (Cyrus Labs AI, Version 1 software-only
platform: plant identification, disease detection, recommendation engine,
FastAPI, Flutter, future LLM assistant).

### Architecture Refactor: Production Package Structure

Reason: business logic had grown spread across notebooks, making testing,
reuse, API integration, and long-term maintenance increasingly difficult, even
though the notebook-based approach had successfully proven out the dataset
pipeline and baseline training workflow (see 2026-07-04 through 2026-07-19
entries below).

Action: began moving reusable logic into `src/viriditas/`, organized as
`config/`, `data/`, `preprocessing/`, `training/`, `inference/`,
`evaluation/`, `models/`, and `utils/`. Notebooks are being converted into
thin wrappers responsible only for orchestration (loading configuration,
calling reusable functions, visualizing results) — not for containing
business logic themselves. `src/viriditas/data/` (dataset preprocessing) and
the new `src/viriditas/preprocessing/` (model-input preprocessing) are
implemented; `training/`, `inference/`, and `evaluation/` are in progress,
with their logic currently still living in `notebooks/02_train_plant_model.py`
and `notebooks/03_model_analysis.py` respectively.

### Configuration Centralization

Implemented `src/viriditas/config/` (`settings.py`, `environment.py`,
`__init__.py`), replacing scattered per-notebook constants (`IMAGE_SIZE`,
`BATCH_SIZE`, `MODEL_DIR`, `OUTPUT_DIR`, `METADATA_DIR`) with configuration
objects: `image_config.SIZE`, `image_config.BATCH_SIZE`, `paths.models_dir`,
`paths.metadata_dir`, `paths.resolve_model_path()`, plus `training_config` and
`dataset_config`. Added automatic environment detection supporting Local,
Kaggle, and Google Colab, so metadata paths, model paths, and output
directories no longer need to be hardcoded per notebook.

### Centralized Preprocessing

This is considered the largest completed milestone after the original dataset
pipeline. Previously, training, evaluation, and any future inference code each
implemented their own image loading, resizing, normalization, and
EfficientNet-specific preprocessing — a real risk of preprocessing drift
between what a model was trained on and what it would see at inference time.
Consolidated this into a single implementation inside `src/viriditas/`, now
intended to be the one and only preprocessing path for every current and
future consumer (training, evaluation, inference, the future FastAPI backend,
and the future Flutter client).

### Smoke Testing

After the configuration and preprocessing refactor, ran architectural smoke
tests covering import validation, configuration validation, and centralized
preprocessing validation. All three passed. Two failures were observed during
testing:

- Missing `pandas` in an isolated sandbox environment.
- A missing local model artifact.

Both were confirmed to be environment/setup issues rather than architectural
regressions — i.e., the refactored code itself is sound; the failures were
about the test environment not having the same setup as the working Kaggle
environment. An import conflict encountered during this testing pass was also
identified and resolved.

### Product Scope Clarification

Documented, for the first time in the project's formal records, that VIRIDITAS
sits under Cyrus Labs AI and that Version 1 is explicitly software-only:
plant identification, disease detection, the AI recommendation engine,
FastAPI, and Flutter are in scope; Arduino, ESP32, IoT sensors, weather
stations, and other embedded/hardware integrations are archived / future
possibilities, not V1 objectives. This matters because the original Flask
prototype included real ESP32 sensor code (`arduino_sensor_sender.ino`), which
could otherwise be mistaken for active roadmap rather than historical
artifact.

### SDK Vision

Formally documented VIRIDITAS's long-term architecture goal: a reusable AI SDK
whose core modules (configuration, preprocessing, training, inference) can be
consumed by Kaggle notebooks, a future FastAPI backend, a future Flutter
client, CLI utilities, and future LLM orchestration, without duplicating
business logic per consumer. This is the underlying reason configuration and
preprocessing were centralized before extracting the training, inference, and
evaluation packages — those later extractions depend on having one shared
configuration and preprocessing layer to build on top of.

### Lazy Model Loading

Originally documented as an architectural decision on 2026-08-01, then
implemented by 2026-08-06: inference modules avoid loading TensorFlow models
during module import and lazily initialize resources on first use. Rationale:
faster startup, easier testing, and better integration with FastAPI's request
lifecycle.

### Resume Point Superseded On 2026-08-06

Immediate priorities, in order:

1. Fix known issues in `notebooks/03_model_analysis.py` (local metadata
   fallback path, undefined misclassified-sample count constant, dataset
   accuracy plot axis using percentage values against a 0-1 x-axis limit)
   before treating its output as reliable.
2. Decide handling for the 7 remaining unlabeled apple images.
3. Run plant model analysis and record verified baseline metrics.
4. Create the disease-classification training workflow.
5. Begin FastAPI backend design around the plant inference package.

### Remaining Risks

- `03_model_analysis.py` has three known defects and should not yet be trusted
  for reported metrics until fixed.
- No unit tests yet cover the filename-based label fallback, non-informative
  folder stripping, duplicate-resolution logic, the hash cache's hit/miss
  behavior, or the new centralized preprocessing module.
- Several plant classes are sourced from only one or two of the 13 Kaggle
  datasets (e.g. Pea, Pumpkin, Strawberry), creating a risk that the plant
  identification model partially learns dataset-specific photography style
  rather than purely botanical features — flagged originally on 2026-07-16
  (see below) and still not fully investigated via the pending
  dataset-source-bias analysis in `03_model_analysis.py`.
- The hash cache is a flat CSV (~48 MB at 2026-07-11 scale); as of
  2026-07-19 generated artifacts including the cache are no longer tracked in
  git by default, so its persistence strategy (Kaggle Dataset artifact vs.
  something else) is an open decision if rebuild speed becomes painful again.

---

## 2026-07-19

### Session Goal

Move from a single dataset-index-and-train workflow toward a repeatable
training + evaluation cycle, and stop tracking generated artifacts in git.

### Training and Evaluation Scripts

Added `notebooks/02_train_plant_model.py`: a Kaggle-friendly EfficientNetV2B0
plant identification trainer with class weights, data augmentation, frozen-base
training followed by fine-tuning, checkpointing, and early stopping. Added
`notebooks/03_model_analysis.py` for evaluating the trained plant model:
predictions, top-k accuracy, confusion matrix, classification report,
per-class accuracy, confidence analysis, misclassified-sample review, and a
dataset-source-bias check.

Removed `tf.data` caching from the training input pipeline specifically to
reduce memory pressure during Kaggle training sessions — full in-memory
caching of the decoded image tensors for the full training set was pushing
against Kaggle's session memory limits.

### Artifact Cleanup

Decided generated artifacts (metadata CSVs, trained model files, analysis
outputs, caches, logs, temp files) should not be tracked in git going forward.
Removed previously tracked generated files from the repository, replacing them
with `.gitkeep` placeholders under `data/metadata/`, `models/`, and
`src/viriditas/data/metadata/` so the required directory structure still
exists for a fresh clone. `.gitignore` was refined accordingly. Locally
generated model files still exist under `models/.v01/` but are intentionally
gitignored.

### Known Follow-Ups Identified

- `03_model_analysis.py` has three specific defects: its local metadata
  fallback path points at `src/viriditas/data/metadata` (inconsistent with
  where the index builder actually writes output in some configurations); a
  misclassified-sample count constant is referenced but undefined; and the
  dataset-accuracy plot uses percentage values while the plotting code applies
  a 0-1 x-axis limit, which will visually clip or misrepresent the chart.
- `src/agriai/` was found to be tracked again despite `src/viriditas/` being
  the only active namespace since 2026-07-04 — needs removal or reconciliation.
- `notebooks/02_train_plant_model.ipynb` and `notebooks/03_model_analysis.ipynb`
  (the notebook-format wrappers, as opposed to the `.py` runner scripts) remain
  empty placeholders.

---

## 2026-07-16

### Baseline Plant Model: First Full Training Run and Overfitting Investigation

Trained the first full baseline using `02_train_plant_model.py` on Kaggle GPU
(T4 x2). Hit and resolved a mid-training crash: `InvalidArgumentError: Trying
to decode BMP format using a wrong op` — some source files had a `.jpg`
extension but were actually BMP-encoded internally. Fixed by switching from
`tf.image.decode_jpeg` to `tf.image.decode_image` (format-agnostic, detects
the real encoding regardless of extension), with `expand_animations=False` and
an explicit `image.set_shape([None, None, 3])` since `decode_image` does not
statically infer shape the way `decode_jpeg` does.

First full run (before augmentation/regularization improvements): train
accuracy ~99%, validation accuracy ~86%, test accuracy 78.2%. The 8-point
validation-to-test gap indicated validation accuracy was not a reliable
predictor of test performance — a sign of overfitting that validation alone
wasn't catching, plausibly including some dataset-source shortcut learning
(several plant classes are sourced from only one or two of the 13 datasets,
so the model could partly learn photography/dataset style rather than
botanical features).

Iterated on the training pipeline: added data augmentation (RandomFlip,
RandomRotation(0.10), RandomZoom(0.10), RandomContrast(0.10)), added
BatchNormalization between the pooled EfficientNet features and the dropout
layer, added EarlyStopping (monitor="val_loss", patience=2,
restore_best_weights=True) and ModelCheckpoint (save best by val_loss), and
kept two-phase training (frozen base, Adam 1e-3; then fine-tune with layers
before index 100 frozen, Adam 1e-5).

Result after these changes: test accuracy improved to 80.98%, validation
accuracy ~81.7-81.8%, and — the more important number — the validation-to-test
gap closed to roughly 1 percentage point, meaning validation metrics are now a
trustworthy proxy for test performance. Training accuracy remained high
(~97-99%) relative to validation, which is expected and not itself concerning
given only 5 epochs per phase and light augmentation; a model with
train~=val~=test would more likely indicate underfitting than success.

Also encountered and diagnosed as harmless: repeated
`layout failed: INVALID_ARGUMENT ... LayoutOptimizer` messages logged as
`E0000` during training (a cosmetic TensorFlow/XLA Grappler optimizer warning
related to dropout op layout on GPU, not a real error — training continued
normally immediately after every occurrence), and duplicated-looking
progress-bar lines per epoch (an artifact of `ModelCheckpoint`'s own verbose
logging interleaving with Keras's progress bar, not two separate epochs).

Decision: rather than continue tweaking the model architecture further,
perform error analysis first via a new `03_model_analysis.ipynb`
(confusion matrix, classification report, per-class accuracy, misclassified
image review, and a dataset-source-bias investigation) to determine whether
the remaining ~19% test error rate is concentrated in specific hard classes,
concentrated in single-source-dataset plant classes (testing the shortcut-
learning hypothesis directly), or evenly spread, before deciding what to fix
next.

---

## 2026-07-11

### Discovery: Yesterday's Fix Was Never Pushed

Checked the live commit on GitHub `main` via the GitHub API and found the
latest commit was `e004f69 Refresh cached modules in Kaggle runner`, dated
2026-07-09 — one day before the label-normalization fix documented on
2026-07-10 was supposedly made. `git status` locally confirmed `main` and
`origin/main` had diverged (1 commit ahead locally, 1 commit ahead on the
remote). The fix existed locally but had never actually been pushed. Resolved
with a clean `git pull` (auto-merge, no conflicts) followed by `git push`.
Refetched `normalizer.py` from `raw.githubusercontent.com` directly to confirm
the fix was finally live.

### Rerun After Session Restart

Restarted the Kaggle session fully (not just rerun) to rule out stale
imports, then reran the index builder. Result: `Indexed 201094 images`, and
all four bad plant labels (`Data`, `Original Dataset`, `Pea Plant Dataset`,
`Test Disease Severity Level`) confirmed at zero. The 2026-07-10 fix was
correct all along — it just hadn't been running.

### Remaining Unknown Disease Rows: Root Cause

With bad plant labels resolved, `Unknown` disease rows were rechecked: 2,507
total, with 2,500 from `strawberry-disease-detection-dataset` and 7 from
`apple-disease-dataset`. The apple 7 were confirmed to be a literal
`Unknown/` folder in the source dataset — not a parser bug, just unlabeled
source data.

The strawberry 2,500 were traced to two folder-layout patterns the parser
didn't handle: a flat split folder with no class subfolder at all (label
encoded only in the filename, e.g. `angular_leafspot351.jpg`), and a nested
non-informative container (`Test Disease Severity Level/Level 1/`) whose
folder names were meaningless severity buckets rather than real class names —
the old parser was joining the last two folder names into a fake label like
`"Test Disease Severity Level___Level 1"`, producing garbage disease classes
`"Level 1"` (537 rows) and `"Level 2"` (206 rows).

### Parser Fixes Implemented (Round 2)

In `layout_detection.py`: added `_label_from_filename()` (strips trailing
digits and extension from a filename to recover the encoded label, triggered
when `label_parts` ends up empty after existing trimming), and
`_strip_non_informative_parts()` (removes folder segments matching
`"test disease severity level"` or the pattern `Level \d+`, even if that
empties the whole `label_parts` tuple, letting the filename fallback trigger
underneath nested severity-level containers). In `normalizer.py`: added one
`DISEASE_ALIASES` entry (`"angular leafspot": "Angular Leaf Spot"`). In
`scanners.py`: fixed a leftover `from agriai.data.config import ...`
