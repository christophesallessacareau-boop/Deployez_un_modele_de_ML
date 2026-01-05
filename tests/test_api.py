# tests de l'API, utilisant les fixtures (client) definies dans conftest.py

# on teste un appel HTTP à la racine que l'API repond sans erreur (code 200)
# et retour attendu : status "ok"
def test_root(client):
    response = client.get("/")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


# test de robustesse sur la validation automatique des donnees d'entree par Pydantic
# on teste un appel HTTP POST à l'endpoint /predict (avec un corps JSON vide)
# erreur 422 retournees par Pydantic car les champs sont vides
def test_predict_missing_fields(client):
    response = client.post("/predict", json={})
    assert response.status_code == 422  


# test sur un employe inexistant (id 1999) renvoyant un message d'erreur
# simulation de la fonction pd.read_sql par monkeypatch
# renvoie un DataFrame vide pour cet ID inexistant
def test_predict_from_db_not_found(client, monkeypatch):
    
    # on accepte tout type de parametres pour que le mock fonctionne
    def mock_sql(*args, **kwargs):
        import pandas as pd
        return pd.DataFrame()

# on remplace pd.read_sql par mock_sql dans le fichier api.py
    monkeypatch.setattr("api.pd.read_sql", mock_sql)

# reponse avec cle error et message ecrit "introuvable"
    response = client.get("/predict/1999")
    assert response.status_code == 200 # l'API repond bien
    assert "introuvable" in response.json()["error"]
