# Test du chargement du modele et des predictions
from model import SimpleModel
import pandas as pd
import pytest



# test que le modele entraine existe et peut être charge
def test_model_load():
    model = SimpleModel("model.joblib")
    assert model.model is not None



# test pour un employe inexistant et levee d'une erreur
def test_predict_one_missing_employee(monkeypatch):
    
    # chargement du modele entraine
    model = SimpleModel("model.joblib")

# mock de la fonction pd.read_sql pour retourner un DataFrame vide
    def mock_sql(*args, **kwargs):
        return pd.DataFrame()
    
# appliquer le mock à la place du vrai modele
    monkeypatch.setattr("model.pd.read_sql", mock_sql)

# exception attendue pour un employe inexistant (1999)
    with pytest.raises(ValueError):
        model.predict_one(1999)
