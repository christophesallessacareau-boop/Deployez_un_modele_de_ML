# script de test rapide
# test d'une prediction (N° de l'ID) quand tout est prêt
# on evite de tout refaire (import, tables) à chaque test
from model import SimpleModel

model = SimpleModel("model.joblib")
result = model.predict_one(10)
print("Prediction :", result)

