# %%
import pandas as pd # import de la librairie pandas pour visualier et travailler les dataframes
import numpy as np #import de numpy pour les calculs simples
import matplotlib.pyplot as plt #import de matplotlib pour visualiser graphiques, courbes
import seaborn as sns #import de seaborn pour graphiques
import scipy.stats as st #import de scipy pour les statistiques et statistiques descriptives
import shap

# %%
#Selection
from sklearn.model_selection import (
    train_test_split,
    GridSearchCV, 
    cross_validate,StratifiedKFold,
)
from sklearn.metrics import mean_squared_error, r2_score, mean_absolute_error, accuracy_score, classification_report, confusion_matrix, precision_score, recall_score, roc_curve, auc, roc_auc_score, precision_recall_curve, average_precision_score
from sklearn.inspection import permutation_importance

#Preprocess
from sklearn.impute import SimpleImputer
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import LabelEncoder, OneHotEncoder, StandardScaler, OrdinalEncoder, RobustScaler

#Modèles
from sklearn.dummy import DummyRegressor, DummyClassifier
from sklearn.linear_model import LinearRegression, LogisticRegression
from sklearn.svm import SVR
from sklearn.ensemble import RandomForestRegressor, RandomForestClassifier
from imblearn.over_sampling import SMOTE
from imblearn.under_sampling import RandomUnderSampler
from imblearn.combine import SMOTETomek, SMOTEENN
from imblearn.pipeline import Pipeline as ImbPipeline
from shap import TreeExplainer


# %%
extrait_eval=pd.read_csv('extrait_eval.csv') 

# %%
extrait_sirh=pd.read_csv('extrait_sirh.csv') 

# %%
extrait_sondage=pd.read_csv('extrait_sondage.csv') 

# %%
extrait_eval.head()

# %%
extrait_sirh.head()

# %%
extrait_sondage.head()

# %%
extrait_eval.info()

# %%
#visualisation des valeurs manquantes(pas de valeurs manquantes car on a 1470 échantillons pour 1470 non-null counts)
extrait_eval.isnull().sum();

# %%
# recherche des doublons: False sur l'ensemble du dataframe =>pas de doublons
extrait_eval.duplicated().value_counts()

# %%
# verification des valeurs prises par la colonne
extrait_eval['satisfaction_employee_environnement'].describe()

# %%
extrait_eval['note_evaluation_precedente'].describe();

# %%
extrait_eval['niveau_hierarchique_poste'].describe();

# %%
extrait_eval['satisfaction_employee_nature_travail'].describe();

# %%
extrait_eval['satisfaction_employee_equipe'].describe();

# %%
extrait_eval['satisfaction_employee_equilibre_pro_perso'].describe();

# %%
# eval_number, id_employe et code_sondage semblent être la clé pour fusionner extrait_val, extrait_sirh et extrait_sondage
extrait_eval['eval_number'].value_counts()

# %%
extrait_eval['note_evaluation_actuelle'].describe();

# %%
extrait_eval['heure_supplementaires'].describe();

# %%
extrait_eval['augementation_salaire_precedente'].describe();

# %%
extrait_sirh.info()

# %%
#visualisation des valeurs manquantes(a priori pas de valeurs manquantes car on a 1470 échantillons pour 1470 non-null counts)
extrait_sirh.isnull().sum();

# %%
# recherche des doublons: False sur l'ensemble du dataframe=>pas de doublons
extrait_sirh.duplicated().value_counts()

# %%
# eval_number, id_employe et code_sondage semblent être la clé pour fusionner extrait_val, extrait_sirh et extrait_sondage
extrait_sirh['id_employee'].value_counts

# %%
# les valeurs de la variable age sont conformes
extrait_sirh['age'].value_counts();

# %%
#valeur de la variable age (en boxplot); la mediane 
plt.figure(figsize=(20, 6))
sns.boxplot(data=extrait_sirh, x='age')
plt.title('age')
plt.show()

