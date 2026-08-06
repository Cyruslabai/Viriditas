# Metadata

This directory is intentionally excluded from Git.

Generate the metadata by running:

```bash
python notebooks/01_dataset_index_builder.py
```

Expected generated files include:

- `plant_id_dataset.csv`
- `disease_dataset.csv`
- `master_dataset.csv`
- `label_map_plants.json`
- `label_map_diseases.json`
- `dataset_summary.json`

For Kaggle training reruns, export these files as the `viriditas-artifacts`
dataset so the training and inference loaders can resolve stable metadata and
label maps from `/kaggle/input`.
