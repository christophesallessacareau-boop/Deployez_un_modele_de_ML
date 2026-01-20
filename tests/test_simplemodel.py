# test unitaire 
# test d'une prediction (N° de l'ID) quand tout est prêt

import pandas as pd
import pytest
from unittest.mock import MagicMock, patch
from model import SimpleModel


@patch("model.engine")  # Mock l'engine importé depuis database
@patch("model.joblib.load")
def test_predict_one_ok(mock_load, mock_engine):
    # faux modèle ML
    fake_model = MagicMock()
    fake_model.predict.return_value = [1] # prediction attendue tjs egale a 1
    mock_load.return_value = fake_model

    # Mock de la connexion et du résultat SQL
    mock_connection = MagicMock()
    mock_engine.connect.return_value.__enter__.return_value = mock_connection

    # Mock pd.read_sql pour retourner de fausses données
    with patch("model.pd.read_sql") as mock_read_sql:
        mock_read_sql.return_value = pd.DataFrame({
            "id_employee": [3000],
            "age": [30],
            "revenu_mensuel": [50000],
            "a_quitte_l_entreprise": [0]
        })

        model = SimpleModel("fake_model.joblib")
        prediction = model.predict_one(3000)

        assert prediction == 1
        
        # on vérifie que log_prediction a été appelé
        mock_connection.execute.assert_called_once()
        mock_connection.commit.assert_called_once()
