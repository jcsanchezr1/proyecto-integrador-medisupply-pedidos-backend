"""
Modelos de base de datos para pedidos
"""
from sqlalchemy import Column, Integer, String, DateTime, Float, ForeignKey, Text, Enum
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime
import enum

Base = declarative_base()


class OrderStatus(enum.Enum):
    """Estados válidos para un pedido"""
    RECIBIDO = "Recibido"
    EN_PREPARACION = "En Preparación"
    EN_TRANSITO = "En Tránsito"
    ENTREGADO = "Entregado"
    DEVUELTO = "Devuelto"


class OrderDB(Base):
    """Modelo de base de datos para pedidos"""
    __tablename__ = 'orders'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    order_number = Column(String(20), unique=True, nullable=False)
    client_id = Column(String(36), nullable=False)
    vendor_id = Column(String(36), nullable=False)
    status = Column(Enum(OrderStatus), nullable=False, default=OrderStatus.RECIBIDO)
    scheduled_delivery_date = Column(DateTime, nullable=True)
    assigned_truck = Column(String(50), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relación con items del pedido
    items = relationship("OrderItemDB", back_populates="order", cascade="all, delete-orphan")


class OrderItemDB(Base):
    """Modelo de base de datos para items del pedido"""
    __tablename__ = 'order_items'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    order_id = Column(Integer, ForeignKey('orders.id'), nullable=False)
    product_id = Column(Integer, nullable=False)
    quantity = Column(Integer, nullable=False)
    
    # Relación con el pedido
    order = relationship("OrderDB", back_populates="items")
