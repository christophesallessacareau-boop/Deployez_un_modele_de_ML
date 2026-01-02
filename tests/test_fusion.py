# Test de la vue fusionnée
from fusion import load_fused_data
from sqlalchemy import create_engine, text
import pandas as pd
import pytest

def test_load_fused_data_empty(monkeypatch):
    # Mock engine pour renvoyer un DataFrame vide
    monkeypatch.setattr("fusion.engine", create_engine("sqlite:///:memory:"))

    with pytest.raises(Exception):
        load_fused_data()
