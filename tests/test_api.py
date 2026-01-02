# test de l'API
def test_root(client):
    response = client.get("/")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"

def test_predict_missing_fields(client):
    response = client.post("/predict", json={})
    assert response.status_code == 422  # validation Pydantic

def test_predict_from_db_not_found(client, monkeypatch):
    def mock_sql(*args, **kwargs):
        import pandas as pd
        return pd.DataFrame()

    monkeypatch.setattr("api.pd.read_sql", mock_sql)

    response = client.get("/predict/999")
    assert response.status_code == 200
    assert "introuvable" in response.json()["error"]
