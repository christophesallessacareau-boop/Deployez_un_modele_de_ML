# Test de robustesse de la vue fusionnee
# %%
from database import load_fused_data
from sqlalchemy import create_engine, text
import pandas as pd
import pytest

def test_load_fused_data_empty(monkeypatch):
    # fixture pytest monkeypatch pour modifier le comportement de la base de donnees
    # Mock engine remplaçant postgresql par un engine sqlite en mémoire, vide
    monkeypatch.setattr("database.engine", create_engine("sqlite:///:memory:"))

    with pytest.raises(Exception):
        load_fused_data() # leve une exception si la base fusionnee est vide

# %%