# %%
extrait_sirh['genre'].value_counts();

# %%
extrait_sirh['revenu_mensuel'].describe();

# %%
#valeur de la variable revenu mensuel (en boxplot)
plt.figure(figsize=(20, 6))
sns.boxplot(data=extrait_sirh, x='revenu_mensuel')
plt.title('revenu_mensuel')
plt.show()

# %%
# on voit bien sur la boxplot que la moyenne est supérieure à la médiane en raison des salaires élevés ; les valeurs sont plausibles


# %%
extrait_sirh['statut_marital'].describe();

# %%
extrait_sirh['departement'].describe();

# %%
extrait_sirh['poste'].describe();

# %%
extrait_sirh['annee_experience_totale'].unique()

# %%
extrait_sirh['nombre_experiences_precedentes'].describe();

# %%
extrait_sirh['nombre_heures_travailless'].value_counts()

# %%
# une seule valeur de nombre d'heures travaillées => la colonne ne sert à rien dans l'analyse du modèle de prédiction
extrait_sirh.drop(columns=['nombre_heures_travailless'], inplace=True)

# %%
extrait_sirh['annees_dans_l_entreprise'].describe();

# %%
extrait_sirh['annees_dans_le_poste_actuel'].describe();

# %%
# rien de bien inquiétant, les valeurs fortes ne sont pas considérées comme des outliers
plt.figure(figsize=(20, 6))
sns.boxplot(data=extrait_sirh, x='annees_dans_le_poste_actuel')
plt.title('annees_dans_le_poste_actuel')
plt.show()

# %%
extrait_sondage.info()

# %%
#visualisation des valeurs manquantes(a priori pas de valeurs manquantes car on a 1470 échantillons pour 1470 non-null counts)
extrait_sondage.isnull().sum();

# %%
# recherche des doublons: False sur l'ensemble du dataframe=>pas de doublons
extrait_sondage.duplicated().value_counts()

# %%
# a_quitte_l_entreprise est notre variable y à prédire
extrait_sondage['a_quitte_l_entreprise'].value_counts;

# %%
extrait_sondage.loc[extrait_sondage['a_quitte_l_entreprise']=="Oui"].value_counts;

# %%
comptage = extrait_sondage['a_quitte_l_entreprise'].value_counts()

# Diagramme en barres
plt.bar(comptage.index, comptage.values)
plt.xlabel('A quitté l\'entreprise', color='blue')
plt.ylabel('Nombre de personnes partantes ou restantes',color='blue')
plt.title('Départ de l\'entreprise',color='blue')
plt.show()

# %%
extrait_sondage['nombre_participation_pee'].describe();

# %%
extrait_sondage['nb_formations_suivies'].describe();

# %%
extrait_sondage['nombre_employee_sous_responsabilite'].value_counts()

# %%
# une seule valeur de nombre employee sous responsabilité => la colonne ne sert à rien dans l'analyse du modèle de prédiction
extrait_sondage.drop(columns=['nombre_employee_sous_responsabilite'], inplace=True)

# %%
# eval_number, id_employe et code_sondage semblent être la clé pour fusionner extrait_val, extrait_sirh et extrait_sondage

# %%
extrait_sondage['code_sondage'].describe();

# %%
extrait_sondage['distance_domicile_travail'].value_counts();

# %%
plt.figure(figsize=(20, 6))
sns.boxplot(data=extrait_sondage, x='distance_domicile_travail')
plt.title('distance_domicile_travail')
plt.show()

# %%
extrait_sondage['niveau_education'].value_counts();

# %%
extrait_sondage['domaine_etude'].value_counts();

# %%
extrait_sondage['ayant_enfants'].value_counts();

# %%
#nombre de Y dans la colonne ayant des enfants
extrait_sondage['ayant_enfants'].value_counts().get('Y', 0)

# %%
# une seule valeur de ayant des enfants=> la colonne ne sert à rien dans l'analyse du modèle de prédiction
extrait_sondage.drop(columns=['ayant_enfants'], inplace=True)

