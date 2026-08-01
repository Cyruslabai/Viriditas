import numpy as np
import pandas as pd
from viriditas.evaluation import reports


def test_topk_handling_for_small_classes():
    # craft minimal probs for single-class
    probs = np.array([[1.0]])
    test_df = pd.DataFrame({
        'image_path': ['data/images/img1.jpg'],
        'task_plant_label': ['species_a'],
        'split': ['test'],
        'plant': ['species_a'],
    })
    class_names = ['species_a']
    df = reports.save_prediction_results(test_df, probs, class_names, output_dir=None)
    assert 'top1' in df.columns
    assert 'top2' in df.columns
    assert 'top3' in df.columns
    assert df.loc[0, 'top2'] is None or pd.isna(df.loc[0, 'top2'])
