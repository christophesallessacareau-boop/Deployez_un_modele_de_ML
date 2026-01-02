# tests/conftest.py
# briques de test réutilisables (fixtures)
import pytest
from fastapi.testclient import TestClient
from api import app

@pytest.fixture
def client():
    return TestClient(app)
