# Application Gradio
import gradio as gr
import joblib
import pandas as pd
import numpy as np

# Charger le modèle
model = joblib.load('model.joblib')

# Chargement du preprocesseur 
ColumnTransformer= joblib.load('preprocessor.joblib')

values = [
    augementation_salaire_precedente, frequence_deplacement,
    heure_supplementaires, genre, statut_marital_Divorcé_e,
    statut_marital_Marié_e, departement_Consulting,
    departement_RH, poste_Cadre_Commercial, poste_Consultant,
    poste_Directeur_Technique, poste_Manager,
    poste_Representant_Commercial, poste_RH,
    poste_Senior_Manager, poste_Tech_Lead,
    domaine_etude_Entrepreunariat, domaine_etude_Infra_Cloud,
    domaine_etude_Marketing, domaine_etude_RH,
    domaine_etude_Transformation_Digitale,
    satisfaction_employee_environnement, note_evaluation_precedente,
    satisfaction_employee_nature_travail, satisfaction_employee_equipe,
    satisfaction_employee_equilibre_pro_perso, note_evaluation_actuelle,
    age, revenu_mensuel, nombre_experiences_precedentes,
    annees_dans_l_entreprise, nombre_participation_pee,
    nb_formations_suivies, distance_domicile_travail,
    niveau_education, annees_depuis_la_derniere_promotion
]

def predict(values):
    """
    Fonction de prédiction
    
    """
    # Créer un DataFrame avec les features

    features = [
    'augementation_salaire_precedente', 'frequence_deplacement',
    'heure_supplementaires', 'genre', 'statut_marital_Divorcé(e)',
    'statut_marital_Marié(e)', 'departement_Consulting',
    'departement_Ressources Humaines', 'poste_Cadre Commercial',
    'poste_Consultant', 'poste_Directeur Technique', 'poste_Manager',
    'poste_Représentant Commercial', 'poste_Ressources Humaines',
    'poste_Senior Manager', 'poste_Tech Lead',
    'domaine_etude_Entrepreunariat', 'domaine_etude_Infra & Cloud',
    'domaine_etude_Marketing', 'domaine_etude_Ressources Humaines',
    'domaine_etude_Transformation Digitale',
    'satisfaction_employee_environnement', 'note_evaluation_precedente',
    'satisfaction_employee_nature_travail', 'satisfaction_employee_equipe',
    'satisfaction_employee_equilibre_pro_perso', 'note_evaluation_actuelle',
    'age', 'revenu_mensuel', 'nombre_experiences_precedentes',
    'annees_dans_l_entreprise', 'nombre_participation_pee',
    'nb_formations_suivies', 'distance_domicile_travail',
    'niveau_education', 'annees_depuis_la_derniere_promotion'
]
    
    input_data = pd.DataFrame([dict(zip(features, values))])
    
    # Application du preprocessing
    input_data = ColumnTransformer.transform(input_data)
    
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