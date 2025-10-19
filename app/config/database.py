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

def auto_close_session(func):
    """Decorador que automáticamente cierra la sesión después de ejecutar el método"""
    def wrapper(self, *args, **kwargs):
        # Cerrar la sesión existente si existe
        if hasattr(self, 'order_repository') and hasattr(self.order_repository, 'session'):
            try:
                self.order_repository.session.close()
                print(f"Sesión cerrada en decorador")
            except Exception as e:
                print(f"Error cerrando sesión existente: {e}")
        
        # Crear nueva sesión
        session = SessionLocal()
        try:
            # Recrear repositorio y servicio con nueva sesión
            from ..repositories.order_repository import OrderRepository
            from ..services.order_service import OrderService
            
            self.order_repository = OrderRepository(session)
            self.order_service = OrderService(self.order_repository)
            
            print(f"Nueva sesión creada en decorador")
            
            # Ejecutar el método original
            return func(self, *args, **kwargs)
        finally:
            # Cerrar la sesión automáticamente
            try:
                session.close()
                print(f"🔒 Sesión cerrada en finally del decorador")
            except Exception as e:
                print(f"Error cerrando sesión en finally: {e}")
    
    return wrapper
