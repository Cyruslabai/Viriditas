# VIRIDITAS Architecture

Overview
--------
VIRIDITAS is organized as modular layers that separate concerns: configuration, preprocessing, training, inference, and evaluation. This enables reuse, testing, and safe iteration.

Components
----------
- config
  - Centralized, environment-aware configuration (paths, image sizes, training hyperparameters).
  - Separates writable output directories from read-only Kaggle artifact inputs.
  - Use `from viriditas.config import paths, image_config, training_config`.

- preprocessing
  - Single ImagePreprocessor class that provides load_from_path, load_from_bytes, and convenience methods for producing numpy batches.
  - Ensures training and inference use identical preprocessing (EfficientNetV2 preprocess_input).

- training
  - dataset.py: metadata loading, optional artifact metadata resolution, label map creation, tf.data pipeline construction, class-weight computation.
  - model.py: EfficientNetV2B0 base, augmentation, head and compilation settings.
  - callbacks.py: factories for ModelCheckpoint and EarlyStopping.
  - trainer.py: PlantIdentifierTrainer orchestrates end-to-end training (frozen phase, fine-tune phase), loads the saved plant label map, and saves models and histories.

- inference
  - loader.py: lazy cached model and label-map loading through `paths.resolve_best_model_path()` and artifact-aware metadata resolution.
  - preprocessing.py: adapter that reuses ImagePreprocessor for inference.
  - predictor.py: PlantPredictor with predict and predict_batch methods returning decoded results.
  - postprocessing.py: decoding logits/probabilities to human-readable labels and confidences.

- evaluation
  - evaluator.py: high-level orchestrator that runs inference on the test split and produces reports/visuals.
  - reports.py: builds prediction DataFrame and saves CSVs.
  - metrics.py: classification metrics wrappers (classification_report, precision/recall/f1, per-class accuracy).
  - visualization.py: plots including confusion matrix and distribution plots.

Dataflow
--------
1. Metadata (`plant_id_dataset.csv`) is read by `training.dataset.load_metadata`; on Kaggle, the trainer requests attached artifact metadata when available.
2. dataset.make_dataset() builds tf.data pipelines using ImagePreprocessor.
3. trainer loads `label_map_plants.json`, builds model via model.build_model, compiles and trains using datasets, saves best model and final model.
4. inference.loader lazily loads the trained model and label map; predictor preprocesses inputs and returns decoded predictions.
5. evaluator uses loader and dataset utilities to run inference on the test split and produce reports and plots.

Design Principles
-----------------
- Single source of truth: configuration and preprocessing centralized.
- Small, testable modules: keep responsibilities focused and well-typed.
- Backwards-compatible wrappers: notebooks remain thin wrappers calling library code.
- Kaggle compatibility: environment-aware paths help notebooks run in Kaggle/Colab/Local.