# %%
extrait_sondage['frequence_deplacement'].value_counts();

# %%
extrait_sondage['annees_depuis_la_derniere_promotion'].value_counts();

# %%
extrait_sondage['annes_sous_responsable_actuel'].value_counts();

# %%
# relation entre a quitte l'entreprise et la frequence de deplacement (frequents départs pour les fréquents déplacemnts)
tableau_croise = pd.crosstab(extrait_sondage['frequence_deplacement'], 
                        extrait_sondage['a_quitte_l_entreprise'], 
                        normalize='index') * 100 

# Graphique en barres groupées
tableau_croise.plot(kind='bar', figsize=(10, 6))
plt.xlabel('Fréquence de déplacement')
plt.ylabel('Pourcentage de départ ou de continuité (%)')
plt.title('Départ selon la fréquence de déplacement')
plt.legend(title='A quitté l\'entreprise')
plt.xticks(rotation=0)
plt.show()

# %%
# relation entre a quitte l'entreprise et la frequence de deplacement
tableau_croise_2 = pd.crosstab(extrait_sondage['annees_depuis_la_derniere_promotion'], 
                        extrait_sondage['a_quitte_l_entreprise'], 
                        normalize='index') * 100

# Graphique en barres groupées
tableau_croise_2.plot(kind='bar', figsize=(10, 6))
plt.xlabel('Années depuis la derniere promotion')
plt.ylabel('Pourcentage de départ ou de continuité (%)')
plt.title("Départ selon le nombre d'année depuis la derniere promotion")
plt.legend(title='A quitté l\'entreprise')
plt.xticks(rotation=0)
plt.show()

# %%
# ou bien sinon Boxplot
#Le manque de promotion n'est pas LE facteur principal de démission (médianes identiques)
#Certains employés partent malgré des promotions récentes (médiane à 1 an): promus récemment mais insatisfaits 
#des employés sont bloqués sans promotion depuis très longtemps (6/8-15 ans), certians restent mais d'autres partent (les "oubliés")
#la quartile Q3 est plus faible chez les démissionaires; 75% des partants le font au bout de 2 années sans promotion 
extrait_sondage.boxplot(column='annees_depuis_la_derniere_promotion', 
                         by='a_quitte_l_entreprise',
                         figsize=(10, 6))
plt.xlabel('A quitté l\'entreprise', color='blue')
plt.ylabel('annees_depuis_la_derniere_promotion', color='blue')
plt.title("Démissions selon le nombre d'années depuis la dernière promotion", color='blue')
plt.suptitle('')
plt.show()


# %%
# boxplot
#Les employés qui quittent l'entreprise habitent généralement plus loin :
#La médiane est plus élevée
#L'intervalle interquartile est plus large, indiquant une plus grande variabilité
#Le quartile Q3 est plus élevé pour ceux qui quittent l'entreprise , ils font plus de kilomètres pour se rendre au travail
extrait_sondage.boxplot(column='distance_domicile_travail', 
                         by='a_quitte_l_entreprise', 
                         figsize=(10, 6))
plt.xlabel('A quitté l\'entreprise', color='blue')
plt.ylabel('Distance domicile-travail (km)', color='blue')
plt.title('Démissions selon la distance domicile-travail', color='blue')
plt.suptitle('')
plt.show()


# %%
# ou bien, quel est le mieux ?
sns.violinplot(data=extrait_sondage, 
               x='a_quitte_l_entreprise', 
               y='distance_domicile_travail')
plt.xlabel('A quitté l\'entreprise', color='blue')
plt.ylabel('Distance domicile-travail (km)', color='blue')
plt.title('Distance selon le départ', color='blue')
plt.show()



# %%
tableau_croise_domaine_etude = pd.crosstab(extrait_sondage['domaine_etude'], 
                        extrait_sondage['a_quitte_l_entreprise'], 
                        normalize='index') * 100 

