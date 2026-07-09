# VIRIDITAS Kaggle Runbook

This runbook is the exact recovery path for running VIRIDITAS preprocessing inside Kaggle after closing the laptop, restarting a session, or losing `/kaggle/working`.

## 1. Required Kaggle Setup

Attach the 13 Kaggle datasets under:

```text
/kaggle/input/datasets/
```

Create a Kaggle secret:

```text
Label: github
Value: your GitHub personal access token
```

Do not paste the token directly into notebook cells.

## 2. Download Latest Repo From GitHub

Run this Kaggle cell:

```python
import shutil
import zipfile
from pathlib import Path

import requests
from kaggle_secrets import UserSecretsClient

token = UserSecretsClient().get_secret("github")

zip_path = Path("/kaggle/working/Viriditas.zip")
target = Path("/kaggle/working/Viriditas")
extract_root = Path("/kaggle/working/Viriditas_extract")

shutil.rmtree(target, ignore_errors=True)
shutil.rmtree(extract_root, ignore_errors=True)
zip_path.unlink(missing_ok=True)

url = "https://api.github.com/repos/Cyruslabai/Viriditas/zipball/main"
headers = {
    "Authorization": f"Bearer {token}",
    "Accept": "application/vnd.github+json",
}

response = requests.get(url, headers=headers, timeout=60)
print("Status:", response.status_code)

if response.status_code != 200:
    print(response.text[:1000])
    raise SystemExit("Download failed")

zip_path.write_bytes(response.content)

with zipfile.ZipFile(zip_path, "r") as zf:
    zf.extractall(extract_root)

repo_folder = next(extract_root.iterdir())
shutil.move(str(repo_folder), str(target))

print("Downloaded to:", target)
print("Files:", [p.name for p in target.iterdir()])
```

Expected status:

```text
Status: 200
Downloaded to: /kaggle/working/Viriditas
```

## 3. Confirm Latest Parser Code Is Present

Run:

```python
!grep -R "GENERIC_PLANT_LABELS" -n /kaggle/working/Viriditas/src/viriditas/data
!grep -R "AUGMENTATION_SUFFIXES" -n /kaggle/working/Viriditas/src/viriditas/data
!grep -R "sys.modules" -n /kaggle/working/Viriditas/notebooks/01_dataset_index_builder.py
```

All three commands should print matching lines.

## 4. Run Preprocessing

Run:

```python
%cd /kaggle/working/Viriditas
%run notebooks/01_dataset_index_builder.py
```

Expected output shape:

```text
Indexed 201094 images
Metadata directory: /kaggle/working/data/metadata
Files: master_dataset.csv, plant_id_dataset.csv, disease_dataset.csv, split CSVs, label maps, dataset_summary.json
```

## 5. Validate Output

Run:

```python
import json
from pathlib import Path

import pandas as pd

metadata_dir = Path("/kaggle/working/data/metadata")
df = pd.read_csv(metadata_dir / "master_dataset.csv")

print("Shape:", df.shape)
print("\nPlants:")
print(df["plant"].value_counts())
print("\nSplits:")
print(df["split"].value_counts())
print("\nTop disease labels:")
print(df["task_disease_label"].value_counts().head(80))
print("\nUnknown plants:", len(df[df["plant"].str.contains("Unknown", case=False, na=False)]))
print("Unknown diseases:", len(df[df["disease"].str.contains("Unknown", case=False, na=False)]))

summary = json.loads((metadata_dir / "dataset_summary.json").read_text())
summary
```

Then run the bad-label check:

```python
bad_plants = ["Data", "Original Dataset", "Pea Plant Dataset", "Test Disease Severity Level"]

for plant in bad_plants:
    count = (df["plant"] == plant).sum()
    print(plant, count)

display(
    df[df["plant"].isin(bad_plants)]
    [["dataset_name", "original_label", "plant", "disease", "image_path"]]
    .head(50)
)
```

Expected result:

```text
Data 0
Original Dataset 0
Pea Plant Dataset 0
Test Disease Severity Level 0
```

## 6. If Kaggle Still Shows Old Labels

Run the download cell again, restart the Kaggle session, and rerun from step 3.

The notebook runner clears cached `viriditas` modules, but a hard restart is still acceptable if Kaggle behaves strangely.

## 7. What Is Safe To Lose

Safe to lose:

- `/kaggle/working/Viriditas`
- `/kaggle/working/data/metadata`
- generated CSV files

Not safe to lose:

- GitHub repo updates
- Kaggle secret access
- attached dataset list

The repo is the durable source. If `/kaggle/working` resets, rerun this runbook.

