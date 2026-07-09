"""Label normalization helpers."""

from __future__ import annotations

import re

PLANT_ALIASES = {
    "bell pepper": "Pepper Bell",
    "pepper bell": "Pepper Bell",
    "pepper": "Pepper Bell",
    "corn maize": "Corn",
    "data": "Corn",
    "maize": "Corn",
    "cherry including sour": "Cherry",
    "original dataset": "Pumpkin",
    "pea plant dataset": "Pea",
    "test disease severity level": "Strawberry",
}

GENERIC_PLANT_LABELS = frozenset({
    "data",
    "original dataset",
    "pea plant dataset",
    "test disease severity level",
})

AUGMENTATION_SUFFIXES = (
    "brightness adjusted",
    "contrast adjusted",
    "cropped",
    "flipped horizontal",
    "flipped vertical",
    "gaussian noise",
    "high pass",
    "hist equalized",
    "jittered",
    "laplacian",
    "poisson noise",
    "rotated",
    "salt pepper noise",
    "saturation adjusted",
    "sobel",
    "translated",
    "unsharp mask",
)

KNOWN_PLANTS = (
    "apple",
    "tomato",
    "potato",
    "corn",
    "maize",
    "cherry",
    "grape",
    "pea",
    "peach",
    "orange",
    "strawberry",
    "soybean",
    "pumpkin",
    "pepper",
)

DISEASE_ALIASES = {
    "haunglongbing citrus greening": "Huanglongbing Citrus Greening",
    "cercospora leaf spot gray leaf spot": "Cercospora Leaf Spot Gray Leaf Spot",
    "spider mites two spotted spider mite": "Spider Mites Two-Spotted Spider Mite",
    "angular leafspot": "Angular Leaf Spot",
}

def normalize_token(value: str) -> str:
    """Convert dataset label text into spaced, readable text."""

    text = value.strip()
    text = text.replace("___", " ")
    text = text.replace("__", " ")
    text = text.replace("_", " ")
    text = text.replace("-", " ")
    text = text.replace("/", " ")
    text = text.replace("\\", " ")
    text = text.replace(",", " ")
    text = text.replace("(", " ")
    text = text.replace(")", " ")
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def title_label(value: str) -> str:
    """Title-case a label without losing common separators."""

    clean = normalize_token(value)
    if not clean:
        return "Unknown"
    return " ".join(word.capitalize() for word in clean.split())


def canonical_plant(value: str) -> str:
    clean = normalize_token(value).lower()
    return PLANT_ALIASES.get(clean, title_label(clean))


def canonical_disease(value: str) -> str:
    clean = strip_augmentation_suffix(normalize_token(value)).lower()
    if clean in {"", "unknown"}:
        return "Unknown"
    if clean in {"healthy", "normal"}:
        return "Healthy"
    return DISEASE_ALIASES.get(clean, title_label(clean))


def make_task_disease_label(plant: str, disease: str) -> str:
    """Create a unique disease class label that keeps plant context."""

    if disease == "Unknown":
        return f"{plant} Unknown"
    return f"{plant} {disease}"


def infer_plant_hint(value: str) -> str:
    """Infer a plant name from dataset or path text when class labels omit it."""

    clean = normalize_token(value).lower()
    words = set(clean.split())
    for plant in KNOWN_PLANTS:
        if plant in words:
            return canonical_plant(plant)
    return ""


def remove_plant_prefix(label: str, plant: str) -> str:
    """Remove a repeated plant prefix or suffix from a disease label."""

    clean_label = normalize_token(label)
    clean_plant = normalize_token(plant)
    if clean_label.lower().startswith(clean_plant.lower() + " "):
        clean_label = clean_label[len(clean_plant) :].strip()
    if clean_label.lower().endswith(" " + clean_plant.lower()):
        clean_label = clean_label[: -len(clean_plant)].strip()
    return clean_label


def is_generic_plant_label(value: str) -> bool:
    """Return true for folder names that are containers, not real plant labels."""

    return normalize_token(value).lower() in GENERIC_PLANT_LABELS


def strip_augmentation_suffix(value: str) -> str:
    """Collapse augmented class folders back to the base disease label."""

    clean = normalize_token(value)
    lowered = clean.lower()
    for suffix in AUGMENTATION_SUFFIXES:
        if lowered.endswith(" " + suffix):
            return clean[: -len(suffix)].strip()
    return clean
