from database import create_tables
from import_csv import import_csv_to_table
from fusion import load_fused_data
from model import SimpleModel
from schema import SCHEMA_SQL

# 1. Création des tables
create_tables(SCHEMA_SQL)

# 2. Import CSV
import_csv_to_table("extrait_sirh.csv", "extrait_sirh")
import_csv_to_table("extrait_eval.csv", "extrait_eval")
import_csv_to_table("extrait_sondage.csv", "extrait_sondage")

# 3. Charger les données fusionnées
df = load_fused_data()

# 4. Charger le modèle
model = SimpleModel("model.joblib")

# 5. Prédiction
result = model.predict_one(101)
print("Prédiction :", result)
