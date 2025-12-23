"""
API FastAPI de prédiction de démissions avec traçabilité PostgreSQL
Fichier: src/app/main.py
"""

from fastapi import FastAPI, Request
from pydantic import BaseModel
import joblib
import pandas as pd
import sys
from pathlib import Path
from datetime import datetime
import json

# Ajoute le dossier src au path pour importer le module database
sys.path.insert(0, str(Path(__file__).parent.parent))

from database import DatabaseManager

# ==========================================
# CONFIGURATION
# ==========================================

# Charger le modèle ML
model = joblib.load('model.joblib')

# Initialiser le gestionnaire de base de données
db_manager = DatabaseManager()

# Création de l'application FastAPI
app = FastAPI(
    title="API de Prédiction de démissions", 
    description="Une API pour prédire la démission d'un employé avec traçabilité complète."
)


# ==========================================
# MODÈLES DE DONNÉES
# ==========================================

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


# ==========================================
# ENDPOINTS
# ==========================================

@app.get("/")
def root():
    """Endpoint racine"""
    return {
        "message": "Bienvenue sur l'API de prédiction de démissions!",
        "version": "2.0",
        "endpoints": {
            "/predict": "POST - Faire une prédiction",
            "/health": "GET - Vérifier l'état de l'API",
            "/stats": "GET - Statistiques des prédictions"
        }
    }


@app.get("/health")
def health_check():
    """Vérification de l'état de l'API et de la base de données"""
    try:
        # Test de connexion à la base
        db_manager.execute_query("SELECT 1")
        db_status = "connected"
    except Exception as e:
        db_status = f"error: {str(e)}"
    
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "model_loaded": model is not None,
        "database_status": db_status
    }


@app.post("/predict")
def get_prediction(data: RequestData, request: Request):
    """
    Endpoint de prédiction avec traçabilité complète
    
    Args:
        data: Données de l'employé pour la prédiction
        request: Objet Request FastAPI (pour récupérer l'IP)
    
    Returns:
        Résultat de la prédiction avec probabilités
    """
    
    start_time = datetime.now()
    
    try:
        # Conversion des données en dictionnaire
        data_dict = data.model_dump()
        
        # ==========================================
        # PRÉDICTION
        # ==========================================
        
        # Créer un DataFrame avec les données
        input_data = pd.DataFrame([data_dict])
        
        # Faire la prédiction
        prediction = model.predict(input_data)[0]
        proba = model.predict_proba(input_data)[0]
        
        # Résultat structuré
        result = {
            "prediction": int(prediction),
            "resultat": "Démission probable" if prediction == 1 else "Pas de démission",
            "probabilite_demission": float(proba[1]),
            "probabilite_rester": float(proba[0]),
            "timestamp": datetime.now().isoformat()
        }
        
        # ==========================================
        # TRAÇABILITÉ - LOG DE LA PRÉDICTION
        # ==========================================
        
        execution_time = (datetime.now() - start_time).total_seconds() * 1000
        
        # Récupération de l'IP du client
        client_ip = request.client.host if request.client else "unknown"
        
        # Log dans la table model_prediction_logs
        db_manager.log_model_prediction(
            model_name='demission_predictor',
            model_version='1.0',  # Adaptez selon votre versioning
            input_features=data_dict,
            prediction=result,
            confidence_score=float(proba[1]),
            execution_time_ms=execution_time,
            user_id=client_ip  # Utilisez l'IP comme identifiant temporaire
        )
        
        # Log dans la table api_interaction_logs
        db_manager.log_api_interaction(
            endpoint='/predict',
            input_data=data_dict,
            output_data=result,
            model_version='1.0',
            user_id=client_ip,
            success=True,
            execution_time_ms=execution_time
        )
        
        return result
        
    except Exception as e:
        # Log de l'erreur
        execution_time = (datetime.now() - start_time).total_seconds() * 1000
        client_ip = request.client.host if request.client else "unknown"
        
        error_result = {
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }
        
        db_manager.log_api_interaction(
            endpoint='/predict',
            input_data=data.model_dump() if data else {},
            output_data=error_result,
            model_version='1.0',
            user_id=client_ip,
            success=False,
            execution_time_ms=execution_time
        )
        
        return {"error": str(e)}


@app.get("/stats")
def get_statistics():
    """
    Récupère des statistiques sur les prédictions effectuées
    
    Returns:
        Statistiques agrégées des prédictions
    """
    
    try:
        # Statistiques des prédictions
        query_predictions = """
        SELECT 
            COUNT(*) as total_predictions,
            AVG(confidence_score) as avg_confidence,
            MIN(timestamp) as first_prediction,
            MAX(timestamp) as last_prediction
        FROM model_prediction_logs
        WHERE model_name = 'demission_predictor'
        """
        
        df_stats = db_manager.execute_query(query_predictions)
        
        # Distribution des prédictions
        query_distribution = """
        SELECT 
            prediction->>'prediction' as prediction_class,
            COUNT(*) as count
        FROM model_prediction_logs
        WHERE model_name = 'demission_predictor'
        GROUP BY prediction->>'prediction'
        """
        
        df_distribution = db_manager.execute_query(query_distribution)
        
        # Dernières prédictions
        query_recent = """
        SELECT 
            timestamp,
            prediction->>'resultat' as resultat,
            confidence_score,
            execution_time_ms
        FROM model_prediction_logs
        WHERE model_name = 'demission_predictor'
        ORDER BY timestamp DESC
        LIMIT 10
        """
        
        df_recent = db_manager.execute_query(query_recent)
        
        return {
            "statistics": df_stats.to_dict(orient='records')[0] if len(df_stats) > 0 else {},
            "distribution": df_distribution.to_dict(orient='records'),
            "recent_predictions": df_recent.to_dict(orient='records')
        }
        
    except Exception as e:
        return {
            "error": str(e),
            "message": "Impossible de récupérer les statistiques. Vérifiez que la base de données est configurée."
        }


@app.get("/logs/api")
def get_api_logs(limit: int = 20):
    """
    Récupère les derniers logs d'interaction avec l'API
    
    Args:
        limit: Nombre de logs à récupérer (défaut: 20)
    
    Returns:
        Liste des dernières interactions API
    """
    
    try:
        logs = db_manager.get_api_logs(limit=limit)
        return {
            "logs": logs.to_dict(orient='records'),
            "count": len(logs)
        }
    except Exception as e:
        return {"error": str(e)}


@app.get("/logs/operations")
def get_operation_logs(limit: int = 20):
    """
    Récupère les derniers logs d'opérations sur la base
    
    Args:
        limit: Nombre de logs à récupérer (défaut: 20)
    
    Returns:
        Liste des dernières opérations
    """
    
    try:
        logs = db_manager.get_operation_logs(limit=limit)
        return {
            "logs": logs.to_dict(orient='records'),
            "count": len(logs)
        }
    except Exception as e:
        return {"error": str(e)}


