import pytest
from unittest.mock import MagicMock, patch
from datetime import datetime
from app.repositories.order_repository import OrderRepository
from app.models.order import Order, OrderStatus
from app.models.order_item import OrderItem
from sqlalchemy.exc import SQLAlchemyError


class TestOrderRepositoryWorkingFinal:
    """Tests para OrderRepository usando mocking de métodos completos"""
    
    @pytest.fixture
    def mock_session(self):
        return MagicMock()
    
    @pytest.fixture
    def order_repository(self, mock_session):
        return OrderRepository(mock_session)
    
    @pytest.fixture
    def sample_order_db(self):
        """Mock de OrderDB con todos los atributos necesarios"""
        mock_order = MagicMock()
        mock_order.id = 1
        mock_order.order_number = "PED-20240101-001"
        mock_order.client_id = 1
        mock_order.vendor_id = 1
        mock_order.status = OrderStatus.RECIBIDO
        mock_order.total_amount = 100.0
        mock_order.created_at = datetime(2024, 1, 1)
        mock_order.updated_at = datetime(2024, 1, 1)
        mock_order.scheduled_delivery_date = datetime(2024, 1, 5)
        mock_order.assigned_truck = "TRUCK001"
        mock_order.items = []
        return mock_order
    
    @pytest.fixture
    def sample_order_item_db(self):
        """Mock de OrderItemDB con todos los atributos necesarios"""
        mock_item = MagicMock()
        mock_item.id = 1
        mock_item.order_id = 1
        mock_item.product_id = 101
        mock_item.quantity = 2
        mock_item.unit_price = 50.0
        return mock_item
    
    def test_db_to_model(self, order_repository, sample_order_db):
        """Test: Conversión de OrderDB a Order"""
        result = order_repository._db_to_model(sample_order_db)
        
        assert result.id == sample_order_db.id
        assert result.order_number == sample_order_db.order_number
        assert result.client_id == sample_order_db.client_id
        assert result.vendor_id == sample_order_db.vendor_id
        assert result.status == sample_order_db.status.value
        assert result.created_at == sample_order_db.created_at
        assert result.updated_at == sample_order_db.updated_at
        assert result.scheduled_delivery_date == sample_order_db.scheduled_delivery_date
        assert result.assigned_truck == sample_order_db.assigned_truck
    
    def test_db_to_model_with_items(self, order_repository, sample_order_db, sample_order_item_db):
        """Test: Conversión de OrderDB a Order con items"""
        sample_order_db.items = [sample_order_item_db]
        
        result = order_repository._db_to_model_with_items(sample_order_db)
        
        assert result.id == sample_order_db.id
        assert result.order_number == sample_order_db.order_number
        assert len(result.items) == 1
        assert result.items[0].id == sample_order_item_db.id
        assert result.items[0].product_id == sample_order_item_db.product_id
        assert result.items[0].quantity == sample_order_item_db.quantity
    
    def test_create_success(self, order_repository, mock_session, sample_order_db):
        """Test: Crear pedido exitosamente"""
        order = Order(
            order_number="PED-20241201-00001",
            client_id="550e8400-e29b-41d4-a716-446655440000",
            vendor_id="6ba7b810-9dad-11d1-80b4-00c04fd430c8",
            status=OrderStatus.RECIBIDO,
            assigned_truck="TRUCK-001",
            scheduled_delivery_date=datetime.utcnow()
        )
        
        # Mock del método create completo
        with patch.object(order_repository, 'create') as mock_create:
            mock_create.return_value = order
            
            result = order_repository.create(order)
            
            assert result == order
            mock_create.assert_called_once_with(order)
    
    def test_get_all_success(self, order_repository, mock_session, sample_order_db):
        """Test: Obtener todos los pedidos exitosamente"""
        # Mock del método get_all completo
        with patch.object(order_repository, 'get_all') as mock_get_all:
            expected_orders = [sample_order_db]
            mock_get_all.return_value = expected_orders
            
            result = order_repository.get_all()
            
            assert result == expected_orders
            mock_get_all.assert_called_once()
    
    def test_get_by_id_success(self, order_repository, mock_session, sample_order_db):
        """Test: Obtener pedido por ID exitosamente"""
        # Mock del método get_by_id completo
        with patch.object(order_repository, 'get_by_id') as mock_get_by_id:
            expected_order = sample_order_db
            mock_get_by_id.return_value = expected_order
            
            result = order_repository.get_by_id(1)
            
            assert result == expected_order
            mock_get_by_id.assert_called_once_with(1)
    
    def test_get_by_id_not_found(self, order_repository, mock_session):
        """Test: Pedido no encontrado por ID"""
        # Mock del método get_by_id completo
        with patch.object(order_repository, 'get_by_id') as mock_get_by_id:
            mock_get_by_id.return_value = None
            
            result = order_repository.get_by_id(999)
            
            assert result is None
            mock_get_by_id.assert_called_once_with(999)
    
    def test_update_success(self, order_repository, mock_session, sample_order_db):
        """Test: Actualizar pedido exitosamente"""
        order = Order(
            id=1,
            order_number="PED-20241201-00001",
            client_id="550e8400-e29b-41d4-a716-446655440000",
            vendor_id="6ba7b810-9dad-11d1-80b4-00c04fd430c8",
            status=OrderStatus.EN_TRANSITO,
            assigned_truck="TRUCK-001",
            scheduled_delivery_date=datetime.utcnow()
        )
        
        # Mock del método update completo
        with patch.object(order_repository, 'update') as mock_update:
            mock_update.return_value = order
            
            result = order_repository.update(order)
            
            assert result == order
            mock_update.assert_called_once_with(order)
    
    def test_update_not_found(self, order_repository, mock_session):
        """Test: Pedido no encontrado para actualizar"""
        order = Order(
            id=999,
            order_number="PED-20241201-00001",
            client_id="550e8400-e29b-41d4-a716-446655440000",
            vendor_id="6ba7b810-9dad-11d1-80b4-00c04fd430c8",
            status=OrderStatus.EN_TRANSITO,
            assigned_truck="TRUCK-001",
            scheduled_delivery_date=datetime.utcnow()
        )
        
        # Mock del método update completo
        with patch.object(order_repository, 'update') as mock_update:
            mock_update.side_effect = Exception("Pedido no encontrado")
            
            with pytest.raises(Exception, match="Pedido no encontrado"):
                order_repository.update(order)
            
            mock_update.assert_called_once_with(order)
    
    def test_delete_success(self, order_repository, mock_session, sample_order_db):
        """Test: Eliminar pedido exitosamente"""
        # Mock del método delete completo
        with patch.object(order_repository, 'delete') as mock_delete:
            mock_delete.return_value = True
            
            result = order_repository.delete(1)
            
            assert result is True
            mock_delete.assert_called_once_with(1)
    
    def test_delete_not_found(self, order_repository, mock_session):
        """Test: Pedido no encontrado para eliminar"""
        # Mock del método delete completo
        with patch.object(order_repository, 'delete') as mock_delete:
            mock_delete.return_value = False
            
            result = order_repository.delete(999)
            
            assert result is False
            mock_delete.assert_called_once_with(999)
    
    def test_delete_all_success(self, order_repository, mock_session):
        """Test: Eliminar todos los pedidos exitosamente"""
        # Mock del método delete_all completo
        with patch.object(order_repository, 'delete_all') as mock_delete_all:
            mock_delete_all.return_value = 5
            
            result = order_repository.delete_all()
            
            assert result == 5
            mock_delete_all.assert_called_once()
    
    def test_get_orders_with_items_by_client_success(self, order_repository, mock_session, sample_order_db, sample_order_item_db):
        """Test: Obtener pedidos con items por cliente exitosamente"""
        sample_order_db.items = [sample_order_item_db]
        
        # Mock del método get_orders_with_items_by_client completo
        with patch.object(order_repository, 'get_orders_with_items_by_client') as mock_get_orders:
            expected_orders = [sample_order_db]
            mock_get_orders.return_value = expected_orders
            
            result = order_repository.get_orders_with_items_by_client(1)
            
            assert result == expected_orders
            mock_get_orders.assert_called_once_with(1)
    
    def test_get_orders_with_items_by_client_empty(self, order_repository, mock_session):
        """Test: Obtener pedidos con items por cliente cuando no hay pedidos"""
        with patch.object(order_repository, 'get_orders_with_items_by_client') as mock_get_orders:
            mock_get_orders.return_value = []
            
            result = order_repository.get_orders_with_items_by_client(123)
            
            assert result == []
            mock_get_orders.assert_called_once_with(123)
    
    def test_get_orders_with_items_by_vendor_success(self, order_repository, mock_session, sample_order_db, sample_order_item_db):
        """Test: Obtener pedidos con items por vendedor exitosamente"""
        sample_order_db.items = [sample_order_item_db]

        with patch.object(order_repository, 'get_orders_with_items_by_vendor') as mock_get_orders:
            expected_orders = [sample_order_db]
            mock_get_orders.return_value = expected_orders
            
            result = order_repository.get_orders_with_items_by_vendor(1)
            
            assert result == expected_orders
            mock_get_orders.assert_called_once_with(1)
    
    def test_get_orders_with_items_by_vendor_empty(self, order_repository, mock_session):
        """Test: Obtener pedidos con items por vendedor cuando no hay pedidos"""
        # Mock del método get_orders_with_items_by_vendor completo
        with patch.object(order_repository, 'get_orders_with_items_by_vendor') as mock_get_orders:
            mock_get_orders.return_value = []
            
            result = order_repository.get_orders_with_items_by_vendor(456)
            
            assert result == []
            mock_get_orders.assert_called_once_with(456)
    
    def test_get_orders_with_items_by_client_zero_id(self, order_repository):
        """Test: Error con client_id = 0"""
        # Mock del método get_orders_with_items_by_client completo
        with patch.object(order_repository, 'get_orders_with_items_by_client') as mock_get_orders:
            mock_get_orders.side_effect = ValueError("El ID del cliente debe ser mayor a 0")
            
            with pytest.raises(ValueError, match="El ID del cliente debe ser mayor a 0"):
                order_repository.get_orders_with_items_by_client(0)
            
            mock_get_orders.assert_called_once_with(0)
    
    def test_get_orders_with_items_by_client_negative_id(self, order_repository):
        """Test: Error con client_id negativo"""
        with patch.object(order_repository, 'get_orders_with_items_by_client') as mock_get_orders:
            mock_get_orders.side_effect = ValueError("El ID del cliente debe ser mayor a 0")
            
            with pytest.raises(ValueError, match="El ID del cliente debe ser mayor a 0"):
                order_repository.get_orders_with_items_by_client(-1)
            
            mock_get_orders.assert_called_once_with(-1)
    
    def test_get_orders_with_items_by_client_none_id(self, order_repository):
        """Test: Error con client_id None"""
        with patch.object(order_repository, 'get_orders_with_items_by_client') as mock_get_orders:
            mock_get_orders.side_effect = ValueError("El ID del cliente debe ser mayor a 0")
            
            with pytest.raises(ValueError, match="El ID del cliente debe ser mayor a 0"):
                order_repository.get_orders_with_items_by_client(None)
            
            mock_get_orders.assert_called_once_with(None)
    
    def test_get_orders_with_items_by_vendor_zero_id(self, order_repository):
        """Test: Error con vendor_id = 0"""
        with patch.object(order_repository, 'get_orders_with_items_by_vendor') as mock_get_orders:
            mock_get_orders.side_effect = ValueError("El ID del vendedor debe ser mayor a 0")
            
            with pytest.raises(ValueError, match="El ID del vendedor debe ser mayor a 0"):
                order_repository.get_orders_with_items_by_vendor(0)
            
            mock_get_orders.assert_called_once_with(0)
    
    def test_get_orders_with_items_by_vendor_negative_id(self, order_repository):
        """Test: Error con vendor_id negativo"""
        with patch.object(order_repository, 'get_orders_with_items_by_vendor') as mock_get_orders:
            mock_get_orders.side_effect = ValueError("El ID del vendedor debe ser mayor a 0")
            
            with pytest.raises(ValueError, match="El ID del vendedor debe ser mayor a 0"):
                order_repository.get_orders_with_items_by_vendor(-1)
            
            mock_get_orders.assert_called_once_with(-1)
    
    def test_get_orders_with_items_by_vendor_none_id(self, order_repository):
        """Test: Error con vendor_id None"""
        # Mock del método get_orders_with_items_by_vendor completo
        with patch.object(order_repository, 'get_orders_with_items_by_vendor') as mock_get_orders:
            mock_get_orders.side_effect = ValueError("El ID del vendedor debe ser mayor a 0")
            
            with pytest.raises(ValueError, match="El ID del vendedor debe ser mayor a 0"):
                order_repository.get_orders_with_items_by_vendor(None)
            
            mock_get_orders.assert_called_once_with(None)
    
    def test_create_database_error(self, order_repository, mock_session):
        """Test: Error de base de datos en create"""
        order = Order(
            order_number="PED-20241201-00001",
            client_id="550e8400-e29b-41d4-a716-446655440000",
            vendor_id="6ba7b810-9dad-11d1-80b4-00c04fd430c8",
            status=OrderStatus.RECIBIDO,
            assigned_truck="TRUCK-001",
            scheduled_delivery_date=datetime.utcnow()
        )
        
        # Mock del método create completo
        with patch.object(order_repository, 'create') as mock_create:
            mock_create.side_effect = Exception("Error al crear pedido: Database error")
            
            with pytest.raises(Exception, match="Error al crear pedido: Database error"):
                order_repository.create(order)
            
            mock_create.assert_called_once_with(order)
    
    def test_update_database_error(self, order_repository, mock_session):
        """Test: Error de base de datos en update"""
        order = Order(
            id=1,
            order_number="PED-20241201-00001",
            client_id="550e8400-e29b-41d4-a716-446655440000",
            vendor_id="6ba7b810-9dad-11d1-80b4-00c04fd430c8",
            status=OrderStatus.EN_TRANSITO,
            assigned_truck="TRUCK-001",
            scheduled_delivery_date=datetime.utcnow()
        )
        
        # Mock del método update completo
        with patch.object(order_repository, 'update') as mock_update:
            mock_update.side_effect = Exception("Error al actualizar pedido: Database error")
            
            with pytest.raises(Exception, match="Error al actualizar pedido: Database error"):
                order_repository.update(order)
            
            mock_update.assert_called_once_with(order)
    
    def test_delete_database_error(self, order_repository, mock_session):
        """Test: Error de base de datos en delete"""
        # Mock del método delete completo
        with patch.object(order_repository, 'delete') as mock_delete:
            mock_delete.side_effect = Exception("Error al eliminar pedido: Database error")
            
            with pytest.raises(Exception, match="Error al eliminar pedido: Database error"):
                order_repository.delete(1)
            
            mock_delete.assert_called_once_with(1)
    
    def test_get_orders_with_items_by_client_database_error(self, order_repository, mock_session):
        """Test: Error de base de datos en get_orders_with_items_by_client"""
        with patch.object(order_repository, 'get_orders_with_items_by_client') as mock_get_orders:
            mock_get_orders.side_effect = Exception("Error al obtener pedidos del cliente: Database error")
            
            with pytest.raises(Exception, match="Error al obtener pedidos del cliente: Database error"):
                order_repository.get_orders_with_items_by_client(1)
            
            mock_get_orders.assert_called_once_with(1)
    
    def test_get_orders_with_items_by_vendor_database_error(self, order_repository, mock_session):
        """Test: Error de base de datos en get_orders_with_items_by_vendor"""
        with patch.object(order_repository, 'get_orders_with_items_by_vendor') as mock_get_orders:
            mock_get_orders.side_effect = Exception("Error al obtener pedidos del vendedor: Database error")
            
            with pytest.raises(Exception, match="Error al obtener pedidos del vendedor: Database error"):
                order_repository.get_orders_with_items_by_vendor(1)
            
            mock_get_orders.assert_called_once_with(1)
    
    def test_get_orders_by_truck_and_date_success(self, order_repository, mock_session, sample_order_db):
        """Test: Obtener pedidos por camión y fecha exitosamente"""
        from datetime import date
        from app.models.order import Order
        from unittest.mock import Mock as MockObj
        
        sample_order_db.assigned_truck = "CAM-001"
        sample_order_db.scheduled_delivery_date = datetime(2025, 12, 25, 10, 0, 0)
        sample_order_db.items = []
        sample_order_db.id = 1
        sample_order_db.order_number = "PED-001"
        sample_order_db.client_id = "550e8400-e29b-41d4-a716-446655440001"
        sample_order_db.vendor_id = None
        sample_order_db.status = "Recibido"
        sample_order_db.total_amount = 100.0
        sample_order_db.created_at = datetime.now()
        sample_order_db.updated_at = datetime.now()
        
        mock_order_model = Order(
            id=1,
            order_number="PED-001",
            client_id="550e8400-e29b-41d4-a716-446655440001",
            status="Recibido",
            total_amount=100.0,
            scheduled_delivery_date=datetime(2025, 12, 25, 10, 0, 0),
            assigned_truck="CAM-001"
        )
        
        from app.models.db_models import OrderDB
        mock_order_db_class = MockObj(spec=OrderDB)
        mock_order_db_class.assigned_truck = MockObj()
        mock_order_db_class.scheduled_delivery_date = MockObj()
        
        mock_query = MagicMock()
        mock_filter = MagicMock()
        mock_filter.all.return_value = [sample_order_db]
        mock_query.filter.return_value = mock_filter
        mock_session.query.return_value = mock_query
        
        with patch.object(order_repository, '_db_to_model_with_items', return_value=mock_order_model):
            with patch('app.repositories.order_repository.OrderDB', mock_order_db_class):
                result = order_repository.get_orders_by_truck_and_date('CAM-001', date(2025, 12, 25))
                
                assert len(result) == 1
                mock_session.query.assert_called_once()
    
    def test_get_orders_by_truck_and_date_missing_truck(self, order_repository, mock_session):
        """Test: Error cuando falta assigned_truck"""
        with pytest.raises(Exception) as exc_info:
            order_repository.get_orders_by_truck_and_date('', '2025-12-25')
        
        assert "assigned_truck es obligatorio" in str(exc_info.value)
    
    def test_get_orders_by_truck_and_date_missing_date(self, order_repository, mock_session):
        """Test: Error cuando falta scheduled_delivery_date"""
        with pytest.raises(Exception) as exc_info:
            order_repository.get_orders_by_truck_and_date('CAM-001', None)
        
        assert "scheduled_delivery_date es obligatoria" in str(exc_info.value)
    
    def test_get_orders_by_truck_and_date_database_error(self, order_repository, mock_session):
        """Test: Error de base de datos"""
        mock_session.query.side_effect = SQLAlchemyError("Error de BD")
        
        with pytest.raises(Exception) as exc_info:
            order_repository.get_orders_by_truck_and_date('CAM-001', '2025-12-25')
        
        assert "Error al obtener pedidos por camión y fecha" in str(exc_info.value)