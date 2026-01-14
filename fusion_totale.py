# %%
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OrdinalEncoder, OneHotEncoder, RobustScaler
from sklearn.pipeline import Pipeline
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split, StratifiedKFold, GridSearchCV
from sklearn.metrics import roc_auc_score, classification_report
# %%
extrait_eval=pd.read_csv('extrait_eval.csv') 
# %%
extrait_sirh=pd.read_csv('extrait_sirh.csv')
# %%
extrait_sondage=pd.read_csv('extrait_sondage.csv')

# %%
extrait_eval['eval_number'] = extrait_eval['eval_number'].str.replace('E_', '').astype(int)
# %%
extrait_sirh['id_employee'] = extrait_sirh['id_employee'].astype(int)
# %%
extrait_eval = extrait_eval.rename(columns={'eval_number': 'id_employee'})
# %%
fusion_eval_sirh = pd.merge(extrait_eval, extrait_sirh, on='id_employee')
# %%
extrait_sondage = extrait_sondage.rename(columns={'code_sondage': 'id_employee'})
# %%
fusion_totale = pd.merge(fusion_eval_sirh, extrait_sondage, on='id_employee')
# %%
fusion_totale.drop(columns=['annees_dans_le_poste_actuel','nombre_heures_travailless','annee_experience_totale','niveau_hierarchique_poste','nombre_employee_sous_responsabilite','annes_sous_responsable_actuel','ayant_enfants'], inplace=True)
# %%
print(fusion_totale.info())
# %%
features_new=['satisfaction_employee_environnement', 'note_evaluation_precedente', 'satisfaction_employee_nature_travail',
          'satisfaction_employee_equipe', 'satisfaction_employee_equilibre_pro_perso', 'id_employee', 'note_evaluation_actuelle',
          'heure_supplementaires', 'augementation_salaire_precedente', 'age', 'genre', 'revenu_mensuel', 'statut_marital', 'departement',
          'poste', 'nombre_experiences_precedentes', 'annees_dans_l_entreprise',
          'nombre_participation_pee', 'nb_formations_suivies', 'distance_domicile_travail', 'niveau_education', 'domaine_etude',
          'frequence_deplacement', 'annees_depuis_la_derniere_promotion']
# %%
fusion_totale["augementation_salaire_precedente"] = (
    fusion_totale["augementation_salaire_precedente"]
    .astype(str)
    .str.strip()
    .str.replace(" ", "", regex=False)
    .str.replace("\u00A0", "", regex=False)  # espace insécable
)
# %%
print(fusion_totale["augementation_salaire_precedente"].unique())
# %%
valeurs = set(fusion_totale["augementation_salaire_precedente"].unique())
# %%
attendues = set([
    "11%", "12%", "13%", "14%", "15%", "16%", "17%", "18%",
    "19%", "20%", "21%", "22%", "23%", "24%", "25%"
])
# %%
print("Valeurs inconnues :", valeurs - attendues)
# %%
y = fusion_totale["a_quitte_l_entreprise"]
# %%
mapping_cible = {"Non": 0, "Oui": 1}
# %%
y_encoded = y.map(mapping_cible)
# %%
X = fusion_totale.drop(columns=["a_quitte_l_entreprise", "id_employee"])
# %%
ordinal_categories = {
    "augementation_salaire_precedente": [
        "11%", "12%", "13%", "14%", "15%", "16%", "17%", "18%",
        "19%", "20%", "21%", "22%", "23%", "24%", "25%"
    ],
    "frequence_deplacement": ["Aucun", "Occasionnel", "Frequent"],
}
# %%
ordinal_cols = list(ordinal_categories.keys())
# %%
binary_cols = ["heure_supplementaires", "genre"]
# %%
nominal_cols = ["statut_marital", "departement", "poste", "domaine_etude"]
# %%
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
    "niveau_education",
    "annees_depuis_la_derniere_promotion",
]
# %%
expected_cols = set(ordinal_cols + binary_cols + nominal_cols + numeric_cols)
# %%
missing_in_X = expected_cols - set(X.columns)
# %%
extra_in_X = set(X.columns) - expected_cols
# %%
if missing_in_X:
    print("Colonnes attendues manquantes dans X :", missing_in_X)
# %%
if extra_in_X:
    print("Colonnes présentes dans X mais non utilisées :", extra_in_X)
# %%
preprocessor = ColumnTransformer(
    transformers=[
        (
            "ordinal_sal",
            OrdinalEncoder(
                categories=[ordinal_categories["augementation_salaire_precedente"]]
            ),
            ["augementation_salaire_precedente"],
        ),
        (
            "ordinal_freq",
            OrdinalEncoder(categories=[ordinal_categories["frequence_deplacement"]]),
            ["frequence_deplacement"],
        ),
        # On encode les binaires avec OrdinalEncoder (0,1 par exemple)
        ("binary", OrdinalEncoder(), binary_cols),
        # One-hot sur les nominales
        ("nominal", OneHotEncoder(drop="first", sparse_output=False), nominal_cols),
        # RobustScaler sur les numériques
        ("numeric", RobustScaler(), numeric_cols),
    ]
)
# %%
classifier = LogisticRegression(
    C=1.0,
    penalty="l2",
    solver="lbfgs",
    max_iter=1000,
    class_weight="balanced",
    n_jobs=-1,
)
# %%
pipeline = Pipeline(
    steps=[
        ("preprocess", preprocessor),
        ("classifier", classifier),
    ]
)
#
pipeline.fit(X, y_encoded)
# %%
df_final = fusion_totale.copy()
# %%
df_final['a_quitte_l_entreprise'] = y_encoded.values
# %%
df_final.to_csv('donnees_fusionnees.csv', index=False, encoding='utf-8')
# %%
print(" Fichier CSV créé avec les donoms des variables ORIGINALES")
print(f"Dimensions: {df_final.shape}")
print(f"\nColonnes: {df_final.columns.tolist()}")
print(df_final.info())
print("heure_supplementaires:", df_final["heure_supplementaires"].unique())
print("augementation_salaire_precedente:", df_final["augementation_salaire_precedente"].unique())
print("genre:", df_final["genre"].unique())
print("statut_marital:", df_final["statut_marital"].unique())
print("departement:", df_final["departement"].unique())
print("poste:", df_final["poste"].unique())
print("domaine_etude:", df_final["domaine_etude"].unique())
print("frequence_deplacement:", df_final["frequence_deplacement"].unique())
# %%
