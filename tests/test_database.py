# tests/test_database.py
import os
from dotenv import load_dotenv
import pytest
from sqlalchemy import create_engine, text
from sqlalchemy.pool import NullPool
from schema import SCHEMA_SQL


# pour ne pas toucher a la base principale, on cree une base test_db
load_dotenv()

TEST_DB_USER = os.getenv("TEST_DB_USER") 
TEST_DB_PASSWORD = os.getenv("TEST_DB_PASSWORD") 
TEST_DB_HOST = os.getenv("TEST_DB_HOST", "localhost") 
TEST_DB_PORT = os.getenv("TEST_DB_PORT", "5432") 
TEST_DB_NAME = os.getenv("TEST_DB_NAME", "test_db")

TEST_DB_URL = ( f"postgresql://{TEST_DB_USER}:{TEST_DB_PASSWORD}" f"@{TEST_DB_HOST}:{TEST_DB_PORT}/{TEST_DB_NAME}" )


@pytest.fixture(scope="module")
def test_engine():
    """
    Fournit un moteur SQLAlchemy connecte a une base PostgreSQL dediee aux tests.
    Chaque test ouvre/ferme une connexion
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

    # Nettoyage de la base de test apres les tests
    with engine.connect() as conn:
        conn.execute(text("DROP SCHEMA public CASCADE; CREATE SCHEMA public;"))
        conn.commit()



    
