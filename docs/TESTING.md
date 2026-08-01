# Testing Guide

Run tests
---------
- Install test deps: `pip install -r requirements.txt` (ensure pytest installed)
- Run all tests: `pytest -q`

Test fixtures
-------------
- `tests/conftest.py` provides fixtures for:
  - sample_image (a small generated image in `data/images/img1.jpg`)
  - metadata_csv (the minimal `data/metadata/plant_id_dataset.csv`)
  - models_dir (paths.models_dir)

Types of tests
--------------
- Unit tests: small, focused functions (e.g., dataset.make_dataset, reports top-k logic).
- Integration tests: evaluator.run() on a minimal dataset to exercise training→inference→evaluation flow.

Smoke tests
-----------
- Previously ad-hoc smoke scripts were replaced with pytest tests under `tests/`.
- Keep smoke fixtures minimal and avoid production datasets.

Production validation
---------------------
- Run Evaluator on the real dataset in a controlled environment (Kaggle/Colab or a machine with access to the full data and models).
- Validate outputs under `models/analysis/` and verify metrics.

Notes
-----
- Tests do not require the full production dataset.
- Warnings about single-class softmax or sklearn single-label are expected when running tests with minimal fixtures.
- Add coverage reporting in CI if desired.
