# lecture des donnees fusionnees depuis la base de donnees
import pandas as pd
from sqlalchemy import create_engine
from config import DB_URL

# utilisation directe des credentials avec DB_URL
engine = create_engine(DB_URL)

def load_fused_data():
    query = "SELECT * FROM donnees_fusionnees"
    df = pd.read_sql(query, engine)
    
    # Verification : la vue est vide 
    if df.empty: 
        raise Exception("Aucune donnee fusionnee disponible")

    return df

