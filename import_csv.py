# import_csv dans base de donnees
import pandas as pd
from sqlalchemy import create_engine
from config import DB_URL

# utilisation directe des credentials avec DB_URL
engine = create_engine(DB_URL)

def import_csv_to_table(csv_path, table_name):
    df = pd.read_csv(csv_path)
    df.to_sql(table_name, engine, if_exists="append", index=False)
    print(f"Import OK → {table_name}")

