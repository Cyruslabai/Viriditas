from viriditas.evaluation import Evaluator


def test_evaluator_run_minimal():
    ev = Evaluator()
    df = ev.run()
    assert hasattr(df, 'shape')
    assert df.shape[0] >= 0
