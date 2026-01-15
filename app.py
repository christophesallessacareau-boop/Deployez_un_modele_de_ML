import gradio as gr
import joblib
import pandas as pd

# Charger le pipeline complet
model = joblib.load("model.joblib")

# -----------------------------
# Définition des colonnes EXACTES du DataFrame fusion_totale
# -----------------------------

numeric_cols = [
    "satisfaction_employee_environnement",
    "note_evaluation_precedente",
    "satisfaction_employee_nature_travail",
    "satisfaction_employee_equipe",
    "satisfaction_employee_equilibre_pro_perso",
    "note_evaluation_actuelle",
    "age",
    "revenu_mensuel",
    "nombre_experiences_precedentes",
    "annees_dans_l_entreprise",
    "nombre_participation_pee",
    "nb_formations_suivies",
    "distance_domicile_travail",
    "annees_depuis_la_derniere_promotion",
    "niveau_education"
]

binary_cols = ["heure_supplementaires", "genre"]

ordinal_cols = ["augementation_salaire_precedente", "frequence_deplacement"]

nominal_cols = [
    "statut_marital",
    "departement",
    "poste",
    "domaine_etude"
]

# Ordres pour les colonnes ordinales
augmentation_choices = [
    "11%", "12%", "13%", "14%", "15%", "16%", "17%", "18%",
    "19%", "20%", "21%", "22%", "23%", "24%", "25%"
]

frequence_choices = ["Aucun", "Occasionnel", "Frequent"]

heure_sup_choices = ["Non", "Oui"]
genre_choices = ["M", "F"]

# -----------------------------
# Fonction de prédiction
# -----------------------------
def predict(*values):
    all_features = numeric_cols + binary_cols + ordinal_cols + nominal_cols
    input_data = pd.DataFrame([dict(zip(all_features, values))])

    prediction = model.predict(input_data)[0]
    proba = model.predict_proba(input_data)[0]

    return {
        "Prediction (0=reste, 1=quitte)": int(prediction),
        "Probabilités": {
            "Rester (classe 0)": float(proba[0]),
            "Quitter (classe 1)": float(proba[1])
        }
    }

# -----------------------------
# Interface Gradio
# -----------------------------
with gr.Blocks(title="Prédiction RH - Modèle ML") as demo:
    gr.Markdown("## Interface de prédiction RH")
    gr.Markdown("Entrez les valeurs pour obtenir une prédiction")

    inputs = []

    # Champs numériques
    for col in numeric_cols:
        inputs.append(gr.Number(label=col, value=0))

    # Champs binaires
    inputs.append(gr.Radio(label="heure_supplementaires", choices=heure_sup_choices, value="Non"))
    inputs.append(gr.Radio(label="genre", choices=genre_choices, value="M"))

    # Champs ordinales
    inputs.append(gr.Dropdown(label="augementation_salaire_precedente", choices=augmentation_choices, value="11%"))
    inputs.append(gr.Dropdown(label="frequence_deplacement", choices=frequence_choices, value="Aucun"))

    # Champs nominales
    inputs.append(gr.Dropdown(label="statut_marital", choices=["Célibataire", "Marié(e)", "Divorcé(e)"], value="Célibataire"))
    inputs.append(gr.Dropdown(label="departement", choices=["Consulting", "Ressources Humaines", "Commercial"], value="Consulting"))
    inputs.append(gr.Dropdown(label="poste", choices=[
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
, value="Consultant"))
    inputs.append(gr.Dropdown(label="domaine_etude", choices=[
        "Infra & Cloud",
        "Autre",
        "Transformation Digitale",
        "Marketing",
        "Entrepreunariat",
        "Ressources Humaines",
    ]
, value="Marketing"))
    

    output = gr.JSON(label="Résultat")
    predict_btn = gr.Button("Prédire")

    predict_btn.click(fn=predict, inputs=inputs, outputs=output)

if __name__ == "__main__":
    demo.launch()
