"""
Configuración de base de datos
"""
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from .settings import get_config

config = get_config()

# URL de conexión a la base de datos
DATABASE_URL = os.getenv('DATABASE_URL', 'postgresql+psycopg2://medisupply_local_user:medisupply_local_password@localhost:5432/medisupply_local_db')

# Crear engine
engine = create_engine(DATABASE_URL, echo=config.DEBUG)

# Crear session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db_session():
    """Obtiene una sesión de base de datos"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def create_tables():
    """Crea las tablas en la base de datos"""
    from ..models.db_models import Base
    Base.metadata.create_all(bind=engine)
