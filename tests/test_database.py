# tests/test_database.py
import os
import pytest
from sqlalchemy import create_engine, text
from sqlalchemy.pool import NullPool
from schema import SCHEMA_SQL


# pour ne pas toucher a la base principale, on cree une base test_db
# Ajout du client_encoding dans l'URL

TEST_DB_URL = os.getenv(
    "TEST_DB_URL",
    "postgresql://postgres:postgres@localhost:5432/test_db?client_encoding=utf8"
)


@pytest.fixture(scope="module")
def test_engine():
    """
    Fournit un moteur SQLAlchemy connecte a une base PostgreSQL dediee aux tests.
    """
    engine = create_engine(
        TEST_DB_URL,
        poolclass=NullPool,
        connect_args={
            'options': '-c client_encoding=utf8'
        },
        execution_options={
            "isolation_level": "AUTOCOMMIT"
        }
    )
    
    # Forcer l'encodage UTF-8 dès la connexion
    with engine.connect() as conn:
        conn.execute(text("SET client_encoding = 'UTF8';"))
        conn.commit()
    
    yield engine

    # Nettoyage
    with engine.connect() as conn:
        conn.execute(text("DROP SCHEMA public CASCADE; CREATE SCHEMA public;"))
        conn.commit()


def test_create_tables(test_engine):
    """
    Verifie que le SCHEMA_SQL peut etre execute sans erreur dans PostgreSQL.
    """
    with test_engine.connect() as conn:
        # Forcer UTF-8 pour cette session
        conn.execute(text("SET client_encoding = 'UTF8';"))
        conn.execute(text(SCHEMA_SQL))
        conn.commit()
    
