"""
Configuration de la base de données PostgreSQL
Fichier: src/database/config.py
"""

import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import logging

# Charge les variables d'environnement
load_dotenv()

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('database_operations.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class DatabaseConfig:
    """Configuration centralisée de la base de données"""
    
    # Paramètres de connexion depuis variables d'environnement
    DB_USER = os.getenv('DB_USER', 'postgres')
    DB_PASSWORD = os.getenv('DB_PASSWORD', 'postgres')
    DB_HOST = os.getenv('DB_HOST', 'localhost')
    DB_PORT = os.getenv('DB_PORT', '5432')
    DB_NAME = os.getenv('DB_NAME', 'ma_base_rh')
    
    # Construction de l'URL de connexion
    DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    
    # Options de configuration du pool de connexions
    ENGINE_OPTIONS = {
        'pool_size': 10,
        'max_overflow': 20,
        'pool_pre_ping': True,  # Vérifie la connexion avant utilisation
        'pool_recycle': 3600,   # Recycle les connexions toutes les heures
        'echo': False           # Mettre à True pour voir les requêtes SQL
    }
    
    @classmethod
    def get_engine(cls):
        """Crée et retourne un moteur SQLAlchemy"""
        try:
            engine = create_engine(cls.DATABASE_URL, **cls.ENGINE_OPTIONS)
            logger.info(f" Connexion établie à la base: {cls.DB_NAME}")
            return engine
        except Exception as e:
            logger.error(f" Erreur de connexion à la base: {e}")
            raise
    
    @classmethod
    def get_session(cls):
        """Crée et retourne une session SQLAlchemy"""
        engine = cls.get_engine()
        Session = sessionmaker(bind=engine)
        return Session()
    
    @classmethod
    def test_connection(cls):
        """Teste la connexion à la base de données"""
        try:
            engine = cls.get_engine()
            with engine.connect() as connection:
                result = connection.execute("SELECT version();")
                version = result.fetchone()[0]
                logger.info(f" PostgreSQL version: {version}")
                return True
        except Exception as e:
            logger.error(f" Test de connexion échoué: {e}")
            return False


# Instance globale pour utilisation dans d'autres modules
db_config = DatabaseConfig()