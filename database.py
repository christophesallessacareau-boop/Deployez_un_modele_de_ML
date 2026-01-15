# creation des tables
# connexion base de donnees

from sqlalchemy import create_engine, text
import os
from dotenv import load_dotenv
import pandas as pd

load_dotenv()

DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME")

# Construction de l'URL de connexion à la base de donnees
DB_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"


# utilisation directe des credentials avec DB_URL
engine = create_engine(DB_URL)

# ids déjà présents
existing_ids = pd.read_sql(
    "SELECT id_employee FROM donnees_fusionnees",
    engine
)

# Chargement du CSV
# -----------------------------
df = pd.read_csv("donnees_fusionnees.csv")

df = df[~df["id_employee"].isin(existing_ids["id_employee"])]

# Insertion dans PostgreSQL
# -----------------------------
df.to_sql(
    name="donnees_fusionnees",
    con=engine,
    if_exists="append",   # ajoute les lignes à la table existante
    index=False           # ne pas créer de colonne index
)

print(" Import du fichier CSV terminé")


# lecture des donnees fusionnees depuis la base de donnees
# utilisation directe des credentials avec DB_URL
engine = create_engine(DB_URL)

def load_fused_data():
    query = "SELECT * FROM donnees_fusionnees"
    df = pd.read_sql(query, engine)
    
    # Verification : la vue est vide 
    if df.empty: 
        raise Exception("Aucune donnee fusionnee disponible")

    return df

if __name__ == "__main__":
    df_loaded = load_fused_data()
    print(df_loaded.head())