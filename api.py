# Fichier : api.py

from fastapi import FastAPI
from pydantic import BaseModel, Field
import joblib
import pandas as pd
from sqlalchemy import create_engine, text
import json
from config import DB_URL

# Connexion PostgreSQL
engine = create_engine(DB_URL)

# Charger le modèle ML
model = joblib.load("model.joblib")

app = FastAPI(
    title="API RH - Modèle ML",
    description="API locale exposant un modèle ML avec validation Pydantic et traçabilité PostgreSQL",
    version="1.0.0"
)

# -----------------------------
# 1. Modèle Pydantic (validation)
# -----------------------------

class EmployeeFeatures(BaseModel):
    augmentation_salaire_precedente: str
    frequence_deplacement: str
    heure_supplementaires: str
    genre: str
    statut_marital: str
    departement: str
    poste: str
    domaine_etude: str

    satisfaction_employee_environnement: int
    note_evaluation_precedente: int
    satisfaction_employee_nature_travail: int
    satisfaction_employee_equipe: int
    satisfaction_employee_equilibre_pro_perso: int
    note_evaluation_actuelle: int

    age: int
    revenu_mensuel: int
    nombre_experiences_precedentes: int
    annees_dans_l_entreprise: int
    annees_dans_le_poste_actuel: int
    nombre_participation_pee: int
    nb_formations_suivies: int
    distance_domicile_travail: int
    niveau_education: int
    annees_depuis_la_derniere_promotion: int


# -----------------------------
# 2. Endpoint racine
# -----------------------------
# avec message de bienvenue et lien vers la doc Swagger
@app.get("/")
def root():
    return {
        "status": "ok",
        "message": "API RH opérationnelle en localhost",
        "docs": "http://127.0.0.1:8000/docs"
    }


# -----------------------------
# 3. Endpoint de prédiction
# -----------------------------

@app.post("/predict")
def predict(features: EmployeeFeatures):

    # Convertir en DataFrame
    df = pd.DataFrame([features.dict()])

    # Prédiction
    prediction = model.predict(df)[0]

    # Traçabilité : enregistrer input/output
    with engine.connect() as conn:
        conn.execute(
            text("""
                INSERT INTO model_logs (id_employee, input_json, output_json)
                VALUES (:id_employee, :input_json, :output_json)
            """),
            {
                "id_employee": None,  # pas d'ID employé ici
                "input_json": json.dumps(features.dict()),
                "output_json": json.dumps({"prediction": prediction})
            }
        )
        conn.commit()

    return {
        "prediction": prediction,
        "details": "Prédiction effectuée avec succès"
    }


# -----------------------------
# 4. Endpoint prédiction via ID employé (depuis PostgreSQL)
# -----------------------------

@app.get("/predict/{employee_id}")
def predict_from_db(employee_id: int):

    query = f"""
        SELECT * FROM donnees_fusionnees
        WHERE id_employee = {employee_id}
    """

    df = pd.read_sql(query, engine)

    if df.empty:
        return {"error": "Employé introuvable dans la base"}

    X = df.drop(columns=["a_quitte_l_entreprise"])
    prediction = model.predict(X)[0]

    # Traçabilité
    with engine.connect() as conn:
        conn.execute(
            text("""
                INSERT INTO model_logs (id_employee, input_json, output_json)
                VALUES (:id_employee, :input_json, :output_json)
            """),
            {
                "id_employee": employee_id,
                "input_json": json.dumps(X.to_dict()),
                "output_json": json.dumps({"prediction": prediction})
            }
        )
        conn.commit()

    return {
        "employee_id": employee_id,
        "prediction": prediction
    }
# Fin du fichier api.py