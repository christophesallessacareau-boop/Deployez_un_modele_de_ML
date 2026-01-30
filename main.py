# fichier api sans BD pour déploiement sur Hugging Face Spaces
from fastapi import FastAPI
from pydantic import BaseModel
from typing import Literal
import joblib
import pandas as pd

# Charger le modèle
model = joblib.load("model.joblib")

app = FastAPI(
    title="API RH - Modele ML",
    description="API FastAPI deployée sur Hugging Face Spaces",
    version="1.0.0"
)

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


@app.get("/")
def root():
    return {
        "status": "ok",
        "message": "API RH opérationnelle sur Hugging Face Spaces",
        "docs": "/docs"
    }


@app.post("/predict")
def predict(features: EmployeeFeatures):
    df = pd.DataFrame([features.model_dump()])
    prediction = int(model.predict(df)[0])
    return {
        "prediction": prediction,
        "details": "0 = l'employé reste, 1 = l'employé quitte"
    }
