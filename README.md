Application de Prédiction Machine Learning
Cette application utilise un modèle de régression logistique optimisé avec GridSearchCV pour faire des prédictions.
Fonctionnalités

Prédiction en temps réel
Interface interactive avec Gradio
Modèle entraîné avec pipeline complet (preprocessing + modèle)

Utilisation

Remplissez les champs avec les valeurs des features
Cliquez sur "Prédire"
Consultez les résultats et probabilités

Modèle

Algorithme : Régression Logistique avec GridSearchCV
Preprocessing : Pipeline avec ColumnTransformer (encoders + RobustScaler)
Métrique : ROC-AUC
Validation : StratifiedKFold Cross-Validation

Technologies

Python
Scikit-learn
Gradio
Joblib

 
 
