FROM python:3.11-slim

WORKDIR /app

# Copier les fichiers de dépendances
COPY requirements.txt .

# Installer les dépendances
RUN pip install --no-cache-dir -r requirements.txt

# Copier le code de l'application et le modèle
COPY main.py .
COPY model.joblib .

# Exposer le port 7860 (port standard pour HF Spaces)
EXPOSE 7860

# Lancer l'application FastAPI avec main.py
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "7860"]