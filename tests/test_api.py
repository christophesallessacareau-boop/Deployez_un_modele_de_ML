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


# test sur un employe inexistant (id 3000) renvoyant un message d'erreur
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
    response = client.get("/predict/3000")
    assert response.status_code == 200 # l'API repond bien
    assert "introuvable" in response.json()["error"]

# Test sur endpoint predict avec données valides
def test_predict_success(client, monkeypatch):

    # ---------- mock du modele ML ----------
    class MockModel:
        def predict(self, df):
            return [0]

    monkeypatch.setattr("api.model", MockModel())

    # ---------- mock de la connexion DB ----------
    class DummyConnection:
        def execute(self, *args, **kwargs):
            pass
        def commit(self):
            pass
        def __enter__(self):
            return self
        def __exit__(self, exc_type, exc, tb):
            pass

    class DummyEngine:
        def connect(self):
            return DummyConnection()

    monkeypatch.setattr("api.engine", DummyEngine())

    # ---------- payload valide ----------
    payload = {
        "satisfaction_employee_environnement": 3,
        "note_evaluation_precedente": 3,
        "satisfaction_employee_nature_travail": 3,
        "satisfaction_employee_equipe": 3,
        "satisfaction_employee_equilibre_pro_perso": 3,
        "note_evaluation_actuelle": 3,
        "heure_supplementaires": "Non",
        "augementation_salaire_precedente": "15%",
        "age": 35,
        "genre": "M",
        "revenu_mensuel": 4000,
        "statut_marital": "Marié(e)",
        "departement": "Commercial",
        "poste": "Manager",
        "nombre_experiences_precedentes": 2,
        "annees_dans_l_entreprise": 5,
        "nombre_participation_pee": 1,
        "nb_formations_suivies": 2,
        "distance_domicile_travail": 10,
        "niveau_education": 3,
        "domaine_etude": "Marketing",
        "frequence_deplacement": "Occasionnel",
        "annees_depuis_la_derniere_promotion": 2
    }

    response = client.post("/predict", json=payload)

    assert response.status_code == 200
    assert response.json()["prediction"] == 0