tableau_croise_domaine_etude.plot(kind='bar', figsize=(10, 6))
plt.xlabel('domaine_etude', color='blue')
plt.ylabel('Pourcentage de départ ou de continuité (%)', color='blue')
plt.title("Départ selon le domaine d'etude", color='blue')
plt.legend(title='A quitté l\'entreprise')
plt.xticks(rotation=30)
plt.show()

# %%
print(extrait_eval['eval_number'].dtype)
print(extrait_eval['eval_number'].head())

# %%
#préparation de la fusion des 2 premiers dataframes
#convertion du type de données en entier
#on retire le préfixe "E_" et convertion en entier dans eval_number
# Convertion id_employee en entier aussi (au cas où)
extrait_eval['eval_number'] = extrait_eval['eval_number'].str.replace('E_', '').astype(int)
extrait_sirh['id_employee'] = extrait_sirh['id_employee'].astype(int)

# %%
print(extrait_eval['eval_number'].dtype)
print(extrait_eval['eval_number'].head())

# %%
print(extrait_sirh['id_employee'].dtype)
print(extrait_sirh['id_employee'].head())

# %%
# eval_number et id_employee ayant les mêmes valeurs en index, on peut renommer les colonnes identiquement
extrait_eval = extrait_eval.rename(columns={'eval_number': 'id_employee'})

# %%
# Fusion sur la même colonne (clé=id_employee)
fusion_eval_sirh = pd.merge(extrait_eval, extrait_sirh, on='id_employee')

# %%
fusion_eval_sirh.info()

# %%
fusion_eval_sirh['id_employee'];

# %%
print(fusion_eval_sirh['id_employee'].dtype)
print(fusion_eval_sirh['id_employee'].head())

# %%
extrait_sondage['code_sondage'];

# %%
print(extrait_sondage['code_sondage'].dtype)
print(extrait_sondage['code_sondage'].head())

# %%
# extrait_sondage et fusion_eval_sirh ayant les mêmes valeurs en index, on peut renommer les colonnes identiquement
extrait_sondage = extrait_sondage.rename(columns={'code_sondage': 'id_employee'})

# %%
# Fusion sur la même colonne (clé=id_employee)
fusion_totale = pd.merge(fusion_eval_sirh, extrait_sondage, on='id_employee')

# %%
fusion_totale.info()

# %%
tableau_croise_departement = pd.crosstab(fusion_totale['departement'], 
                        fusion_totale['a_quitte_l_entreprise'], 
                        normalize='index') * 100 

tableau_croise_departement.plot(kind='bar', figsize=(10, 6))
plt.xlabel('Département', color='blue')
plt.ylabel('Pourcentage de départ ou de continuité (%)', color='blue')
plt.title("Départ selon le département", color='blue')
plt.legend(title='A quitté l\'entreprise')
plt.xticks(rotation=30)
plt.show()

# %%
# On Crée 10 catégories de revenus ainsi qu'une nouvelle colonne d'une variable catégorielle ordonnée
fusion_totale['categorie_revenu'] = pd.qcut(fusion_totale['revenu_mensuel'], q=10)

# %%
#Compter les occurrences par catégorie et par départ
#tableau croisé qui compte combien de personnes ont quitté ou pas l'entreprise pour chaque catégorie de revenu
#size pour Compter le nombre de lignes dans chaque groupe-series
#unstack Transforme la Series en DataFrame
#fill_value=0 remplace les valeurs manquantes par 0 (si une combinaison n'existe pas)
comptage = fusion_totale.groupby(['categorie_revenu', 'a_quitte_l_entreprise']).size().unstack(fill_value=0)


# %%
# Créer le graphique en barres groupées
comptage.plot(kind='bar', color=['blue', 'orange'], figsize=(10, 6))
plt.xlabel('Revenu mensuel', color='blue')
plt.ylabel('Nombre de personnes partantes ou restantes', color='blue')
plt.title('Départ de l\'entreprise selon le revenu mensuel', color='blue')
plt.legend(title='A quitté l\'entreprise', labels=['Non', 'Oui'])
plt.xticks(rotation=45)
plt.tight_layout()
plt.show()

