"""
Modèles SQLAlchemy pour la traçabilité et les logs
Fichier: src/database/models.py
"""

from sqlalchemy import Column, Integer, String, Float, DateTime, Text, Boolean
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()


class OperationLog(Base):
    """Table de traçabilité de toutes les opérations sur la base"""
    __tablename__ = 'operation_logs'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    timestamp = Column(DateTime, default=datetime.now, nullable=False, index=True)
    operation_type = Column(String(50), nullable=False, index=True)
    table_name = Column(String(100), index=True)
    user_context = Column(String(100))
    rows_affected = Column(Integer)
    status = Column(String(20), nullable=False)
    error_message = Column(Text)
    execution_time_ms = Column(Float)
    input_hash = Column(String(64))
    metadata_json = Column(Text)
    
    def __repr__(self):
        return f"<OperationLog(id={self.id}, type={self.operation_type}, status={self.status})>"


class APIInteractionLog(Base):
    """Table de traçabilité des interactions avec l'API ML"""
    __tablename__ = 'api_interaction_logs'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    timestamp = Column(DateTime, default=datetime.now, nullable=False, index=True)
    api_endpoint = Column(String(200))
    request_method = Column(String(10))
    input_data = Column(Text)  # JSON des features du modèle
    output_data = Column(Text)  # JSON des prédictions
    model_version = Column(String(50))  # Version du modèle utilisé
    status_code = Column(Integer)
    execution_time_ms = Column(Float)
    user_id = Column(String(100), index=True)
    ip_address = Column(String(45))
    success = Column(Boolean, default=True)
    
    def __repr__(self):
        return f"<APIInteractionLog(id={self.id}, endpoint={self.api_endpoint})>"


class DataAccessLog(Base):
    """Table de traçabilité des accès aux données sensibles"""
    __tablename__ = 'data_access_logs'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    timestamp = Column(DateTime, default=datetime.now, nullable=False, index=True)
    user_id = Column(String(100), nullable=False, index=True)
    table_accessed = Column(String(100), nullable=False, index=True)
    access_type = Column(String(20), nullable=False)  # READ, WRITE, DELETE
    query_executed = Column(Text)
    rows_accessed = Column(Integer)
    granted = Column(Boolean, default=True)
    denied_reason = Column(Text)
    
    def __repr__(self):
        return f"<DataAccessLog(id={self.id}, user={self.user_id}, table={self.table_accessed})>"


class ModelPredictionLog(Base):
    """Table pour logger les prédictions du modèle ML"""
    __tablename__ = 'model_prediction_logs'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    timestamp = Column(DateTime, default=datetime.now, nullable=False, index=True)
    model_name = Column(String(100), nullable=False)
    model_version = Column(String(50))
    input_features = Column(Text)  # JSON des features
    prediction = Column(Text)  # Résultat de la prédiction
    confidence_score = Column(Float)
    execution_time_ms = Column(Float)
    user_id = Column(String(100))
    
    def __repr__(self):
        return f"<ModelPredictionLog(id={self.id}, model={self.model_name})>"