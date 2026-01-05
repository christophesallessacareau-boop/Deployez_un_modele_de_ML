# tests/conftest.py
# briques de tests reutilisables (fixtures) pour tests sur l'API
# TestClient de FastAPI pour simuler des requêtes HTTP
# app est l'application FastAPI
import pytest
from fastapi.testclient import TestClient
import sys 
import os 
sys.path.append(os.path.dirname(os.path.dirname(__file__))) # ajouter le repertoire parent au chemin d'importation
from api import app

@pytest.fixture
def client():
    return TestClient(app)