# %%
tableau_croise_augmentation_salaire = pd.crosstab(fusion_totale['augementation_salaire_precedente'], 
                        fusion_totale['a_quitte_l_entreprise'], 
                        normalize='index') * 100 

tableau_croise_augmentation_salaire.plot(kind='bar', figsize=(10, 6))
plt.xlabel('Pourcentage de la dernière augmentation de salaire', color='blue')
plt.ylabel('Pourcentage de départ ou de continuité (%)', color='blue')
plt.title("Départ selon la dernière hausse de salaire", color='blue')
plt.legend(title='A quitté l\'entreprise')
plt.xticks(rotation=30)
plt.show()

# %%
fusion_totale.boxplot(column='annees_dans_l_entreprise', 
                         by='a_quitte_l_entreprise', 
                         figsize=(10, 6))
plt.xlabel('A quitté l\'entreprise', color='blue')
plt.ylabel('Ancienneté au sein de l\'entreprise', color='blue')
plt.title("Démissions selon l'ancienneté", color='blue')
plt.suptitle('')
plt.show()

# %%
sns.violinplot(data=fusion_totale, 
               x='annees_dans_le_poste_actuel', 
               y='a_quitte_l_entreprise')
plt.title("Démissions selon l'ancienneté au poste")
plt.show()

# %%
#liste des colonnes
fusion_totale.columns.tolist();

# %%
# création d'une feature de progression professionnelle à partir de 2 variables quantitatives
# +1 pour éviter division par 0
fusion_totale['promotion_anciennete'] = (
    fusion_totale['annees_depuis_la_derniere_promotion'] / 
    (fusion_totale['annees_dans_l_entreprise'] + 1)*100)  


# %%
# création d'une feature de stabilité professionnelle à partir de 2 variables quantitatives
# +1 pour éviter division par 0
fusion_totale['score_stabilite'] = (
    fusion_totale['annees_dans_l_entreprise'] / 
    (fusion_totale['nombre_experiences_precedentes'] + 1))

# %%
print (fusion_totale['promotion_anciennete'])

# %%
print (fusion_totale['score_stabilite'])

# %%
#definition des features initiales
features=['satisfaction_employee_environnement', 'note_evaluation_precedente', 'niveau_hierarchique_poste', 'satisfaction_employee_nature_travail',
          'satisfaction_employee_equipe', 'satisfaction_employee_equilibre_pro_perso', 'id_employee', 'note_evaluation_actuelle',
          'heure_supplementaires', 'augementation_salaire_precedente', 'age', 'genre', 'revenu_mensuel', 'statut_marital', 'departement',
          'poste', 'nombre_experiences_precedentes', 'annee_experience_totale', 'annees_dans_l_entreprise', 'annees_dans_le_poste_actuel',
          'nombre_participation_pee', 'nb_formations_suivies', 'distance_domicile_travail', 'niveau_education', 'domaine_etude',
          'frequence_deplacement', 'annees_depuis_la_derniere_promotion', 'annes_sous_responsable_actuel', 'categorie_revenu','promotion_anciennete',
          'score_stabilite']

# %%
# on met de côté les variables numériques:

numeric_cols = ['satisfaction_employee_environnement', 'note_evaluation_precedente', 'niveau_hierarchique_poste', 'satisfaction_employee_nature_travail',
                'satisfaction_employee_equipe', 'satisfaction_employee_equilibre_pro_perso', 'note_evaluation_actuelle', 'age', 'revenu_mensuel',
                'nombre_experiences_precedentes', 'annee_experience_totale', 'annees_dans_l_entreprise', 'annees_dans_le_poste_actuel',
                'nombre_participation_pee', 'nb_formations_suivies', 'distance_domicile_travail', 'niveau_education',
                'annees_depuis_la_derniere_promotion', 'annes_sous_responsable_actuel','promotion_anciennete', 'score_stabilite']

