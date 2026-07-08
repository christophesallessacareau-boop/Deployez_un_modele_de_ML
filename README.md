---
title: Api Fastapi: prediction turnover de salariés
emoji: 🚀
colorFrom: green
colorTo: blue
sdk: docker
app_port: 7860
base_path: /docs
pinned: false
---



# Application de Prédiction Machine Learning      
Cette application utilise un modèle pour faire des prédictions.

# Modèle  
Algorithme : Régression Logistique avec GridSearchCV  
Preprocessing : Pipeline avec ColumnTransformer (encoders + RobustScaler)  
Métrique : ROC-AUC  
  
# Installation  
Pour récupérer le projet accessible sous  
https://github.com/christophesallessacareau-boop/Deployez_un_modele_de_ML  
depuis l'explorateur Windows, ouvrir la fenêtre Exécuter avec Win + R  
taper powershell  
puis utiliser la commande:  
git clone https://github.com/christophesallessacareau-boop/Deployez_un_modele_de_ML  
puis la commande :  
cd Deployez_un_modele_de_ML  

Créer un environnement virtuel sur Python 3.12:  
python -3.12 -m venv venv312  
Activer l'environnement:  
.\venv312\Scripts\Activate.ps1  
Installer les dépendances:  
pip install --upgrade pip  
pip install --prefer-binary -r requirements.txt  
  
  # Base de données
une base de données, sécurisée avec un mot de passe confidentiel, pour éviter toute manipilation externe.  
La base de données est crée manuellement sous Postgre SQL dans laquelle des tables vont êtres insérées:    
une table de données en entrée de modèle  
et une table pour la traçabilité des prédictions réalisées par l'utilisateur.

# Sources de données:
fichiers CSV (extrait_sirh.csv, extrait_eval.csv, extrait_sondage.csv) utilisés pour créer un fichier fusionné qui alimente une table de données dans une base de données.  
La table est crée avec SQLalchemy.

# Tests du code
Tests du code avec des tests unitaires et fonctionnels;  
à chaque push et pull request Git / GitHub;  
un environnement est crée à chaque test automatique;  
visibilité du bon fonctionnement du code avant déploiement;  
traçage des erreurs

# Fonctionnalités:
Prédiction en temps réel  
Interface interactive avec Fast API  
Modèle entraîné avec pipeline complet (preprocessing + modèle)

# Utilisation de l'API FastAPI:  
Utilisation en local seulement (sera présentée lors de la soutenance).  
Lancer l'API FastAPI: uvicorn api:app --reload   
Ou bien via http://127.0.0.1:8000  
Documentation Swagger : http://127.0.0.1:8000/docs  

N.B: l'API est disponible directement grâce à **Hugging Face Spaces**:  
https://christophesalles31-api-fastapi.hf.space/docs 
  
Remplissez les champs avec les valeurs des features  
Cliquez sur "Prédire"  
Consultez les résultats et probabilités de démission  
Ctrl+C pour arrêter l'application.  
  
  exemples de choix pour la prédiction:  
1) cas d'un employé avec une probabilité de quitter l'entreprise:  
{
  "satisfaction_employee_environnement": 0,
  "note_evaluation_precedente": 0,
  "satisfaction_employee_nature_travail": 0,
  "satisfaction_employee_equipe": 0,
  "satisfaction_employee_equilibre_pro_perso": 0,
  "note_evaluation_actuelle": 0,
  "heure_supplementaires": "Oui",
  "augementation_salaire_precedente": "11%",
  "age": 20,
  "genre": "F",
  "revenu_mensuel": 1000,
  "statut_marital": "Célibataire",
  "departement": "Commercial",
  "poste": "Cadre Commercial",
  "nombre_experiences_precedentes": 0,
  "annees_dans_l_entreprise": 0,
  "nombre_participation_pee": 0,
  "nb_formations_suivies": 0,
  "distance_domicile_travail": 0,
  "niveau_education": 0,
  "domaine_etude": "Infra & Cloud",
  "frequence_deplacement": "Occasionnel",
  "annees_depuis_la_derniere_promotion": 0
}  
  
2) cas d'un employé avec une probabilité de rester dans l'entreprise:  
{
  "satisfaction_employee_environnement": 3,
  "note_evaluation_precedente": 3,
  "satisfaction_employee_nature_travail": 3,
  "satisfaction_employee_equipe": 3,
  "satisfaction_employee_equilibre_pro_perso": 3,
  "note_evaluation_actuelle": 3,
  "heure_supplementaires": "Non",
  "augementation_salaire_precedente": "21%",
  "age": 60,
  "genre": "F",
  "revenu_mensuel": 10000,
  "statut_marital": "Célibataire",
  "departement": "Commercial",
  "poste": "Cadre Commercial",
  "nombre_experiences_precedentes": 0,
  "annees_dans_l_entreprise": 30,
  "nombre_participation_pee": 3,
  "nb_formations_suivies": 3,
  "distance_domicile_travail": 0,
  "niveau_education": 0,
  "domaine_etude": "Infra & Cloud",
  "frequence_deplacement": "Aucun",
  "annees_depuis_la_derniere_promotion": 0
}  

3) probabilité de partir/rester dans l'entreprise selon 2 exemples d' Id existants:  

ID=1, proba=1, il est considéré comme partant  

ID=2, proba=0, il est considéré comme restant  
  
# Traçabilité:
les prédictions sont loggées dans une table de données model_logs  
les entrées/sorties sont horodatées  
la base est PostgreSQL

# Gradio: une alternative à FastAPI
app.py contient une interface Gradio pour tester le modèle manuellement et obtenir une prédiction instantanée.  

Lancement de Gradio sur le cloud Hugging Face (ouvert à tous):  

cliquez sur https://huggingface.co/spaces/ChristopheSalles31/Deployez_un_modele_de_ML  
cliquez ensuite en haut à droite sur App  
indiquer les valeurs voulues pour chaque variable numérique  
et lorsque c'est le cas, choisissez une valeur dans le Menu déroulant pour les variables contraintes.  
Cliquez sur Prédire
Consultez les résultats et probabilités de démission:  
si proba=1, le salarié est considéré comme partant;  
si proba=0, le salarié est considéré comme restant.  

Gradio peut aussi être utilisée en tant qu'application locale avec:  
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

 
 
