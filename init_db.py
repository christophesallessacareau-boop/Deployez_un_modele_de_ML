"""
Script d'initialisation TOUT-EN-UN avec schéma SQL personnalisé
Fichier: init_db.py

Utilise le schéma SQL défini par l'utilisateur :
- 3 tables métier avec FOREIGN KEY
- Tables de traçabilité
- Vue fusionnée
- Import automatique des CSV
"""

import sys
from pathlib import Path
import pandas as pd

sys.path.insert(0, str(Path(__file__).parent / 'src'))

from database import DatabaseManager, db_config


# Schéma SQL complet
SCHEMA_SQL = """
-- =====================================================
-- CRÉATION DES TABLES MÉTIER
-- =====================================================

DROP TABLE IF EXISTS extrait_eval CASCADE;
DROP TABLE IF EXISTS extrait_sondage CASCADE;
DROP TABLE IF EXISTS extrait_sirh CASCADE;

CREATE TABLE extrait_sirh (
    id_employee INTEGER PRIMARY KEY,
    age INTEGER,
    genre VARCHAR(20),
    revenu_mensuel INTEGER,
    statut_marital VARCHAR(30),
    departement VARCHAR(50),
    poste VARCHAR(50),
    nombre_experiences_precedentes INTEGER,
    annees_dans_l_entreprise INTEGER,
    annees_dans_le_poste_actuel INTEGER,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE extrait_eval (
    eval_number VARCHAR(50) PRIMARY KEY,
    id_employee INTEGER NOT NULL,
    augmentation_salaire_precedente VARCHAR(20),
    heure_supplementaires VARCHAR(20),
    satisfaction_employee_environnement INTEGER,
    note_evaluation_precedente INTEGER,
    satisfaction_employee_nature_travail INTEGER,
    satisfaction_employee_equipe INTEGER,
    satisfaction_employee_equilibre_pro_perso INTEGER,
    note_evaluation_actuelle INTEGER,
    created_at TIMESTAMP DEFAULT NOW(),
    FOREIGN KEY (id_employee) REFERENCES extrait_sirh(id_employee) ON DELETE CASCADE
);

CREATE TABLE extrait_sondage (
    code_sondage VARCHAR(50) PRIMARY KEY,
    id_employee INTEGER NOT NULL,
    a_quitte_l_entreprise VARCHAR(10),
    frequence_deplacement VARCHAR(30),
    domaine_etude VARCHAR(50),
    nombre_participation_pee INTEGER,
    nb_formations_suivies INTEGER,
    distance_domicile_travail INTEGER,
    niveau_education INTEGER,
    annees_depuis_la_derniere_promotion INTEGER,
    created_at TIMESTAMP DEFAULT NOW(),
    FOREIGN KEY (id_employee) REFERENCES extrait_sirh(id_employee) ON DELETE CASCADE
);

-- =====================================================
-- VUE FUSIONNÉE (INNER JOIN)
-- =====================================================

CREATE OR REPLACE VIEW donnees_fusionnees AS
SELECT
    s.id_employee,
    s.age,
    s.genre,
    s.revenu_mensuel,
    s.statut_marital,
    s.departement,
    s.poste,
    s.nombre_experiences_precedentes,
    s.annees_dans_l_entreprise,
    s.annees_dans_le_poste_actuel,
    
    e.eval_number,
    e.augmentation_salaire_precedente,
    e.heure_supplementaires,
    e.satisfaction_employee_environnement,
    e.note_evaluation_precedente,
    e.satisfaction_employee_nature_travail,
    e.satisfaction_employee_equipe,
    e.satisfaction_employee_equilibre_pro_perso,
    e.note_evaluation_actuelle,
    
    so.code_sondage,
    so.a_quitte_l_entreprise,
    so.frequence_deplacement,
    so.domaine_etude,
    so.nombre_participation_pee,
    so.nb_formations_suivies,
    so.distance_domicile_travail,
    so.niveau_education,
    so.annees_depuis_la_derniere_promotion
FROM extrait_sirh s
INNER JOIN extrait_eval e ON s.id_employee = e.id_employee
INNER JOIN extrait_sondage so ON s.id_employee = so.id_employee;

-- =====================================================
-- INDEX POUR PERFORMANCES
-- =====================================================

CREATE INDEX IF NOT EXISTS idx_sirh_employee ON extrait_sirh(id_employee);
CREATE INDEX IF NOT EXISTS idx_eval_employee ON extrait_eval(id_employee);
CREATE INDEX IF NOT EXISTS idx_sondage_employee ON extrait_sondage(id_employee);
"""


def create_schema(db):
    """Crée le schéma complet de la base de données"""
    
    print("2️  Création du schéma SQL...")
    
    try:
        # Exécute le schéma SQL complet
        with db.engine.begin() as connection:
            connection.execute(SCHEMA_SQL)
        print("    Tables métier créées (avec FOREIGN KEY)")
        print("    Vue 'donnees_fusionnees' créée")
        print("    Index créés\n")
        return True
    except Exception as e:
        print(f"    Erreur: {e}\n")
        return False


