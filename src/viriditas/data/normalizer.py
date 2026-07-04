"""Label normalization helpers."""

from __future__ import annotations

import re

PLANT_ALIASES = {
    "bell pepper": "Pepper Bell",
    "pepper bell": "Pepper Bell",
    "pepper": "Pepper Bell",
    "corn maize": "Corn",
    "maize": "Corn",
    "cherry including sour": "Cherry",
}

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
    clean = normalize_token(value).lower()
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
    """Remove a repeated plant prefix from a disease label when present."""

    clean_label = normalize_token(label)
    clean_plant = normalize_token(plant)
    if clean_label.lower().startswith(clean_plant.lower() + " "):
        return clean_label[len(clean_plant) :].strip()
    return clean_label
