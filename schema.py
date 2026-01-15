# version schema.py
# connexion à la base de données
# création du schema sql et des tables


import psycopg2
from psycopg2 import sql
import os

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
    

def create_schema(host="localhost", database="ma_base_rh", user="postgres", password=None):
    """
    Crée le schéma de la base de données.
    
    Args:
        host: Hôte PostgreSQL
        database: Nom de la base de données
        user: Utilisateur PostgreSQL
        password: Mot de passe (si None, sera demandé)
    """
    try:
        # Si pas de mot de passe fourni, le demander
        if password is None:
            import getpass
            password = getpass.getpass("Mot de passe PostgreSQL: ")
        
        # Connexion à la base de données
        print(f"Connexion à la base de données '{database}'...")
        conn = psycopg2.connect(
            host=host,
            database=database,
            user=user,
            password=password
        )
        
        # Désactiver l'autocommit pour gérer les transactions
        conn.autocommit = False
        
        cur = conn.cursor()
        
        # Exécution du schéma
        print("Création des tables et vues...")
        cur.execute(SCHEMA_SQL)
        
        # Validation des changements
        conn.commit()
        
        print(" Schéma créé avec succès!")
        
        # Vérification des tables créées
        cur.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public' 
            AND table_type = 'BASE TABLE'
            ORDER BY table_name;
        """)
        
        tables = cur.fetchall()
        print(f"\nTables créées ({len(tables)}):")
        for table in tables:
            print(f"  - {table[0]}")
        
        # Vérification des vues
        cur.execute("""
            SELECT table_name 
            FROM information_schema.views 
            WHERE table_schema = 'public'
            ORDER BY table_name;
        """)
        
        views = cur.fetchall()
        print(f"\nVues créées ({len(views)}):")
        for view in views:
            print(f"  - {view[0]}")
        
        cur.close()
        conn.close()
        
    except psycopg2.Error as e:
        print(f" Erreur PostgreSQL: {e}")
        if 'conn' in locals():
            conn.rollback()
            conn.close()
    except Exception as e:
        print(f" Erreur: {e}")

if __name__ == "__main__":
    create_schema(
        host="localhost",
        database="ma_base_rh",
        user="postgres",
        password=None  # Sera demandé lors de l'exécution
    )
