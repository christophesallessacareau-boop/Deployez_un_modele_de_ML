import json
import joblib
import pandas as pd
from sqlalchemy import create_engine, text
from config import DB_URL

engine = create_engine(DB_URL)

class SimpleModel:

    def __init__(self, model_path="model.joblib"):
        self.model = joblib.load(model_path)

    def predict_one(self, employee_id):
        query = f"""
            SELECT * FROM donnees_fusionnees
            WHERE id_employee = {employee_id}
        """
        df = pd.read_sql(query, engine)

        if df.empty:
            raise ValueError("Employé introuvable")

        X = df.drop(columns=["a_quitte_l_entreprise"])
        prediction = self.model.predict(X)[0]

        self.log_prediction(employee_id, X.to_dict(), {"prediction": prediction})

        return prediction

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

