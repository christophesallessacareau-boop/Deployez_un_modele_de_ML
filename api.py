# Fichier : api.py pour FastAPI

import uvicorn
from fastapi import FastAPI
from pydantic import BaseModel, Field, ConfigDict
from typing import Literal
import joblib
import pandas as pd
from sqlalchemy import create_engine, text
import json
from database import DB_URL

# utilisation directe des credentials avec DB_URL
# Connexion PostgreSQL
engine = create_engine(DB_URL)

# Charger le modele ML
model = joblib.load("model.joblib")

app = FastAPI(
    title="API RH - Modele ML",
    description="API locale exposant un modele ML avec validation Pydantic et traçabilite PostgreSQL",
    version="1.0.0"
)

# -----------------------------
# 1. Modele Pydantic (validation)
# -----------------------------


class EmployeeFeatures(BaseModel):
    satisfaction_employee_environnement: int
    note_evaluation_precedente: int
    satisfaction_employee_nature_travail: int
    satisfaction_employee_equipe: int
    satisfaction_employee_equilibre_pro_perso: int

    note_evaluation_actuelle: int
    heure_supplementaires: Literal["Oui", "Non"]
    augementation_salaire_precedente: Literal[
        "11%", "12%", "13%", "14%", "15%", "16%", "17%", "18%", "19%",
        "20%", "21%", "22%", "23%", "24%", "25%"
    ]
    age: int
    genre: Literal["F", "M"]
    revenu_mensuel: int
    statut_marital: Literal["Célibataire", "Marié(e)", "Divorcé(e)"]
    departement: Literal["Commercial", "Consulting", "Ressources Humaines"]
    poste: Literal[
        "Cadre Commercial",
        "Assistant de Direction",
        "Consultant",
        "Tech Lead",
        "Manager",
        "Senior Manager",
        "Représentant Commercial",
        "Directeur Technique",
        "Ressources Humaines",
    ]
    nombre_experiences_precedentes: int
    annees_dans_l_entreprise: int
    nombre_participation_pee: int
    nb_formations_suivies: int
    distance_domicile_travail: int
    niveau_education: int
    domaine_etude: Literal[
        "Infra & Cloud",
        "Autre",
        "Transformation Digitale",
        "Marketing",
        "Entrepreunariat",
        "Ressources Humaines",
    ]
    frequence_deplacement: Literal["Occasionnel", "Frequent", "Aucun"]
    annees_depuis_la_derniere_promotion: int

    class Config:
        orm_mode = True


# -----------------------------
# 2. Endpoint racine
# -----------------------------
# avec message de bienvenue et lien vers la doc Swagger
@app.get("/")
def root():
    return {
        "status": "ok",
        "message": "API RH operationnelle en localhost",
        "docs": "http://127.0.0.1:8000/docs"
    }


# -----------------------------
# 3. Endpoint de prediction
# -----------------------------

@app.post("/predict")
def predict(features: EmployeeFeatures):

    # Convertir en DataFrame
    df = pd.DataFrame([features.dict()])
    

    # Prediction
    prediction = int(model.predict(df)[0])

    # Traçabilite : enregistre input/output
    with engine.connect() as conn:
        conn.execute(
            text("""
                INSERT INTO model_logs (id_employee, input_json, output_json)
                VALUES (:id_employee, :input_json, :output_json)
            """),
            {
                "id_employee": None,  # pas d'ID employe ici
                "input_json": json.dumps(features.dict()),
                "output_json": json.dumps({"prediction": prediction})
            }
        )
        conn.commit()

    return {
        "prediction": prediction,
        "details": "0 = l'employé reste, 1 = l'employé quitte"
    }


# -----------------------------
# 4. Endpoint prediction via ID employe (depuis PostgreSQL)
# -----------------------------
#l'utilisateur demande une prediction via un ID
@app.get("/predict/{employee_id}")
def predict_from_db(employee_id: int):

    query = text("""
        SELECT * FROM donnees_fusionnees
        WHERE id_employee = :employee_id
    """)
    
    df = pd.read_sql(query, engine, params={"employee_id": employee_id})

    if df.empty:
        return {"error": "Employe introuvable dans la base"}

    # Supprimer la cible + created_at (pour enlever les mgs d'erreur)
    X = df.drop(columns=["a_quitte_l_entreprise", "created_at"])
    prediction = int(model.predict(df)[0])


    # Traçabilite
    with engine.connect() as conn:
        conn.execute(
            text("""
                INSERT INTO model_logs (id_employee, input_json, output_json)
                VALUES (:id_employee, :input_json, :output_json)
            """),
            {
                "id_employee": employee_id,
                "input_json": json.dumps(X.to_dict(orient="records")[0]),
                "output_json": json.dumps({"prediction": int(prediction)})
            }
        )
        conn.commit()

    return {
        "employee_id": employee_id,
        "prediction": int(prediction)
    }
# Fin du fichier api.py