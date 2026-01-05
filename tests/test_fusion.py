# Test de robustesse de la vue fusionnee
from fusion import load_fused_data
from sqlalchemy import create_engine, text
import pandas as pd
import pytest

def test_load_fused_data_empty(monkeypatch):
    # Mock engine remplaçant postgresqlpour renvoyer un DataFrame vide
    # sqlite en memoire pour simuler une base sans tables
    monkeypatch.setattr("fusion.engine", create_engine("sqlite:///:memory:"))

    with pytest.raises(Exception):
        load_fused_data() # leve une exception si la base fusionnee est vide
