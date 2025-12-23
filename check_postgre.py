"""
Script de diagnostic PostgreSQL
Fichier: check_postgres.py

Vérifie si PostgreSQL est installé et accessible
"""

import subprocess
import sys
import platform


def check_postgres_installed():
    """Vérifie si PostgreSQL est installé"""
    
    print("=" * 60)
    print("1️  VÉRIFICATION DE L'INSTALLATION")
    print("=" * 60)
    
    commands_to_try = ['psql --version', 'postgres --version']
    
    for cmd in commands_to_try:
        try:
            result = subprocess.run(
                cmd.split(),
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0:
                print(f"\n PostgreSQL est installé!")
                print(f"   Version: {result.stdout.strip()}")
                return True
        except (subprocess.TimeoutExpired, FileNotFoundError):
            continue
    
    print("\n PostgreSQL ne semble pas installé")
    print("\n Pour installer PostgreSQL:")
    
    os_type = platform.system()
    if os_type == "Windows":
        print("   Windows: https://www.postgresql.org/download/windows/")
    elif os_type == "Darwin":
        print("   Mac: brew install postgresql")
        print("        brew services start postgresql")
    elif os_type == "Linux":
        print("   Linux: sudo apt install postgresql postgresql-contrib")
    
    return False


def check_postgres_running():
    """Vérifie si PostgreSQL est démarré"""
    
    print("\n" + "=" * 60)
    print("2️  VÉRIFICATION DU SERVICE")
    print("=" * 60)
    
    os_type = platform.system()
    
    try:
        if os_type == "Windows":
            # Sur Windows, vérifie via sc query
            result = subprocess.run(
                ['sc', 'query', 'postgresql-x64-15'],  # Ajustez le numéro de version
                capture_output=True,
                text=True,
                timeout=5
            )
            if 'RUNNING' in result.stdout:
                print("\n Le service PostgreSQL est démarré")
                return True
            else:
                print("\n Le service PostgreSQL n'est pas démarré")
                print("   Démarrez-le dans les Services Windows (services.msc)")
                return False
                
        elif os_type == "Darwin":
            # Sur Mac avec Homebrew
            result = subprocess.run(
                ['brew', 'services', 'list'],
                capture_output=True,
                text=True,
                timeout=5
            )
            if 'postgresql' in result.stdout and 'started' in result.stdout:
                print("\n Le service PostgreSQL est démarré")
                return True
            else:
                print("\n  Le service PostgreSQL n'est pas démarré")
                print("   Démarrez-le avec: brew services start postgresql")
                return False
                
        elif os_type == "Linux":
            # Sur Linux
            result = subprocess.run(
                ['systemctl', 'is-active', 'postgresql'],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.stdout.strip() == 'active':
                print("\n Le service PostgreSQL est démarré")
                return True
            else:
                print("\n  Le service PostgreSQL n'est pas démarré")
                print("   Démarrez-le avec: sudo systemctl start postgresql")
                return False
    
    except Exception as e:
        print(f"\n  Impossible de vérifier le statut du service")
        print("   Vérifiez manuellement que PostgreSQL est démarré")
        return None


def test_connection_interactive():
    """Teste la connexion de manière interactive"""
    
    print("\n" + "=" * 60)
    print("3️  TEST DE CONNEXION")
    print("=" * 60)
    
    print("\nEssayons de nous connecter à PostgreSQL...")
    print("(L'utilisateur par défaut est 'postgres')\n")
    
    # Demande les credentials
    user = input("Nom d'utilisateur [postgres]: ").strip() or "postgres"
    
    import getpass
    password = getpass.getpass("Mot de passe: ")
    
    if not password:
        print("\n  Mot de passe vide - Impossible de tester")
        return False
    
    # Test avec psycopg2
    try:
        import psycopg2
        
        print("\nConnexion en cours...")
        conn = psycopg2.connect(
            user=user,
            password=password,
            host='localhost',
            port='5432',
            database='postgres'  # Base par défaut
        )
        
        cursor = conn.cursor()
        cursor.execute("SELECT version();")
        version = cursor.fetchone()[0]
        
        cursor.execute("SELECT current_user;")
        current_user = cursor.fetchone()[0]
        
        print("\n" + "=" * 60)
        print(" CONNEXION RÉUSSIE!")
        print("=" * 60)
        print(f"\nUtilisateur connecté: {current_user}")
        print(f"PostgreSQL: {version[:60]}...")
        
        # Liste des bases
        cursor.execute("""
            SELECT datname FROM pg_database 
            WHERE datistemplate = false;
        """)
        databases = cursor.fetchall()
        
        print(f"\nBases de données disponibles:")
        for db in databases:
            print(f"  • {db[0]}")
        
        cursor.close()
        conn.close()
        
        # Proposer de créer le .env
        print("\n" + "=" * 60)
        create_env = input("\n Voulez-vous créer le fichier .env avec ces paramètres? (o/n): ").strip().lower()
        
        if create_env == 'o':
            db_name = input("\nNom de la base de données à utiliser [ma_base_rh]: ").strip() or "ma_base_rh"
            
            env_content = f"""# Configuration de la base de données PostgreSQL
# Généré par check_postgres.py

DB_USER={user}
DB_PASSWORD={password}
DB_HOST=localhost
DB_PORT=5432
DB_NAME={db_name}
"""
            
            with open('.env', 'w', encoding='utf-8') as f:
                f.write(env_content)
            
            print(f"\n Fichier .env créé!")
            print(f"   Base configurée: {db_name}")
            print("\n  N'oubliez pas de créer cette base si elle n'existe pas:")
            print(f"   psql -U {user}")
            print(f"   CREATE DATABASE {db_name};")
        
        return True
        
    except ImportError:
        print("\n  Module psycopg2 non installé")
        print("   Installez-le avec: pip install psycopg2-binary")
        return False
        
    except Exception as e:
        print("\n" + "=" * 60)
        print(" ÉCHEC DE CONNEXION")
        print("=" * 60)
        print(f"\nErreur: {e}")
        print("\n Causes possibles:")
        print("  1. Mot de passe incorrect")
        print("  2. L'utilisateur n'existe pas")
        print("  3. PostgreSQL n'est pas démarré")
        print("  4. Problème de configuration pg_hba.conf")
        
        return False


def show_summary():
    """Affiche un résumé des informations"""
    
    print("\n" + "=" * 60)
    print(" RÉSUMÉ")
    print("=" * 60)
    
    print("""
 UTILISATEUR PostgreSQL:
 FICHIER .ENV:
   DB_USER=postgres         ← Utilisateur
   DB_PASSWORD=???          ← mot de passe
   DB_HOST=localhost        ← Connexion locale
   DB_PORT=5432            ← Port par défaut
   DB_NAME=ma_base_rh      ←  crée dans PostgreSQL
""")


def main():
    """Fonction principale"""
    
    print("\n DIAGNOSTIC PostgreSQL\n")
    
    # Vérifications
    installed = check_postgres_installed()
    
    if installed:
        running = check_postgres_running()
        
        if running or running is None:
            test = input("\n Voulez-vous tester la connexion? (o/n): ").strip().lower()
            if test == 'o':
                test_connection_interactive()
    
    # Résumé
    show_summary()
    
    print("\n" + "=" * 60)
    print(" PROCHAINES ÉTAPES")
    print("=" * 60)
    print("""
1. Assurez-vous que PostgreSQL est installé et démarré
2. Testez votre connexion avec ce script
3. Créez le fichier .env avec vos credentials
4. Lancez: python setup_database.py
""")


if __name__ == "__main__":
    main()