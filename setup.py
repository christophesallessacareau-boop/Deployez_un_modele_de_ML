# script d'initialisation
## creation des tables, import CSV, fusion des donnees, chargement du modele entraîne
## prediction du modele avec un individu (id_employee=101)
from database import create_tables, load_fused_data, import_csv_to_table
from model import SimpleModel
from schema import SCHEMA_SQL

# 1. Creation des tables
create_tables(SCHEMA_SQL)

# 2. Import CSV
import_csv_to_table("donnees_fusionnees.csv", "donnees_fusionnees")

# 3. Charger les donnees fusionnees
df = load_fused_data()

# 4. Charger le modele
model = SimpleModel("model.joblib")

# 5. Prediction
result = model.predict_one(1)
print("Prediction :", result)
