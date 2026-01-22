# tests
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


@pytest.fixture(scope="module") # module pour creer la base une fois par module de tests
def test_engine():
    """
    Fournit un moteur SQLAlchemy connecte a une base PostgreSQL dediee aux tests.
    Chaque test ouvre/ferme une connexion
    """
    engine = create_engine(
        TEST_DB_URL,
        poolclass=NullPool, # connexion ouverte/fermee a chaque fois
        connect_args={
            'options': '-c client_encoding=utf8'
        },
        execution_options={
            "isolation_level": "AUTOCOMMIT" # pas de transaction ouverte
        }
    )
    
    # Forcer l'encodage UTF-8 dès la connexion
    with engine.connect() as conn:
        conn.execute(text("SET client_encoding = 'UTF8';"))
        conn.commit()
    
    yield engine # fournir le moteur aux tests puis fin du setup

    # Nettoyage de la base de test apres les tests (reset; teardown automatique)
    with engine.connect() as conn:
        conn.execute(text("DROP SCHEMA public CASCADE; CREATE SCHEMA public;"))
        conn.commit()

#  LES TESTS 
def test_connexion_database(test_engine):
    """
    Vérifie que la connexion à la base de données fonctionne
    """
    with test_engine.connect() as conn:
        result = conn.execute(text("SELECT 1"))
        assert result.scalar() == 1


def test_creation_schema(test_engine):
    """
    Vérifie que le schéma SQL peut être créé sans erreur
    """
    with test_engine.connect() as conn:
        conn.execute(text(SCHEMA_SQL))
        conn.commit()
        
        result = conn.execute(text(
            "SELECT table_name FROM information_schema.tables WHERE table_schema = 'public'"
        ))
        tables = [row[0] for row in result]
        assert len(tables) > 0


    
