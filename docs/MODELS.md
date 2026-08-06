# Models

Model files are not tracked by Git. Place trained models here.

## Versioned Model Naming

The official model for each version follows this naming convention:

```
viriditas_best_v01.keras
viriditas_best_v02.keras
viriditas_best_v03.keras
...
```

**The best validation checkpoint is the canonical model.** No separate "final model" is saved.

The current version is configured in `src/viriditas/config/settings.py`:
```python
MODEL_VERSION = "v02"
```

From this, all model paths are automatically derived:
- `BEST_MODEL_FILENAME` = `viriditas_best_v02.keras` (official model loaded for inference)
- `TRAINING_HISTORY_FILENAME` = `viriditas_training_history_v02.json` (training metrics)

## Switching Versions

To switch from v02 to v03, change only:
```python
MODEL_VERSION = "v03"
```

All module paths (training, inference, evaluation) update automatically. No other source-code modifications needed.

## Model Resolution

On Kaggle, inference searches attached model artifacts for the versioned model. Local development falls back to `models/` directory.

