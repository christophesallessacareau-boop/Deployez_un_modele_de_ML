# Application Gradio (framework) 
import gradio as gr
import joblib
import pandas as pd
import numpy as np

# Charger le modèle
model = joblib.load('model.joblib')

# Chargement du preprocesseur normalement inutile car le pipeline s'en charge automatiquement
## (sinon) ColumnTransformer= joblib.load('preprocessor.joblib')

values = [
    satisfaction_employee_environnement, note_evaluation_precedente, satisfaction_employee_nature_travail,
          satisfaction_employee_equipe, satisfaction_employee_equilibre_pro_perso, id_employee, note_evaluation_actuelle,
          heure_supplementaires, augmentation_salaire_precedente, age, genre, revenu_mensuel, statut_marital, departement,
          poste, nombre_experiences_precedentes, annees_dans_l_entreprise,
          nombre_participation_pee, nb_formations_suivies, distance_domicile_travail, niveau_education, domaine_etude,
          frequence_deplacement, annees_depuis_la_derniere_promotion, categorie_revenu
]

def predict(values):
    """
    Fonction de prédiction
    
    """
    # Créer un DataFrame avec les features

    features = [
    'satisfaction_employee_environnement', 'note_evaluation_precedente', 'satisfaction_employee_nature_travail',
          'satisfaction_employee_equipe', 'satisfaction_employee_equilibre_pro_perso', 'id_employee', 'note_evaluation_actuelle',
          'heure_supplementaires', 'augementation_salaire_precedente', 'age', 'genre', 'revenu_mensuel', 'statut_marital', 'departement',
          'poste', 'nombre_experiences_precedentes', 'annees_dans_l_entreprise',
          'nombre_participation_pee', 'nb_formations_suivies', 'distance_domicile_travail', 'niveau_education', 'domaine_etude',
          'frequence_deplacement', 'annees_depuis_la_derniere_promotion', 'categorie_revenu'
]
    
    input_data = pd.DataFrame([dict(zip(features, values))])
    
    # Application du preprocessing (normalement inutile car le pipeline s'en charge automatiquement)
    ## (sinon) input_data = ColumnTransformer.transform(input_data)
    
    # Faire la prédiction
    prediction = model.predict(input_data)[1]
    
    # modèle de classification, obtention des probabilités
    if hasattr(model, 'predict_proba'):
        proba = model.predict_proba(input_data)[1]
        return {
            'Prédiction': str(prediction),
            'Probabilités': {f'Classe {i}': float(p) for i, p in enumerate(proba)}
        }
    
    return f"Prédiction: {prediction}"

# Interface Gradio
with gr.Blocks(title="Modèle de regression logistique - Prédiction") as demo:
    gr.Markdown(" Application de Prédiction de regression logistique")
    gr.Markdown("Entrez les valeurs des features pour obtenir une prédiction")
    
    with gr.Row():
        inputs = []
        with gr.Column():
        for feat in features:
        inputs.append(gr.Number(label=feat, value=0))
                   
            predict_btn = gr.Button("Prédire", variant="primary")
        
        with gr.Column():
            output = gr.JSON(label="Résultat")
    
        
    predict_btn.click(
        fn=predict,
        inputs = []
        with gr.Column():
            for feat in features:
            inputs.append(gr.Number(label=feat, value=0))
        outputs=output
    )

if __name__ == "__main__":
    demo.launch()