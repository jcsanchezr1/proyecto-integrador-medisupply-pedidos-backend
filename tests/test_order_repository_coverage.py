"""
Tests para mejorar coverage de OrderRepository usando patch estratégico
"""
import pytest
from unittest.mock import MagicMock, patch
from datetime import datetime
from app.repositories.order_repository import OrderRepository
from app.models.order import Order, OrderStatus
from sqlalchemy.exc import SQLAlchemyError


class TestOrderRepositoryCoverage:
    """Tests para mejorar coverage de OrderRepository"""
    
    def setup_method(self):
        """Setup para cada test"""
        self.mock_session = MagicMock()
        self.repository = OrderRepository(self.mock_session)
    
    @patch('app.repositories.order_repository.OrderDB')
    def test_get_all_success(self, mock_order_db_class):
        """Test: get_all exitoso (líneas 21-25)"""
        # Crear mock de OrderDB
        mock_order_db = MagicMock()
        mock_order_db.id = 1
        mock_order_db.order_number = "PED-001"
        mock_order_db.client_id = 1
        mock_order_db.vendor_id = 1
        mock_order_db.status = OrderStatus.RECIBIDO
        mock_order_db.scheduled_delivery_date = datetime(2024, 1, 5)
        mock_order_db.assigned_truck = "TRUCK001"
        mock_order_db.created_at = datetime(2024, 1, 1)
        mock_order_db.updated_at = datetime(2024, 1, 1)
        
        # Mock de la sesión
        self.mock_session.query.return_value.all.return_value = [mock_order_db]
        
        result = self.repository.get_all()
        
        assert len(result) == 1
        assert result[0].order_number == "PED-001"
        self.mock_session.query.assert_called_once_with(mock_order_db_class)
    
    @patch('app.repositories.order_repository.OrderDB')
    def test_get_all_sqlalchemy_error(self, mock_order_db_class):
        """Test: get_all con SQLAlchemyError (líneas 21-25)"""
        self.mock_session.query.side_effect = SQLAlchemyError("Database error")
        
        with pytest.raises(Exception, match="Error al obtener pedidos"):
            self.repository.get_all()
    
    @patch('app.repositories.order_repository.OrderDB')
    def test_get_orders_with_items_by_client_success(self, mock_order_db_class):
        """Test: get_orders_with_items_by_client exitoso (líneas 29-37)"""
        # Crear mock de OrderDB
        mock_order_db = MagicMock()
        mock_order_db.id = 1
        mock_order_db.order_number = "PED-001"
        mock_order_db.client_id = 1
        mock_order_db.vendor_id = 1
        mock_order_db.status = OrderStatus.RECIBIDO
        mock_order_db.scheduled_delivery_date = datetime(2024, 1, 5)
        mock_order_db.assigned_truck = "TRUCK001"
        mock_order_db.created_at = datetime(2024, 1, 1)
        mock_order_db.updated_at = datetime(2024, 1, 1)
        mock_order_db.items = []
        
        # Mock de la sesión
        self.mock_session.query.return_value.filter.return_value.all.return_value = [mock_order_db]
        
        result = self.repository.get_orders_with_items_by_client(1)
        
        assert len(result) == 1
        assert result[0].order_number == "PED-001"
        self.mock_session.query.assert_called_once_with(mock_order_db_class)
    
    def test_get_orders_with_items_by_client_invalid_id(self):
        """Test: get_orders_with_items_by_client con ID inválido (líneas 29-37)"""
        with pytest.raises(Exception, match="Error al obtener pedidos del cliente"):
            self.repository.get_orders_with_items_by_client(0)
    
    @patch('app.repositories.order_repository.OrderDB')
    def test_get_orders_with_items_by_client_sqlalchemy_error(self, mock_order_db_class):
        """Test: get_orders_with_items_by_client con SQLAlchemyError (líneas 29-37)"""
        self.mock_session.query.side_effect = SQLAlchemyError("Database error")
        
        with pytest.raises(Exception, match="Error al obtener pedidos del cliente"):
            self.repository.get_orders_with_items_by_client(1)
    
    @patch('app.repositories.order_repository.OrderDB')
    def test_get_orders_with_items_by_vendor_success(self, mock_order_db_class):
        """Test: get_orders_with_items_by_vendor exitoso (líneas 41-49)"""
        # Crear mock de OrderDB
        mock_order_db = MagicMock()
        mock_order_db.id = 1
        mock_order_db.order_number = "PED-001"
        mock_order_db.client_id = 1
        mock_order_db.vendor_id = 1
        mock_order_db.status = OrderStatus.RECIBIDO
        mock_order_db.scheduled_delivery_date = datetime(2024, 1, 5)
        mock_order_db.assigned_truck = "TRUCK001"
        mock_order_db.created_at = datetime(2024, 1, 1)
        mock_order_db.updated_at = datetime(2024, 1, 1)
        mock_order_db.items = []
        
        # Mock de la sesión
        self.mock_session.query.return_value.filter.return_value.all.return_value = [mock_order_db]
        
        result = self.repository.get_orders_with_items_by_vendor(1)
        
        assert len(result) == 1
        assert result[0].order_number == "PED-001"
        self.mock_session.query.assert_called_once_with(mock_order_db_class)
    
    def test_get_orders_with_items_by_vendor_invalid_id(self):
        """Test: get_orders_with_items_by_vendor con ID inválido (líneas 41-49)"""
        with pytest.raises(Exception, match="Error al obtener pedidos del vendedor"):
            self.repository.get_orders_with_items_by_vendor(0)
    
    @patch('app.repositories.order_repository.OrderDB')
    def test_get_orders_with_items_by_vendor_sqlalchemy_error(self, mock_order_db_class):
        """Test: get_orders_with_items_by_vendor con SQLAlchemyError (líneas 41-49)"""
        self.mock_session.query.side_effect = SQLAlchemyError("Database error")
        
        with pytest.raises(Exception, match="Error al obtener pedidos del vendedor"):
            self.repository.get_orders_with_items_by_vendor(1)
    
    @patch('app.repositories.order_repository.OrderDB')
    def test_create_success(self, mock_order_db_class):
        """Test: create exitoso (líneas 53-68)"""
        # Crear order para crear
        order = Order(
            order_number="PED-001",
            client_id=1,
            vendor_id=1,
            status="Recibido",
            scheduled_delivery_date=datetime(2024, 1, 5),
            assigned_truck="TRUCK001"
        )
        
        # Mock de la sesión
        self.mock_session.add.return_value = None
        self.mock_session.commit.return_value = None
        self.mock_session.refresh.return_value = None
        
        # Mock del refresh para que establezca atributos
        def mock_refresh(obj):
            obj.id = 1
            obj.created_at = datetime(2024, 1, 1)
            obj.updated_at = datetime(2024, 1, 1)
        
        self.mock_session.refresh.side_effect = mock_refresh
        
        result = self.repository.create(order)
        
        # Verificar que se creó correctamente (el mock retorna un MagicMock)
        assert result is not None
        self.mock_session.add.assert_called_once()
        self.mock_session.commit.assert_called_once()
        self.mock_session.refresh.assert_called_once()
    
    @patch('app.repositories.order_repository.OrderDB')
    def test_create_sqlalchemy_error(self, mock_order_db_class):
        """Test: create con SQLAlchemyError (líneas 53-68)"""
        order = Order(
            order_number="PED-001",
            client_id=1,
            vendor_id=1,
            status="Recibido"
        )
        
        self.mock_session.add.side_effect = SQLAlchemyError("Database error")
        
        with pytest.raises(Exception, match="Error al crear pedido"):
            self.repository.create(order)
        
        self.mock_session.rollback.assert_called_once()
    
    @patch('app.repositories.order_repository.OrderDB')
    def test_get_by_id_success(self, mock_order_db_class):
        """Test: get_by_id exitoso (líneas 72-78)"""
        # Crear mock de OrderDB
        mock_order_db = MagicMock()
        mock_order_db.id = 1
        mock_order_db.order_number = "PED-001"
        mock_order_db.client_id = 1
        mock_order_db.vendor_id = 1
        mock_order_db.status = OrderStatus.RECIBIDO
        mock_order_db.scheduled_delivery_date = datetime(2024, 1, 5)
        mock_order_db.assigned_truck = "TRUCK001"
        mock_order_db.created_at = datetime(2024, 1, 1)
        mock_order_db.updated_at = datetime(2024, 1, 1)
        
        # Mock de la sesión
        self.mock_session.query.return_value.filter.return_value.first.return_value = mock_order_db
        
        result = self.repository.get_by_id(1)
        
        assert result is not None
        assert result.order_number == "PED-001"
        self.mock_session.query.assert_called_once_with(mock_order_db_class)
    
    @patch('app.repositories.order_repository.OrderDB')
    def test_get_by_id_not_found(self, mock_order_db_class):
        """Test: get_by_id no encontrado (líneas 72-78)"""
        self.mock_session.query.return_value.filter.return_value.first.return_value = None
        
        result = self.repository.get_by_id(1)
        
        assert result is None
        self.mock_session.query.assert_called_once_with(mock_order_db_class)
    
    @patch('app.repositories.order_repository.OrderDB')
    def test_get_by_id_sqlalchemy_error(self, mock_order_db_class):
        """Test: get_by_id con SQLAlchemyError (líneas 72-78)"""
        self.mock_session.query.side_effect = SQLAlchemyError("Database error")
        
        with pytest.raises(Exception, match="Error al obtener pedido"):
            self.repository.get_by_id(1)
    
    @patch('app.repositories.order_repository.OrderDB')
    def test_update_success(self, mock_order_db_class):
        """Test: update exitoso (líneas 82-98)"""
        # Crear order para actualizar
        order = Order(
            id=1,
            order_number="PED-001-UPDATED",
            client_id=1,
            vendor_id=1,
            status="En Proceso",
            scheduled_delivery_date=datetime(2024, 1, 6),
            assigned_truck="TRUCK002"
        )
        
        # Crear mock de OrderDB existente
        mock_order_db = MagicMock()
        mock_order_db.id = 1
        mock_order_db.order_number = "PED-001"
        mock_order_db.client_id = 1
        mock_order_db.vendor_id = 1
        mock_order_db.status = OrderStatus.RECIBIDO
        mock_order_db.scheduled_delivery_date = datetime(2024, 1, 5)
        mock_order_db.assigned_truck = "TRUCK001"
        mock_order_db.created_at = datetime(2024, 1, 1)
        mock_order_db.updated_at = datetime(2024, 1, 1)
        
        # Mock de la sesión
        self.mock_session.query.return_value.filter.return_value.first.return_value = mock_order_db
        self.mock_session.commit.return_value = None
        
        result = self.repository.update(order)
        
        assert result.order_number == "PED-001-UPDATED"
        self.mock_session.query.assert_called_once_with(mock_order_db_class)
        self.mock_session.commit.assert_called_once()
    
    @patch('app.repositories.order_repository.OrderDB')
    def test_update_not_found(self, mock_order_db_class):
        """Test: update no encontrado (líneas 82-98)"""
        order = Order(
            id=1,
            order_number="PED-001",
            client_id=1,
            vendor_id=1,
            status="Recibido"
        )
        
        self.mock_session.query.return_value.filter.return_value.first.return_value = None
        
        with pytest.raises(Exception, match="Pedido no encontrado"):
            self.repository.update(order)
    
    @patch('app.repositories.order_repository.OrderDB')
    def test_update_sqlalchemy_error(self, mock_order_db_class):
        """Test: update con SQLAlchemyError (líneas 82-98)"""
        order = Order(
            id=1,
            order_number="PED-001",
            client_id=1,
            vendor_id=1,
            status="Recibido"
        )
        
        self.mock_session.query.side_effect = SQLAlchemyError("Database error")
        
        with pytest.raises(Exception, match="Error al actualizar pedido"):
            self.repository.update(order)
        
        self.mock_session.rollback.assert_called_once()
    
    @patch('app.repositories.order_repository.OrderDB')
    @patch('app.repositories.order_repository.OrderItemDB')
    def test_delete_success(self, mock_order_item_db_class, mock_order_db_class):
        """Test: delete exitoso (líneas 102-115)"""
        # Crear mock de OrderDB existente
        mock_order_db = MagicMock()
        mock_order_db.id = 1
        
        # Mock de la sesión
        self.mock_session.query.return_value.filter.return_value.first.return_value = mock_order_db
        self.mock_session.query.return_value.filter.return_value.delete.return_value = 1
        self.mock_session.delete.return_value = None
        self.mock_session.commit.return_value = None
        
        result = self.repository.delete(1)
        
        assert result is True
        self.mock_session.query.assert_called()
        self.mock_session.delete.assert_called_once_with(mock_order_db)
        self.mock_session.commit.assert_called_once()
    
    @patch('app.repositories.order_repository.OrderDB')
    def test_delete_not_found(self, mock_order_db_class):
        """Test: delete no encontrado (líneas 102-115)"""
        self.mock_session.query.return_value.filter.return_value.first.return_value = None
        
        result = self.repository.delete(1)
        
        assert result is False
        self.mock_session.query.assert_called_once_with(mock_order_db_class)
    
    @patch('app.repositories.order_repository.OrderDB')
    def test_delete_sqlalchemy_error(self, mock_order_db_class):
        """Test: delete con SQLAlchemyError (líneas 102-115)"""
        self.mock_session.query.side_effect = SQLAlchemyError("Database error")
        
        with pytest.raises(Exception, match="Error al eliminar pedido"):
            self.repository.delete(1)
        
        self.mock_session.rollback.assert_called_once()
    
    @patch('app.repositories.order_repository.OrderDB')
    @patch('app.repositories.order_repository.OrderItemDB')
    def test_delete_all_success(self, mock_order_item_db_class, mock_order_db_class):
        """Test: delete_all exitoso (líneas 119-128)"""
        # Mock de la sesión
        self.mock_session.query.return_value.count.return_value = 5
        self.mock_session.query.return_value.delete.return_value = 5
        self.mock_session.commit.return_value = None
        
        result = self.repository.delete_all()
        
        assert result == 5
        self.mock_session.query.assert_called()
        self.mock_session.commit.assert_called_once()
    
    @patch('app.repositories.order_repository.OrderDB')
    def test_delete_all_sqlalchemy_error(self, mock_order_db_class):
        """Test: delete_all con SQLAlchemyError (líneas 119-128)"""
        self.mock_session.query.side_effect = SQLAlchemyError("Database error")
        
        with pytest.raises(Exception, match="Error al eliminar todos los pedidos"):
            self.repository.delete_all()
        
        self.mock_session.rollback.assert_called_once()