def import_csv_files(db):
    """Importe les CSV dans les tables avec respect des FOREIGN KEY"""
    
    print("3️  Import des fichiers CSV...")
    
    csv_files = [
        # IMPORTANT : Ordre respectant les FOREIGN KEY
        # 1. D'abord la table parent (extrait_sirh)
        ('src/data/extrait_sirh.csv', 'extrait_sirh'),
        # 2. Puis les tables enfants
        ('src/data/extrait_eval.csv', 'extrait_eval'),
        ('src/data/extrait_sondage.csv', 'extrait_sondage')
    ]
    
    imported = 0
    for csv_path, table_name in csv_files:
        if not Path(csv_path).exists():
            print(f"     {csv_path} introuvable")
            continue
        
        try:
            # Lecture du CSV
            df = pd.read_csv(csv_path)
            
            # Import dans PostgreSQL (append pour respecter les contraintes)
            df.to_sql(table_name, db.engine, if_exists='append', index=False)
            
            print(f"    {table_name}: {len(df)} lignes importées")
            imported += 1
            
            # Log de l'opération
            db.log_operation(
                operation_type='IMPORT_CSV',
                table_name=table_name,
                rows_affected=len(df),
                status='SUCCESS'
            )
            
        except Exception as e:
            print(f"    {table_name}: {e}")
            db.log_operation(
                operation_type='IMPORT_CSV',
                table_name=table_name,
                status='ERROR',
                error_message=str(e)
            )
    
    print()
    return imported > 0


def verify_data(db):
    """Vérifie les données importées et la vue fusionnée"""
    
    print("4️  Vérification des données...")
    
    try:
        # Comptage dans chaque table
        for table in ['extrait_sirh', 'extrait_eval', 'extrait_sondage']:
            count = pd.read_sql_query(f"SELECT COUNT(*) FROM {table}", db.engine).iloc[0, 0]
            print(f"   • {table:20s}: {count:>5} lignes")
        
        # Comptage dans la vue fusionnée
        count_fusion = pd.read_sql_query("SELECT COUNT(*) FROM donnees_fusionnees", db.engine).iloc[0, 0]
        print(f"   • {'donnees_fusionnees':20s}: {count_fusion:>5} lignes (INNER JOIN)\n")
        
        # Vérification de l'intégrité référentielle
        query_orphan = """
        SELECT 
            (SELECT COUNT(*) FROM extrait_eval WHERE id_employee NOT IN (SELECT id_employee FROM extrait_sirh)) as orphan_eval,
            (SELECT COUNT(*) FROM extrait_sondage WHERE id_employee NOT IN (SELECT id_employee FROM extrait_sirh)) as orphan_sondage
        """
        orphans = pd.read_sql_query(query_orphan, db.engine).iloc[0]
        
        if orphans['orphan_eval'] == 0 and orphans['orphan_sondage'] == 0:
            print("    Intégrité référentielle OK (pas d'orphelins)\n")
        else:
            print(f"     Orphelins détectés: eval={orphans['orphan_eval']}, sondage={orphans['orphan_sondage']}\n")
        
        return True
        
    except Exception as e:
        print(f"    Erreur: {e}\n")
        return False


def show_sample_data(db):
    """Affiche un échantillon de données fusionnées"""
    
    print("5️  Aperçu des données fusionnées...")
    
    try:
        df_sample = pd.read_sql_query("SELECT * FROM donnees_fusionnees LIMIT 3", db.engine)
        print(f"\n{df_sample.to_string(index=False)}\n")
    except Exception as e:
        print(f"     {e}\n")


def main():
    """Fonction principale"""
    
    print("\n Initialisation complète de la base de données\n")
    print("=" * 60)
    
    # ==========================================
    # ÉTAPE 1 : Test de connexion
    # ==========================================
    print("1️  Test de connexion PostgreSQL...")
    
    if not db_config.test_connection():
        print("\n Connexion impossible!")
        print("\n Créez d'abord la base de données:")
        print("   psql -U postgres -c 'CREATE DATABASE ma_base_rh;'")
        print("\nPuis configurez .env avec vos credentials.")
        return 1
    
    print("    Connexion OK\n")
    
    # Initialisation du gestionnaire
    db = DatabaseManager()
    
    # ==========================================
    # ÉTAPE 2 : Création du schéma SQL
    # ==========================================
    if not create_schema(db):
        return 1
    
    # Création des tables de traçabilité (SQLAlchemy)
    db.create_all_tables()
    print("    Tables de traçabilité créées\n")
    
    # ==========================================
    # ÉTAPE 3 : Import des CSV
    # ==========================================
    if not import_csv_files(db):
        print("  Aucun CSV importé. Placez vos fichiers dans src/data/\n")
        return 0
    
    # ==========================================
    # ÉTAPE 4-5 : Vérifications
    # ==========================================
    verify_data(db)
    show_sample_data(db)
    
    # ==========================================
    # RÉSUMÉ FINAL
    # ==========================================
    print("=" * 60)
    print(" INITIALISATION TERMINÉE")
    print("=" * 60)
    
    tables = db.list_all_tables()
    print(f"\n {len(tables)} tables/vues disponibles:")
    for table in sorted(tables):
        print(f"   • {table}")
    
    print("\n Prochaines étapes:")
    print("   1. Requête SQL : SELECT * FROM donnees_fusionnees;")
    print("   2. Lance l'API : uvicorn src.app.main:app --reload")
    print("   3. Test : http://localhost:8000/docs\n")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())