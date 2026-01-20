import json
import joblib
import pandas as pd
from sqlalchemy import create_engine, text
from database import engine


# configuration de la connexion à la base avec SQLAlchemy


class SimpleModel:
    # chargement du modele entraîne
    def __init__(self, model_path="model.joblib"):
        self.model = joblib.load(model_path)
    # prediction avec ce modele
    def predict_one(self, employee_id):
        query = text("""
            SELECT * FROM donnees_fusionnees
            WHERE id_employee = :id
        """)
        df = pd.read_sql(query, engine, params={"id": employee_id})
        if df.empty:
            raise ValueError("Employe introuvable")

        X = df.drop(columns=["a_quitte_l_entreprise"])
        prediction = self.model.predict(X)[0] # une seule prediction unique

        self.log_prediction(employee_id, X.to_dict(), {"prediction": prediction})

        return prediction
    # enregistrement des predictions dans la base dédiée aux logs
    def log_prediction(self, employee_id, input_data, output_data):
        with engine.connect() as conn:
            conn.execute(
                text("""
                    INSERT INTO model_logs (id_employee, input_json, output_json)
                    VALUES (:id_employee, :input_json, :output_json)
                """),
                {
                    "id_employee": employee_id,
                    "input_json": json.dumps(input_data),
                    "output_json": json.dumps(output_data)
                }
            )
            conn.commit()

