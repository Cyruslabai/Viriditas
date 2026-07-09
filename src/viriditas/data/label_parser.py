"""Parse plant and disease names from dataset labels."""

from __future__ import annotations

import re

from viriditas.data.normalizer import (
    canonical_disease,
    canonical_plant,
    is_generic_plant_label,
    normalize_token,
    remove_plant_prefix,
)
from viriditas.data.schemas import ParsedLabel

HEALTHY_PATTERN = re.compile(r"(^|[\s_/-])healthy($|[\s_/-])|(^|[\s_/-])normal($|[\s_/-])", re.I)


def parse_label(
    original_label: str,
    label_parts: tuple[str, ...] = (),
    plant_hint: str = "",
) -> ParsedLabel:
    """Parse a raw class label into plant, disease, and healthy fields.

    Supports common labels such as ``Tomato___Early_blight`` and nested
    folder labels such as ``Tomato/Early_blight``.
    """

    raw = original_label.strip()
    plant_raw = ""
    disease_raw = ""

    if "___" in raw:
        plant_raw, disease_raw = raw.split("___", 1)
    elif len(label_parts) >= 2:
        plant_raw, disease_raw = label_parts[-2], label_parts[-1]
    elif "__" in raw:
        plant_raw, disease_raw = raw.split("__", 1)
    elif plant_hint:
        plant_raw = plant_hint
        disease_raw = _disease_from_single_label(raw, plant_hint)
    else:
        plant_raw, disease_raw = _split_single_label(raw)

    if plant_hint and is_generic_plant_label(plant_raw):
        plant_raw = plant_hint

    plant = canonical_plant(plant_raw)
    disease_raw = remove_plant_prefix(disease_raw, plant)
    disease = canonical_disease(disease_raw)
    is_healthy = disease == "Healthy" or bool(HEALTHY_PATTERN.search(raw))

    if is_healthy:
        disease = "Healthy"

    return ParsedLabel(plant=plant, disease=disease, is_healthy=is_healthy)


def _disease_from_single_label(raw: str, plant_hint: str) -> str:
    clean = normalize_token(raw)
    if clean.lower() in {"healthy", "normal"}:
        return "Healthy"
    return remove_plant_prefix(clean, plant_hint)


def _split_single_label(raw: str) -> tuple[str, str]:
    clean = normalize_token(raw)
    if not clean:
        return "Unknown", "Unknown"

    tokens = clean.split()
    if len(tokens) == 1:
        if tokens[0].lower() in {"healthy", "normal"}:
            return "Unknown", "Healthy"
        return tokens[0], "Unknown"

    lower_tokens = [token.lower() for token in tokens]
    if "healthy" in lower_tokens:
        healthy_index = lower_tokens.index("healthy")
        plant = " ".join(tokens[:healthy_index]) or tokens[0]
        return plant, "Healthy"

    if "normal" in lower_tokens:
        normal_index = lower_tokens.index("normal")
        plant = " ".join(tokens[:normal_index]) or tokens[0]
        return plant, "Healthy"

    return tokens[0], " ".join(tokens[1:])
