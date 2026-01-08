# module optionnel
# framework de Gradio, interface web pour tester le modele

import gradio as gr
import joblib
import pandas as pd

# Charge le modele entraîne du projet precedent
model = joblib.load('model.joblib')

# Liste des features
# pour chaque variable, Gradio cree un champ d'entree
features = ['augementation_salaire_precedente', 'frequence_deplacement',
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
       'niveau_education', 'annees_depuis_la_derniere_promotion']

# Fonction de prediction
# on recupere les valeurs saisies dans Gradio sous forme d'un tuple
# association de ces valeurs aux noms des features
# on cree un DataFrame pandas avec ces valeurs
def predict(*values):
    input_data = pd.DataFrame([dict(zip(features, values))])
    prediction = model.predict(input_data)[0]
    
    # Définir le libellé selon la prédiction
    label_prediction = "probabilité de rester" if prediction == 0 else "probabilité de démissionner"

    if hasattr(model, 'predict_proba'):
        proba = model.predict_proba(input_data)[0]
        return {
            'Prediction': str(prediction),
            'Probabilites': {f'Classe {i}': float(p) for i, p in enumerate(proba)}
        } # retourne la prediction et les probabilites

    return {
        'Prediction': str(prediction),
        'Interpretation': label_prediction
    }

# Interface Gradio
with gr.Blocks(title="Modele de regression logistique - Prediction") as demo:
    gr.Markdown("## Application de Prediction")
    gr.Markdown("Entrez les valeurs des features pour obtenir une prediction")
    
    # Creation des champs d'entree pour chaque feature
    # affichage d'un dictionnaire json en sortie
    inputs = [gr.Number(label=feat, value=0) for feat in features]
    output = gr.JSON(label="Resultat")
    predict_btn = gr.Button("Predire")

    # input recupere puis lie le bouton à la fonction de prediction
    predict_btn.click(fn=predict, inputs=inputs, outputs=output)

# Lancement de l'application en local dans le navigateur
if __name__ == "__main__":
    demo.launch()

