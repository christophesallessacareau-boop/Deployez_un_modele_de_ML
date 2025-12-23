"""
Gestionnaire de base de données PostgreSQL avec traçabilité complète
Fichier: src/database/db_manager.py
"""

import pandas as pd
from sqlalchemy import inspect
from datetime import datetime
import logging
import json
import hashlib
from pathlib import Path
from typing import Optional, Dict, Any, List

from .config import db_config
from .models import Base, OperationLog, APIInteractionLog, DataAccessLog, ModelPredictionLog

logger = logging.getLogger(__name__)


class DatabaseManager:
    """Gestionnaire principal de la base de données avec traçabilité"""
    
    def __init__(self, custom_engine=None):
        """
        Initialise le gestionnaire
        
        Args:
            custom_engine: Moteur SQLAlchemy personnalisé (optionnel)
        """
        self.engine = custom_engine or db_config.get_engine()
        logger.info("DatabaseManager initialisé")
    
    def create_all_tables(self):
        """Crée toutes les tables incluant les tables de traçabilité"""
        try:
            Base.metadata.create_all(self.engine)
            logger.info("✓ Tables de traçabilité créées avec succès")
            return True
        except Exception as e:
            logger.error(f"✗ Erreur lors de la création des tables: {e}")
            raise
    
    def log_operation(self, operation_type: str, table_name: str = None,
                     rows_affected: int = 0, status: str = "SUCCESS",
                     error_message: str = None, execution_time_ms: float = 0,
                     input_data: Any = None, metadata: Dict = None):
        """Enregistre une opération dans les logs"""
        session = db_config.get_session()
        try:
            input_hash = None
            if input_data is not None:
                input_str = json.dumps(input_data, default=str)
                input_hash = hashlib.sha256(input_str.encode()).hexdigest()
            
            log_entry = OperationLog(
                operation_type=operation_type,
                table_name=table_name,
                rows_affected=rows_affected,
                status=status,
                error_message=error_message,
                execution_time_ms=execution_time_ms,
                input_hash=input_hash,
                metadata_json=json.dumps(metadata) if metadata else None
            )
            session.add(log_entry)
            session.commit()
        except Exception as e:
            logger.error(f"Erreur lors de l'enregistrement du log: {e}")
            session.rollback()
        finally:
            session.close()
    
    def log_api_interaction(self, endpoint: str, input_data: Dict, 
                           output_data: Dict, model_version: str = None,
                           user_id: str = "anonymous", success: bool = True,
                           execution_time_ms: float = 0):
        """Enregistre une interaction avec l'API ML"""
        session = db_config.get_session()
        try:
            log_entry = APIInteractionLog(
                api_endpoint=endpoint,
                request_method="POST",
                input_data=json.dumps(input_data),
                output_data=json.dumps(output_data),
                model_version=model_version,
                execution_time_ms=execution_time_ms,
                user_id=user_id,
                success=success
            )
            session.add(log_entry)
            session.commit()
            logger.info(f"✓ Interaction API loggée: {endpoint}")
        except Exception as e:
            logger.error(f"Erreur lors du log API: {e}")
            session.rollback()
        finally:
            session.close()
    
    def log_model_prediction(self, model_name: str, input_features: Dict,
                            prediction: Any, confidence_score: float = None,
                            model_version: str = None, user_id: str = None,
                            execution_time_ms: float = 0):
        """Enregistre une prédiction du modèle ML"""
        session = db_config.get_session()
        try:
            log_entry = ModelPredictionLog(
                model_name=model_name,
                model_version=model_version,
                input_features=json.dumps(input_features),
                prediction=json.dumps(prediction),
                confidence_score=confidence_score,
                execution_time_ms=execution_time_ms,
                user_id=user_id
            )
            session.add(log_entry)
            session.commit()
            logger.info(f"✓ Prédiction loggée: {model_name}")
        except Exception as e:
            logger.error(f"Erreur lors du log de prédiction: {e}")
            session.rollback()
        finally:
            session.close()
    
    def import_csv_to_table(self, csv_path: str, table_name: str, 
                           if_exists: str = 'replace') -> int:
        """
        Importe un fichier CSV dans une table PostgreSQL
        
        Args:
            csv_path: Chemin du fichier CSV
            table_name: Nom de la table destination
            if_exists: 'replace', 'append', ou 'fail'
        
        Returns:
            Nombre de lignes importées
        """
        start_time = datetime.now()
        
        try:
            # Lecture du CSV avec gestion robuste
            df = pd.read_csv(csv_path, encoding='utf-8')
            df.columns = df.columns.str.strip()
            
            logger.info(f"Lecture de {csv_path}: {len(df)} lignes, {len(df.columns)} colonnes")
            
            # Import dans PostgreSQL
            df.to_sql(table_name, self.engine, if_exists=if_exists, index=False)
            
            execution_time = (datetime.now() - start_time).total_seconds() * 1000
            
            # Log de l'opération
            self.log_operation(
                operation_type='IMPORT_CSV',
                table_name=table_name,
                rows_affected=len(df),
                status='SUCCESS',
                execution_time_ms=execution_time,
                metadata={'csv_path': csv_path, 'columns': list(df.columns)}
            )
            
            logger.info(f"✓ Import réussi: {len(df)} lignes dans '{table_name}'")
            return len(df)
            
        except Exception as e:
            execution_time = (datetime.now() - start_time).total_seconds() * 1000
            self.log_operation(
                operation_type='IMPORT_CSV',
                table_name=table_name,
                status='ERROR',
                error_message=str(e),
                execution_time_ms=execution_time
            )
            logger.error(f"✗ Erreur lors de l'import de {csv_path}: {e}")
            raise
    
    def merge_tables(self, tables: List[str], output_table: str, 
                    join_key: str, how: str = 'inner') -> int:
        """
        Fusionne plusieurs tables sur une clé commune
        
        Args:
            tables: Liste des noms de tables à fusionner
            output_table: Nom de la table résultante
            join_key: Colonne clé pour la jointure
            how: Type de jointure ('inner', 'outer', 'left', 'right')
        
        Returns:
            Nombre de lignes dans la table fusionnée
        """
        start_time = datetime.now()
        
        try:
            # Lecture des tables
            dfs = []
            for table in tables:
                df = pd.read_sql_table(table, self.engine)
                dfs.append(df)
                logger.info(f"Table '{table}' chargée: {len(df)} lignes")
            
            # Fusion progressive
            merged_df = dfs[0]
            for df in dfs[1:]:
                merged_df = pd.merge(merged_df, df, on=join_key, how=how, suffixes=('', '_dup'))
            
            # Suppression des colonnes dupliquées
            merged_df = merged_df.loc[:, ~merged_df.columns.str.endswith('_dup')]
            
            # Sauvegarde dans PostgreSQL
            merged_df.to_sql(output_table, self.engine, if_exists='replace', index=False)
            
            execution_time = (datetime.now() - start_time).total_seconds() * 1000
            
            self.log_operation(
                operation_type='MERGE',
                table_name=output_table,
                rows_affected=len(merged_df),
                status='SUCCESS',
                execution_time_ms=execution_time,
                metadata={
                    'source_tables': tables,
                    'join_key': join_key,
                    'join_type': how,
                    'final_columns': list(merged_df.columns)
                }
            )
            
            logger.info(f"✓ Fusion réussie: {len(merged_df)} lignes dans '{output_table}'")
            return len(merged_df)
            
        except Exception as e:
            execution_time = (datetime.now() - start_time).total_seconds() * 1000
            self.log_operation(
                operation_type='MERGE',
                table_name=output_table,
                status='ERROR',
                error_message=str(e),
                execution_time_ms=execution_time
            )
            logger.error(f"✗ Erreur lors de la fusion: {e}")
            raise
    
    def execute_query(self, query: str, user_id: str = "system") -> pd.DataFrame:
        """
        Exécute une requête SQL avec traçabilité
        
        Args:
            query: Requête SQL à exécuter
            user_id: Identifiant de l'utilisateur
        
        Returns:
            DataFrame avec les résultats
        """
        start_time = datetime.now()
        session = db_config.get_session()
        
        try:
            result_df = pd.read_sql_query(query, self.engine)
            
            # Log de l'accès aux données
            access_log = DataAccessLog(
                user_id=user_id,
                table_accessed="multiple" if "JOIN" in query.upper() else "unknown",
                access_type="READ",
                query_executed=query,
                rows_accessed=len(result_df),
                granted=True
            )
            session.add(access_log)
            session.commit()
            
            logger.info(f"✓ Requête exécutée: {len(result_df)} lignes retournées")
            return result_df
            
        except Exception as e:
            logger.error(f"✗ Erreur lors de l'exécution de la requête: {e}")
            
            access_log = DataAccessLog(
                user_id=user_id,
                table_accessed="unknown",
                access_type="READ",
                query_executed=query,
                rows_accessed=0,
                granted=False,
                denied_reason=str(e)
            )
            session.add(access_log)
            session.commit()
            raise
        finally:
            session.close()
    
    def get_table_info(self, table_name: str) -> Optional[Dict]:
        """Récupère les informations sur une table"""
        inspector = inspect(self.engine)
        
        if table_name not in inspector.get_table_names():
            return None
        
        columns = inspector.get_columns(table_name)
        pk_constraint = inspector.get_pk_constraint(table_name)
        
        return {
            'table_name': table_name,
            'columns': [
                {
                    'name': col['name'],
                    'type': str(col['type']),
                    'nullable': col['nullable']
                }
                for col in columns
            ],
            'primary_key': pk_constraint.get('constrained_columns', [])
        }
    
    def list_all_tables(self) -> List[str]:
        """Liste toutes les tables de la base"""
        inspector = inspect(self.engine)
        return inspector.get_table_names()
    
    def get_operation_logs(self, limit: int = 10) -> pd.DataFrame:
        """Récupère les dernières opérations loggées"""
        query = f"""
        SELECT timestamp, operation_type, table_name, status, 
               rows_affected, execution_time_ms
        FROM operation_logs 
        ORDER BY timestamp DESC 
        LIMIT {limit}
        """
        return pd.read_sql_query(query, self.engine)
    
    def get_api_logs(self, limit: int = 10) -> pd.DataFrame:
        """Récupère les dernières interactions API"""
        query = f"""
        SELECT timestamp, api_endpoint, user_id, model_version,
               success, execution_time_ms
        FROM api_interaction_logs 
        ORDER BY timestamp DESC 
        LIMIT {limit}
        """
        return pd.read_sql_query(query, self.engine)