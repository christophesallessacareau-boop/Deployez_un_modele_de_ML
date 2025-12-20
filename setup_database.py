"""
Script d'initialisation de la base de données
Fichier: setup_database.py 
Usage: python setup_database.py
"""

import sys
from pathlib import Path

# Ajoute le dossier src au path pour les imports
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from database import DatabaseManager, db_config


def setup_database():
    """Configuration initiale de la base de données"""
    
    
    print("CONFIGURATION DE LA BASE DE DONNÉES PostgreSQL")
    
    
    # Test de connexion
    print("\n1. Test de connexion...")
    if not db_config.test_connection():
        print(" Impossible de se connecter à la base de données")
        print("\nVérifiez:")
        print("  - PostgreSQL est installé et démarré")
        print("  - Le fichier .env contient les bonnes credentials")
        print("  - La base de données existe")
        return False
    
    # Initialisation du gestionnaire
    print("\n2. Initialisation du gestionnaire...")
    db_manager = DatabaseManager()
    
    # Création des tables
    print("\n3. Création des tables de traçabilité...")
    db_manager.create_all_tables()
    
    # Affichage des tables créées
    print("\n4. Tables créées avec succès:")
    tables = db_manager.list_all_tables()
    for table in tables:
        print(f"   ✓ {table}")
    
    
    print(" Configuration terminée avec succès!")
    
    
    return True


def import_csv_files():
    """Importe les fichiers CSV dans la base"""
    
    
    print("IMPORT DES FICHIERS CSV")
    
    
    db_manager = DatabaseManager()
    
    # Définition des fichiers CSV à importer
    csv_files = [
        ('src/data/extrait_sirh.csv', 'sirh'),
        ('src/data/extrait_sondage.csv', 'sondage'),
        ('src/data/extrait_eval.csv', 'evaluation')
    ]
    
    imported = 0
    for csv_path, table_name in csv_files:
        if Path(csv_path).exists():
            try:
                print(f"\n Import de {csv_path}...")
                rows = db_manager.import_csv_to_table(csv_path, table_name)
                print(f"  ✓ {rows} lignes importées dans '{table_name}'")
                imported += 1
            except Exception as e:
                print(f"  ✗ Erreur: {e}")
        else:
            print(f"\n⚠ Fichier non trouvé: {csv_path}")
    
    if imported > 0:
        print(f"\n {imported} fichier(s) importé(s) avec succès")
    else:
        print("\n⚠ Aucun fichier CSV n'a été importé")
        print("   Placez vos fichiers CSV dans src/data/")
    
    return imported > 0


def merge_tables_example():
    """ fusion de tables"""
    

    print("FUSION DES TABLES")
    
    
    db_manager = DatabaseManager()
    
    # Vérifie que les tables existent
    tables = db_manager.list_all_tables()
    required_tables = ['sirh', 'sondage', 'evaluation']
    
    if not all(t in tables for t in required_tables):
        print("\n Toutes les tables nécessaires ne sont pas présentes")
        print(f"   Tables disponibles: {', '.join(tables)}")
        print("\n Pour fusionner les tables, vous devez d'abord importer les CSV")
        return False
    
    # Affichage des colonnes de chaque table
    print("\nColonnes disponibles dans chaque table:")
    for table in required_tables:
        info = db_manager.get_table_info(table)
        if info:
            cols = [col['name'] for col in info['columns']]
            print(f"\n  {table}:")
            print(f"    {', '.join(cols)}")
    
    
    print("Pour fusionner les tables, ajoutez ce code:")
    
    print("""
# Exemple de fusion sur une clé commune 
db_manager.merge_tables(
    tables=['sirh', 'sondage', 'evaluation'],
    output_table='donnees_fusionnees',
    join_key='employee_id',  # à Remplacer par la clé commune
    how='inner'  # ou 'outer', 'left', 'right'
)
    """)
    
    return True


def show_logs():
    """Affiche les dernières opérations loggées"""
    
    
    print("DERNIÈRES OPÉRATIONS ENREGISTRÉES")
    
    
    db_manager = DatabaseManager()
    
    try:
        logs = db_manager.get_operation_logs(limit=10)
        if len(logs) > 0:
            print("\n")
            print(logs.to_string(index=False))
        else:
            print("\n⚠ Aucune opération enregistrée pour le moment")
    except Exception as e:
        print(f"\n⚠ Impossible de récupérer les logs: {e}")


def main():
    """Fonction principale"""
    
    print("\n Script d'initialisation de la base de données\n")
    
    # Étape 1: Configuration de base
    if not setup_database():
        sys.exit(1)
    
    # Étape 2: Import des CSV (optionnel)
    import_choice = input("\n Voulez-vous importer les fichiers CSV maintenant? (o/n): ")
    if import_choice.lower() == 'o':
        import_csv_files()
        
        # Étape 3: Fusion (optionnel)
        merge_choice = input("\n Voulez-vous voir un exemple de fusion? (o/n): ")
        if merge_choice.lower() == 'o':
            merge_tables_example()
    
    # Affichage des logs
    show_logs()
    
    
    print(" PROCHAINES ÉTAPES")
    
    print("""
1. Placer les fichiers CSV dans: src/data/
2. Pour importer: python setup_database.py
3. Pour utiliser dans le code:
   
   from database import DatabaseManager
   db = DatabaseManager()
   db.import_csv_to_table('chemin.csv', 'nom_table')
   
4. Logs disponibles dans: database_operations.log
    """)


if __name__ == "__main__":
    main()