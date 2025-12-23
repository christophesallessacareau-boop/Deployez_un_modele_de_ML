"""
Script de configuration rapide de PostgreSQL
Fichier: quick_setup.py 

Ce script vous aide à créer le fichier .env interactivement
"""

import os
from pathlib import Path


def create_env_file():
    """Crée le fichier .env de manière interactive"""
    
    print("=" * 60)
    print("CONFIGURATION RAPIDE DE LA BASE DE DONNÉES")
    print("=" * 60)
    
    print("\n Je vais vous aider à créer le fichier .env\n")
    
    # Valeurs par défaut
    defaults = {
        'DB_USER': 'postgres',
        'DB_HOST': 'localhost',
        'DB_PORT': '5432',
        'DB_NAME': 'ma_base_rh'
    }
    
    config = {}
    
    # Questions interactives
    print("Appuyez sur Entrée pour utiliser la valeur par défaut [entre crochets]\n")
    
    config['DB_USER'] = input(f"Utilisateur PostgreSQL [{defaults['DB_USER']}]: ").strip() or defaults['DB_USER']
    
    # Mot de passe (obligatoire)
    while True:
        password = input("Mot de passe PostgreSQL (OBLIGATOIRE): ").strip()
        if password:
            config['DB_PASSWORD'] = password
            break
        else:
            print("  Le mot de passe est obligatoire!\n")
    
    config['DB_HOST'] = input(f"Hôte [{defaults['DB_HOST']}]: ").strip() or defaults['DB_HOST']
    config['DB_PORT'] = input(f"Port [{defaults['DB_PORT']}]: ").strip() or defaults['DB_PORT']
    config['DB_NAME'] = input(f"Nom de la base de données [{defaults['DB_NAME']}]: ").strip() or defaults['DB_NAME']
    
    # Affichage du résumé
    print("\n" + "=" * 60)
    print("RÉSUMÉ DE VOTRE CONFIGURATION")
    print("=" * 60)
    for key, value in config.items():
        if key == 'DB_PASSWORD':
            print(f"{key}={'*' * len(value)}")
        else:
            print(f"{key}={value}")
    
    # Confirmation
    confirm = input("\n Confirmer et créer le fichier .env ? (o/n): ").strip().lower()
    
    if confirm == 'o':
        # Création du fichier .env
        env_path = Path('.env')
        with open(env_path, 'w', encoding='utf-8') as f:
            f.write("# Configuration de la base de données PostgreSQL\n")
            f.write("# Généré automatiquement par quick_setup.py\n\n")
            for key, value in config.items():
                f.write(f"{key}={value}\n")
        
        print(f"\n Fichier .env créé avec succès!")
        
        # Vérification du .gitignore
        gitignore_path = Path('.gitignore')
        if gitignore_path.exists():
            with open(gitignore_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            if '.env' not in content:
                print("  N'oubliez pas d'ajouter .env à votre .gitignore!")
                add_gitignore = input("   Voulez-vous que je l'ajoute maintenant? (o/n): ").strip().lower()
                if add_gitignore == 'o':
                    with open(gitignore_path, 'a', encoding='utf-8') as f:
                        f.write("\n# Fichier de configuration avec credentials\n.env\n")
                    print("    .env ajouté à .gitignore")
        
        return True
    else:
        print("\n Opération annulée")
        return False


def test_connection(config):
    """Teste la connexion à PostgreSQL"""
    
    print("\n" + "=" * 60)
    print("TEST DE CONNEXION")
    print("=" * 60)
    
    try:
        import psycopg2
        
        conn = psycopg2.connect(
            user=config['DB_USER'],
            password=config['DB_PASSWORD'],
            host=config['DB_HOST'],
            port=config['DB_PORT'],
            database='postgres'  # Base par défaut pour tester
        )
        
        cursor = conn.cursor()
        cursor.execute("SELECT version();")
        version = cursor.fetchone()[0]
        
        print(f"\n Connexion réussie!")
        print(f"PostgreSQL version: {version[:50]}...")
        
        cursor.close()
        conn.close()
        
        return True
        
    except ImportError:
        print("\n  Module psycopg2 non installé")
        print("   Installez-le avec: pip install psycopg2-binary")
        return False
        
    except Exception as e:
        print(f"\n Erreur de connexion: {e}")
        print("\nVérifiez que:")
        print("  - PostgreSQL est démarré")
        print("  - Le mot de passe est correct")
        print("  - L'utilisateur existe")
        return False


def create_database(db_name):
    """Crée la base de données"""
    
    print("\n" + "=" * 60)
    print("CRÉATION DE LA BASE DE DONNÉES")
    print("=" * 60)
    
    print(f"\nPour créer la base '{db_name}', exécutez ces commandes:")
    print("\n1. Ouvrez un terminal et connectez-vous à PostgreSQL:")
    print(f"   psql -U postgres")
    print("\n2. Créez la base de données:")
    print(f"   CREATE DATABASE {db_name};")
    print("\n3. Vérifiez qu'elle existe:")
    print("   \\l")
    print("\n4. Quittez:")
    print("   \\q")
    
    print("\nOu utilisez pgAdmin (interface graphique) pour créer la base.")


def main():
    """Fonction principale"""
    
    print("\n Configuration rapide de PostgreSQL pour votre projet\n")
    
    # Vérification si .env existe déjà
    if Path('.env').exists():
        print("  Un fichier .env existe déjà!")
        overwrite = input("   Voulez-vous le remplacer? (o/n): ").strip().lower()
        if overwrite != 'o':
            print("\n Opération annulée")
            return
    
    # Création du fichier .env
    if not create_env_file():
        return
    
    # Lecture de la config
    from dotenv import load_dotenv
    load_dotenv()
    
    config = {
        'DB_USER': os.getenv('DB_USER'),
        'DB_PASSWORD': os.getenv('DB_PASSWORD'),
        'DB_HOST': os.getenv('DB_HOST'),
        'DB_PORT': os.getenv('DB_PORT'),
        'DB_NAME': os.getenv('DB_NAME')
    }
    
    # Test de connexion
    test = input("\n Voulez-vous tester la connexion maintenant? (o/n): ").strip().lower()
    if test == 'o':
        if test_connection(config):
            # Instructions pour créer la base
            create_db = input("\n Voulez-vous voir comment créer la base de données? (o/n): ").strip().lower()
            if create_db == 'o':
                create_database(config['DB_NAME'])
    
    print("\n" + "=" * 60)
    print(" CONFIGURATION TERMINÉE")
    print("=" * 60)
    print("\n Prochaines étapes:")
    print("  1. Créez la base de données (si pas déjà fait)")
    print("  2. Lancez: python setup_database.py")
    print("  3. Placez vos CSV dans src/data/")
    print("\n Votre configuration est sauvegardée dans .env")


if __name__ == "__main__":
    main()