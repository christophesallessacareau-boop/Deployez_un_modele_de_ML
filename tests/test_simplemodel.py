# test unitaire 
# test d'une prediction (N° de l'ID) quand tout est prêt

import pandas as pd
import pytest
from unittest.mock import MagicMock, patch
from model import SimpleModel


@patch("model.joblib.load")
@patch("model.pd.read_sql")
def test_predict_one_ok(mock_read_sql, mock_load):
    # faux modèle ML
    fake_model = MagicMock()
    fake_model.predict.return_value = [1] # prediction attendue tjs egale a 1
    mock_load.return_value = fake_model

    # fausses données SQL
    mock_read_sql.return_value = pd.DataFrame({
        "id_employee": [3000],
        "age": [30],
        "revenu_mensuel": [50000],
        "a_quitte_l_entreprise": [0]
    })

    model = SimpleModel("fake_model.joblib")
    prediction = model.predict_one(1)

    assert prediction == 1
