"""
Tests para los nuevos métodos del OrderRepository
"""
import pytest
from unittest.mock import MagicMock, Mock, patch
from datetime import datetime, date
from app.repositories.order_repository import OrderRepository
from app.models.order import Order, OrderStatus
from app.models.order_item import OrderItem
from sqlalchemy.exc import SQLAlchemyError


class TestOrderRepositoryNewMethods:
    """Tests para los nuevos métodos del OrderRepository"""
    
    @pytest.fixture
    def mock_session(self):
        return MagicMock()
    
    @pytest.fixture
    def order_repository(self, mock_session):
        return OrderRepository(mock_session)
    
    def test_create_with_items(self, order_repository, mock_session):
        from app.models.db_models import OrderDB, OrderItemDB
        
        order = Order(
            order_number="PED-001",
            client_id="client-1",
            vendor_id="vendor-1",
            status=OrderStatus.RECIBIDO,
            total_amount=200.0,
            scheduled_delivery_date=date(2024, 12, 25),
            assigned_truck="TRUCK-001"
        )
        order.items = [
            OrderItem(product_id="prod-1", quantity=2),
            OrderItem(product_id="prod-2", quantity=3)
        ]
        
        mock_db_order = MagicMock()
        mock_db_order.id = 1
        mock_db_order.order_number = "PED-001"
        mock_db_order.client_id = "client-1"
        mock_db_order.vendor_id = "vendor-1"
        mock_db_order.status = OrderStatus.RECIBIDO
        mock_db_order.total_amount = 200.0
        mock_db_order.scheduled_delivery_date = date(2024, 12, 25)
        mock_db_order.assigned_truck = "TRUCK-001"
        mock_db_order.created_at = datetime(2024, 12, 25)
        mock_db_order.updated_at = datetime(2024, 12, 25)
        mock_db_order.items = []
        
        mock_session.add = MagicMock()
        mock_session.flush = MagicMock()
        mock_session.commit = MagicMock()
        mock_session.refresh = MagicMock()
        
        with patch('app.repositories.order_repository.OrderDB', return_value=mock_db_order):
            with patch('app.repositories.order_repository.OrderItemDB') as mock_item_db:
                with patch.object(order_repository, '_db_to_model_with_items') as mock_convert:
                    mock_convert.return_value = order
                    
                    result = order_repository.create(order)
                    
                    assert result == order
                    assert mock_session.add.call_count == 3
                    mock_session.flush.assert_called_once()
                    mock_session.commit.assert_called_once()
    
    @patch('app.repositories.order_repository.OrderDB')
    def test_get_orders_status_summary_by_client_ids_success(self, mock_order_db, order_repository, mock_session):
        client_ids = ['client-1', 'client-2']
        
        mock_result1 = Mock()
        mock_result1.status = OrderStatus.RECIBIDO
        mock_result1.count = 5
        mock_result1.total_amount = 1000.0
        
        mock_result2 = Mock()
        mock_result2.status = OrderStatus.ENTREGADO
        mock_result2.count = 3
        mock_result2.total_amount = 500.0
        
        mock_query = MagicMock()
        mock_query.filter.return_value = mock_query
        mock_query.group_by.return_value = mock_query
        mock_query.all.return_value = [mock_result1, mock_result2]
        
        mock_session.query.return_value = mock_query
        
        result = order_repository.get_orders_status_summary_by_client_ids(client_ids)
        
        assert len(result) == 2
        assert result[0]['status'] == OrderStatus.RECIBIDO
        assert result[0]['count'] == 5
        assert result[0]['total_amount'] == 1000.0
    
    def test_get_orders_status_summary_by_client_ids_empty_list(self, order_repository, mock_session):
        result = order_repository.get_orders_status_summary_by_client_ids([])
        
        assert result == []
        mock_session.query.assert_not_called()
    
    @patch('app.repositories.order_repository.OrderDB')
    def test_get_orders_status_summary_by_client_ids_with_none_values(self, mock_order_db, order_repository, mock_session):
        client_ids = ['client-1']
        
        mock_result = Mock()
        mock_result.status = OrderStatus.RECIBIDO
        mock_result.count = None
        mock_result.total_amount = None
        
        mock_query = MagicMock()
        mock_query.filter.return_value = mock_query
        mock_query.group_by.return_value = mock_query
        mock_query.all.return_value = [mock_result]
        
        mock_session.query.return_value = mock_query
        
        result = order_repository.get_orders_status_summary_by_client_ids(client_ids)
        
        assert result[0]['count'] == 0
        assert result[0]['total_amount'] == 0.0
    
    def test_get_orders_status_summary_by_client_ids_sqlalchemy_error(self, order_repository, mock_session):
        mock_session.query.side_effect = SQLAlchemyError("Database error")
        
        with pytest.raises(Exception, match="Error al obtener resumen por estado"):
            order_repository.get_orders_status_summary_by_client_ids(['client-1'])
    
    def test_get_orders_monthly_summary_by_client_ids_empty_list(self, order_repository, mock_session):
        result = order_repository.get_orders_monthly_summary_by_client_ids([], datetime(2024, 1, 1), datetime(2024, 12, 31))
        
        assert result == []
        mock_session.query.assert_not_called()
    
    def test_get_orders_monthly_summary_by_client_ids_sqlalchemy_error(self, order_repository, mock_session):
        mock_session.query.side_effect = SQLAlchemyError("Database error")
        
        with pytest.raises(Exception, match="Error al obtener resumen mensual"):
            order_repository.get_orders_monthly_summary_by_client_ids(['client-1'], datetime(2024, 1, 1), datetime(2024, 12, 31))
    
    @patch('app.repositories.order_repository.OrderDB')
    def test_get_clients_summary_by_client_ids_success(self, mock_order_db, order_repository, mock_session):
        client_ids = ['client-1', 'client-2']
        
        mock_total_result = Mock()
        mock_total_result.scalar.return_value = 2
        
        mock_total_query = MagicMock()
        mock_total_query.scalar.return_value = 2
        
        mock_result1 = Mock()
        mock_result1.client_id = 'client-1'
        mock_result1.orders_count = 5
        mock_result1.total_amount = 1000.0
        mock_result1.average_order_amount = 200.0
        
        mock_result2 = Mock()
        mock_result2.client_id = 'client-2'
        mock_result2.orders_count = 3
        mock_result2.total_amount = 500.0
        mock_result2.average_order_amount = 166.67
        
        mock_query = MagicMock()
        mock_query.filter.return_value = mock_query
        mock_query.group_by.return_value = mock_query
        mock_query.order_by.return_value = mock_query
        mock_query.offset.return_value = mock_query
        mock_query.limit.return_value = mock_query
        mock_query.all.return_value = [mock_result1, mock_result2]
        
        mock_session.query.return_value = mock_query
        mock_query.scalar.return_value = 2
        
        result, total = order_repository.get_clients_summary_by_client_ids(client_ids, 10, 0)
        
        assert total == 2
        assert len(result) == 2
        assert result[0]['client_id'] == 'client-1'
        assert result[0]['orders_count'] == 5
        assert result[0]['total_amount'] == 1000.0
    
    def test_get_clients_summary_by_client_ids_empty_list(self, order_repository, mock_session):
        result, total = order_repository.get_clients_summary_by_client_ids([], 10, 0)
        
        assert result == []
        assert total == 0
        mock_session.query.assert_not_called()
    
    @patch('app.repositories.order_repository.OrderDB')
    def test_get_clients_summary_by_client_ids_with_none_values(self, mock_order_db, order_repository, mock_session):
        client_ids = ['client-1']
        
        mock_total_query = MagicMock()
        mock_total_query.scalar.return_value = 1
        
        mock_result = Mock()
        mock_result.client_id = 'client-1'
        mock_result.orders_count = None
        mock_result.total_amount = None
        mock_result.average_order_amount = None
        
        mock_query = MagicMock()
        mock_query.filter.return_value = mock_query
        mock_query.group_by.return_value = mock_query
        mock_query.order_by.return_value = mock_query
        mock_query.offset.return_value = mock_query
        mock_query.limit.return_value = mock_query
        mock_query.all.return_value = [mock_result]
        
        mock_session.query.return_value = mock_query
        mock_query.scalar.return_value = 1
        
        result, total = order_repository.get_clients_summary_by_client_ids(client_ids, 10, 0)
        
        assert result[0]['orders_count'] == 0
        assert result[0]['total_amount'] == 0.0
        assert result[0]['average_order_amount'] == 0.0
    
    def test_get_clients_summary_by_client_ids_sqlalchemy_error(self, order_repository, mock_session):
        mock_session.query.side_effect = SQLAlchemyError("Database error")
        
        with pytest.raises(Exception, match="Error al obtener resumen por clientes"):
            order_repository.get_clients_summary_by_client_ids(['client-1'], 10, 0)

