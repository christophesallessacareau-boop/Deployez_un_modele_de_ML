# Application de Prédiction Machine Learning      
Cette application utilise un modèle pour faire des prédictions.

# Modèle  
Algorithme : Régression Logistique avec GridSearchCV  
Preprocessing : Pipeline avec ColumnTransformer (encoders + RobustScaler)  
Métrique : ROC-AUC  
Validation : StratifiedKFold Cross-Validation  

# Installation  
Pour récupérer le projet accessible sous https://github.com/christophesallessacareau-boop/Deployez_un_modele_de_ML
depuis l'explorateur Windows, ouvrir la fençetre Exécuter avec Win + R
taper cmd (ou bien powershell)
puis utiliser la commande :
git clone https://github.com/christophesallessacareau-boop/Deployez_un_modele_de_ML
puis la commande :
cd Deployez_un_modele_de_ML

Créer un environnement virtuel sur Python 3.12:
py -3.12 -m venv venv312
Activer l'environnement:
.\venv312\Scripts\Activate.ps1
Installer les dépendances: pip install -r requirements.txt

# Base de données
une base de données, sécurisée avec un mot de passe confidential, crée manuellement sous Postgre SQL dans laquelle des tables vont êtres insérées.

# Sources de données:
fichiers CSV (extrait_sirh.csv, extrait_eval.csv, extrait_sondage.csv) utilisés pour créer un fichier fusionné qui alimente une table de données dans une base de données.
La table est crée avec SQLalchemy ici.

# Tests du code
Tests du code avec des tests unitaires et fonctionnels à chaque push et pull request Git / GitHub.

# Fonctionnalités:
Prédiction en temps réel
Interface interactive avec Fast API
Modèle entraîné avec pipeline complet (preprocessing + modèle)

# Utilisation:
Lancer l'API FastAPI: uvicorn app:app --reload
Ou bien via http://127.0.0.1:8000
Remplissez les champs avec les valeurs des features
Cliquez sur "Prédire"
Consultez les résultats et probabilités de démission
Ctrl+C pour arrêter l'application

# Traçabilité:
les prédictions sont loggées dans une table de données model_logs
les entrées/sorties sont horodatées
la base est PostgreSQL

# Gradio: en complément de FastAPI
app.py contient une interface Gradio optionnelle pour tester le modèle manuellement et obtenir une prédiction instantanée.
Option indépendante de l’API FastAPI et n’est pas utilisée dans le fonctionnement normal du projet.
Lancement de Gradio en application locale:
python app.py
ou bien http://127.0.0.1:7860


# Technologies:
Python
Scikit-learn
Joblib
FastAPI
PostgreSQL
SQLAlchemy
Gradio

 
 
