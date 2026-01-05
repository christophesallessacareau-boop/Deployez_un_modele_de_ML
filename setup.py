# script d'initialisation
## creation des tables, import CSV, fusion des donnees, chargement du modele entraîne
## prediction du modele avec un individu (id_employee=101)
from database import create_tables
from import_csv import import_csv_to_table
from fusion import load_fused_data
from model import SimpleModel
from schema import SCHEMA_SQL

# 1. Creation des tables
create_tables(SCHEMA_SQL)

# 2. Import CSV
import_csv_to_table("extrait_sirh.csv", "extrait_sirh")
import_csv_to_table("extrait_eval.csv", "extrait_eval")
import_csv_to_table("extrait_sondage.csv", "extrait_sondage")

# 3. Charger les donnees fusionnees
df = load_fused_data()

# 4. Charger le modele
model = SimpleModel("model.joblib")

# 5. Prediction
result = model.predict_one(101)
print("Prediction :", result)
