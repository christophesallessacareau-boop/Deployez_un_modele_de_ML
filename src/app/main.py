from fastapi import FastAPI
from pydantic import BaseModel
import joblib
import pandas as pd

# Charger le modèle
model = joblib.load('model.joblib')

# Création de l'application FastAPI
app = FastAPI(
    title="API de Prédiction de démissions", 
    description="Une API pour prédire la démission d'un employé à l'aide d'un modèle ML."
)

@app.get("/")
def root():
    return {"message": "Bienvenue sur l'API de prédiction!"}

# Modèle de données pour la requête
class RequestData(BaseModel):
    augmentation_salaire_precedente: str  
    frequence_deplacement: str
    heure_supplementaires: str
    genre: str
    statut_marital_Divorcé_e: str
    departement: str
    poste: str
    domaine: str
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

# Fonction de prédiction 
def predict(data_dict):
    """Fonction de prédiction du modèle"""
    # Créer un DataFrame avec les données
    input_data = pd.DataFrame([data_dict])
    
    # Faire la prédiction
    prediction = model.predict(input_data)[0]
    proba = model.predict_proba(input_data)[0]
    
    return {
        "prediction": int(prediction),
        "resultat": "Démission probable" if prediction == 1 else "Pas de démission",
        "probabilite_demission": float(proba[1]),
        "probabilite_rester": float(proba[0])
    }

# Endpoint de prédiction
@app.post("/predict")
def get_prediction(data: RequestData):
    try:
        # Utiliser model_dump() pour Pydantic v2
        result = predict(data.model_dump())
        return result
    except Exception as e:
        return {"error": str(e)}