# Test de la création des tables et erreurs SQL
from database import create_tables
from schema import SCHEMA_SQL
from sqlalchemy import create_engine, text
import pytest

def test_create_tables():
    engine = create_engine("sqlite:///:memory:")  # DB temporaire
    try:
        with engine.connect() as conn:
            conn.execute(text(SCHEMA_SQL))
    except Exception as e:
        pytest.fail(f"Erreur lors de la création des tables : {e}")
