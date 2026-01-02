from sqlalchemy import create_engine, text
from config import DB_URL

engine = create_engine(DB_URL)

def create_tables(schema_sql):
    with engine.connect() as conn:
        conn.execute(text(schema_sql))
        conn.commit()
