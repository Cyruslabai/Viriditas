import numpy as np
from pathlib import Path

from viriditas.inference import PlantPredictor
from viriditas.inference import loader


def test_predict_single(sample_image):
    p = PlantPredictor()
    res = p.predict(str(sample_image))
    assert isinstance(res, dict)
    assert 'predicted_label' in res
    assert 'confidence' in res
    assert 'probabilities' in res


def test_predict_batch(sample_image):
    p = PlantPredictor()
    res = p.predict_batch([str(sample_image), str(sample_image)])
    assert isinstance(res, list)
    assert len(res) == 2
    for r in res:
        assert 'predicted_label' in r
        assert 'probabilities' in r