# %%
# matrice de correlation Pearson des variables numériques
corr_matrice_features_numeriques = fusion_totale[numeric_cols].corr()

# %%
plt.figure(figsize=(10, 8))
sns.heatmap(corr_matrice_features_numeriques, annot=True, cmap='coolwarm', center=0, 
            fmt='.2f', square=True, linewidths=1)
plt.title('Matrice de corrélation_features_numeriques')
plt.show()

# %%
# niveau hiérarchique et revenu mensuel sont corrélées=>suppression colonne niv hierarchique
# niveau hiérarchique et annee experience totale corrélées=>OK
# revenu mensuel et annee experience totale corrélées =>suppression colonne annee experience totale
# annee dans l entreprise et annee dans le poste actuel corrélées=>suppression colonne annee dans le poste actuel
# annee dans l entreprise et annee sous responsable actuel corrélées=>suppression colonne annee sous responsable actuel
# année dans le poste actuel et annee sous responsable actuel correlées=>OK
# promotion ancienneté corrélée avec annee depuis la derniere promotion=>suppression de promotion ancienneté
# score stabilite corrélée avec annee dans l entreprise=> suppression de score stabilite

# %%
fusion_totale.drop(columns=['niveau_hierarchique_poste','annee_experience_totale','annees_dans_le_poste_actuel','annes_sous_responsable_actuel',
                            'promotion_anciennete', 'score_stabilite'], inplace=True)

# %%
fusion_totale.info()

# %%
fusion_totale.drop(columns=['categorie_revenu'], inplace=True)


# %%
#definition des features après suppression des corrélations
features_new=['satisfaction_employee_environnement', 'note_evaluation_precedente', 'satisfaction_employee_nature_travail',
          'satisfaction_employee_equipe', 'satisfaction_employee_equilibre_pro_perso', 'id_employee', 'note_evaluation_actuelle',
          'heure_supplementaires', 'augementation_salaire_precedente', 'age', 'genre', 'revenu_mensuel', 'statut_marital', 'departement',
          'poste', 'nombre_experiences_precedentes', 'annees_dans_l_entreprise',
          'nombre_participation_pee', 'nb_formations_suivies', 'distance_domicile_travail', 'niveau_education', 'domaine_etude',
          'frequence_deplacement', 'annees_depuis_la_derniere_promotion']

# %%
#features numériques après suppression des corrélations
numeric_cols_new = ['satisfaction_employee_environnement', 'note_evaluation_precedente', 'satisfaction_employee_nature_travail',
                'satisfaction_employee_equipe', 'satisfaction_employee_equilibre_pro_perso', 'note_evaluation_actuelle', 'age', 'revenu_mensuel',
                'nombre_experiences_precedentes', 'annees_dans_l_entreprise', 'nombre_participation_pee', 'nb_formations_suivies', 
                'distance_domicile_travail', 'niveau_education', 'annees_depuis_la_derniere_promotion']

# %%
# simplication du modèle

import pandas as pd
import joblib

from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OrdinalEncoder, OneHotEncoder, RobustScaler
from sklearn.pipeline import Pipeline
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split, StratifiedKFold, GridSearchCV
from sklearn.metrics import roc_auc_score, classification_report

# Nettoyage robuste des pourcentages AVANT toute utilisation
fusion_totale["augementation_salaire_precedente"] = (
    fusion_totale["augementation_salaire_precedente"]
    .astype(str)
    .str.strip()
    .str.replace(" ", "", regex=False)
    .str.replace("\u00A0", "", regex=False)  # espace insécable
)
print(fusion_totale["augementation_salaire_precedente"].unique())

valeurs = set(fusion_totale["augementation_salaire_precedente"].unique())
attendues = set([
    "11%", "12%", "13%", "14%", "15%", "16%", "17%", "18%",
    "19%", "20%", "21%", "22%", "23%", "24%", "25%"
])

print("Valeurs inconnues :", valeurs - attendues)


