"""
Configuración de base de datos
"""
import os
import logging
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from .settings import get_config

logger = logging.getLogger(__name__)

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

def auto_close_session(func):
    """Decorador que automáticamente cierra la sesión después de ejecutar el método"""
    def wrapper(self, *args, **kwargs):

        is_mocked = False
        if hasattr(self, 'order_service'):
            service_class = self.order_service.__class__
            is_mocked = 'mock' in service_class.__module__.lower() or 'Mock' in service_class.__name__

        if is_mocked:
            logger.debug("Servicio mockeado detectado, saltando recreacion en decorador")
            return func(self, *args, **kwargs)

        if hasattr(self, 'order_repository') and hasattr(self.order_repository, 'session'):
            try:
                self.order_repository.session.close()
                logger.debug("Sesion cerrada en decorador")
            except Exception as e:
                logger.warning(f"Error cerrando sesion existente: {e}")

        session = SessionLocal()
        try:
            from ..repositories.order_repository import OrderRepository
            from ..services.order_service import OrderService
            
            self.order_repository = OrderRepository(session)
            self.order_service = OrderService(self.order_repository)
            
            logger.debug("Nueva sesion creada en decorador")

            return func(self, *args, **kwargs)
        finally:
            try:
                session.close()
                logger.debug("Sesion cerrada en finally del decorador")
            except Exception as e:
                logger.warning(f"Error cerrando sesion en finally: {e}")
    
    return wrapper
