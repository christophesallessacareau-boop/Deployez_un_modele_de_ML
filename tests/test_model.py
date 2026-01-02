# Test du chargement du modèle et des prédictions
from model import SimpleModel
import pandas as pd
import pytest

def test_model_load():
    model = SimpleModel("model.joblib")
    assert model.model is not None

def test_predict_one_missing_employee(monkeypatch):
    model = SimpleModel("model.joblib")

    def mock_sql(*args, **kwargs):
        return pd.DataFrame()

    monkeypatch.setattr("model.pd.read_sql", mock_sql)

    with pytest.raises(ValueError):
        model.predict_one(999)