# -------------------------------------------------------------------
# Définition de la cible y et encodage
# -------------------------------------------------------------------
y = fusion_totale["a_quitte_l_entreprise"]
mapping_cible = {"Non": 0, "Oui": 1}
y_encoded = y.map(mapping_cible)

# On enlève la cible de X et id_employee
X = fusion_totale.drop(columns=["a_quitte_l_entreprise", "id_employee"])



# -------------------------------------------------------------------
# 3. Définition des colonnes par type
# -------------------------------------------------------------------

# Variables ordinales avec ordre explicite
ordinal_categories = {
    "augementation_salaire_precedente": [
        "11%", "12%", "13%", "14%", "15%", "16%", "17%", "18%",
        "19%", "20%", "21%", "22%", "23%", "24%", "25%"
    ],
    "frequence_deplacement": ["Aucun", "Occasionnel", "Frequent"],
}

ordinal_cols = list(ordinal_categories.keys())

# Variables binaires (0/1 ou Oui/Non déjà codés de manière binaire ou assimilable)
binary_cols = ["heure_supplementaires", "genre"]

# Variables nominales (catégorielles sans ordre)
nominal_cols = ["statut_marital", "departement", "poste", "domaine_etude"]

# Variables numériques ( numeric_cols_new)
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

# vérifier qu'on ne s'est pas trompé dans les colonnes
expected_cols = set(ordinal_cols + binary_cols + nominal_cols + numeric_cols)
missing_in_X = expected_cols - set(X.columns)
extra_in_X = set(X.columns) - expected_cols

if missing_in_X:
    print("Colonnes attendues manquantes dans X :", missing_in_X)
if extra_in_X:
    print("Colonnes présentes dans X mais non utilisées :", extra_in_X)

# -------------------------------------------------------------------
# 4. Construction du préprocesseur (ColumnTransformer)
# -------------------------------------------------------------------
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



# -------------------------------------------------------------------
# 5. Construction du pipeline complet (preprocess + modèle)
# -------------------------------------------------------------------
classifier = LogisticRegression(
    C=1.0,
    penalty="l2",
    solver="lbfgs",
    max_iter=1000,
    class_weight="balanced",
    n_jobs=-1,
)

pipeline = Pipeline(
    steps=[
        ("preprocess", preprocessor),
        ("classifier", classifier),
    ]
)


# -------------------------------------------------------------------
# 6. Découpage train/test
# -------------------------------------------------------------------
X_train, X_test, y_train, y_test = train_test_split(
    X,
    y_encoded,
    test_size=0.20,
    random_state=42,
    stratify=y_encoded,
)

# -------------------------------------------------------------------
# 7. GridSearchCV (optionnel mais propre)
# -------------------------------------------------------------------
param_grid = {
    "classifier__C": [0.01, 0.1, 1.0, 10.0],
}

skf = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)

grid = GridSearchCV(
    estimator=pipeline,
    param_grid=param_grid,
    cv=skf,
    scoring="roc_auc",
    n_jobs=-1,
    verbose=1,
    return_train_score=True,
)

grid.fit(X_train, y_train)

print("Meilleurs hyperparamètres :", grid.best_params_)

best_model = grid.best_estimator_

# -------------------------------------------------------------------
# 8. Évaluation sur le test set
# -------------------------------------------------------------------
y_pred_proba = best_model.predict_proba(X_test)[:, 1]
y_pred = best_model.predict(X_test)

auc = roc_auc_score(y_test, y_pred_proba)
print(f"ROC-AUC sur le test set : {auc:.4f}")
print("\nClassification report :\n")
print(classification_report(y_test, y_pred))

# -------------------------------------------------------------------
# 9. Sauvegarde du pipeline complet
# -------------------------------------------------------------------
joblib.dump(best_model, "model.joblib")
print(" Modèle sauvegardé dans 'model.joblib' (pipeline complet).")


# %%
print(X)

# %%


# %%


# %%


# %%



