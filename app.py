#framework de Gradio, interface webvpour tester le modèle

import gradio as gr
import joblib
import pandas as pd

# Charge le modèle entraîné du projet précédent
model = joblib.load('model.joblib')

# Liste des features
# pour chaque variable, Gradio crée un champ d'entrée
features = [
    'satisfaction_employee_environnement', 'note_evaluation_precedente', 'satisfaction_employee_nature_travail',
    'satisfaction_employee_equipe', 'satisfaction_employee_equilibre_pro_perso', 'id_employee', 'note_evaluation_actuelle',
    'heure_supplementaires', 'augmentation_salaire_precedente', 'age', 'genre', 'revenu_mensuel', 'statut_marital', 'departement',
    'poste', 'nombre_experiences_precedentes', 'annees_dans_l_entreprise', 'nombre_participation_pee',
    'nb_formations_suivies', 'distance_domicile_travail', 'niveau_education', 'domaine_etude',
    'frequence_deplacement', 'annees_depuis_la_derniere_promotion', 'categorie_revenu'
]

# Fonction de prédiction
# on récupère les valeurs saisies dans Gradio sous forme d'un tuple
# association de ces valeurs aux noms des features
# on crée un DataFrame pandas avec ces valeurs
def predict(*values):
    input_data = pd.DataFrame([dict(zip(features, values))])
    prediction = model.predict(input_data)[0]

    if hasattr(model, 'predict_proba'):
        proba = model.predict_proba(input_data)[0]
        return {
            'Prédiction': str(prediction),
            'Probabilités': {f'Classe {i}': float(p) for i, p in enumerate(proba)}
        } # retourne la prédiction et les probabilités

    return f"Prédiction: {prediction}"

# Interface Gradio
with gr.Blocks(title="Modèle de régression logistique - Prédiction") as demo:
    gr.Markdown("## Application de Prédiction")
    gr.Markdown("Entrez les valeurs des features pour obtenir une prédiction")
    
    # Création des champs d'entrée pour chaque feature
    # affichage d'un dictionnaire json en sortie
    inputs = [gr.Number(label=feat, value=0) for feat in features]
    output = gr.JSON(label="Résultat")
    predict_btn = gr.Button("Prédire")

    # input récupérer puis lie le bouton à la fonction de prédiction
    predict_btn.click(fn=predict, inputs=inputs, outputs=output)

# Lancement de l'application en local dans le navigateur
if __name__ == "__main__":
    demo.launch()

