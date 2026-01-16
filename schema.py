# version schema.py
# connexion à la base de données
# création du schema sql et des tables


from sqlalchemy import text
from database import engine

SCHEMA_SQL = """
-- =====================================================
-- CREATION DES TABLES METIER
-- =====================================================

CREATE TABLE IF NOT EXISTS donnees_fusionnees (
    id_employee INTEGER PRIMARY KEY,

    satisfaction_employee_environnement        INTEGER,
    note_evaluation_precedente                 INTEGER,
    satisfaction_employee_nature_travail       INTEGER,
    satisfaction_employee_equipe               INTEGER,
    satisfaction_employee_equilibre_pro_perso  INTEGER,

    note_evaluation_actuelle                   INTEGER,
    heure_supplementaires                      TEXT,
    augementation_salaire_precedente           TEXT,
    age                                        INTEGER,
    genre                                      TEXT,
    revenu_mensuel                             INTEGER,
    statut_marital                             TEXT,
    departement                                TEXT,
    poste                                      TEXT,
    nombre_experiences_precedentes             INTEGER,
    annees_dans_l_entreprise                   INTEGER,
    a_quitte_l_entreprise                      INTEGER,
    nombre_participation_pee                   INTEGER,
    nb_formations_suivies                      INTEGER,
    distance_domicile_travail                  INTEGER,
    niveau_education                           INTEGER,
    domaine_etude                              TEXT,
    frequence_deplacement                      TEXT,
    annees_depuis_la_derniere_promotion        INTEGER,

    created_at TIMESTAMP DEFAULT NOW()
);

-- =====================================================
-- TABLE DE LOGS POUR LE MODELE
-- =====================================================
-- Tracabilite du modele et enregistrement des predictions
-- pour chaque employe, on stocke les donnees d'entree,
-- la prediction et un horodatage

CREATE TABLE IF NOT EXISTS model_logs ( 
    id SERIAL PRIMARY KEY,
    id_employee INTEGER, 
    input_json JSONB, 
    output_json JSONB, 
    created_at TIMESTAMP DEFAULT NOW() 
);
"""
    

def create_schema():
    """
    Crée les tables de la base de données via SQLAlchemy.
    """
    with engine.begin() as conn:
        conn.execute(text(SCHEMA_SQL))

    print("Schéma créé avec succès")


if __name__ == "__main__":
    create_schema()