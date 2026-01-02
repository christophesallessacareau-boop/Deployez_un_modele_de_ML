import pandas as pd
from sqlalchemy import create_engine
from config import DB_URL

engine = create_engine(DB_URL)

def load_fused_data():
    query = "SELECT * FROM donnees_fusionnees"
    df = pd.read_sql(query, engine)
    return df

