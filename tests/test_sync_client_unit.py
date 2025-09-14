"""Unit tests for sync client components."""

import pytest
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path
import tempfile

from secreton_api_client import SyncSecretOnClient
from secreton_api_client.sync_http_client import SyncHTTPClient
from secreton_api_client.sync_services import SyncAuthService, SyncProfileService, SyncOrdersService
from secreton_api_client.exceptions import AuthenticationError, ValidationError


class TestSyncClientUnit:
    """Unit tests for SyncSecretOnClient."""

    def test_client_initialization(self):
        """Test client initialization."""
        client = SyncSecretOnClient("https://api.example.com")
        
        assert client.base_url == "https://api.example.com"
        assert client.token is None
        assert isinstance(client.http_client, SyncHTTPClient)
        assert isinstance(client.auth, SyncAuthService)
        assert not hasattr(client, 'profile')  # Not initialized without token
        assert not hasattr(client, 'orders')   # Not initialized without token

    def test_client_initialization_with_token(self):
        """Test client initialization with token."""
        client = SyncSecretOnClient("https://api.example.com", token="test-token")
        
        assert client.token == "test-token"
        assert isinstance(client.profile, SyncProfileService)
        assert isinstance(client.orders, SyncOrdersService)

    def test_set_token(self):
        """Test setting token after initialization."""
        client = SyncSecretOnClient("https://api.example.com")
        
        client.set_token("new-token")
        
        assert client.token == "new-token"
        assert isinstance(client.profile, SyncProfileService)
        assert isinstance(client.orders, SyncOrdersService)

    def test_context_manager(self):
        """Test context manager functionality."""
        with SyncSecretOnClient("https://api.example.com") as client:
            assert client.base_url == "https://api.example.com"
            # Context manager should work without errors

    def test_get_auth_without_token(self):
        """Test get_auth without token."""
        client = SyncSecretOnClient("https://api.example.com")
        assert client.get_auth() is None

    def test_get_auth_with_token(self):
        """Test get_auth with token."""
        client = SyncSecretOnClient("https://api.example.com", token="test-token")
        auth = client.get_auth()
        assert auth is not None
        assert hasattr(auth, 'token')


class TestSyncAuthService:
    """Unit tests for SyncAuthService."""

    def setup_method(self):
        """Set up test fixtures."""
        self.mock_http_client = Mock(spec=SyncHTTPClient)
        self.auth_service = SyncAuthService(self.mock_http_client)

    def test_login_valid_phone(self):
        """Test login with valid phone number."""
        from uuid import uuid4
        
        # Mock response
        mock_response = Mock()
        request_id = uuid4()
        mock_response.json.return_value = {"request_id": str(request_id)}
        self.mock_http_client.post.return_value = mock_response

        result = self.auth_service.login(79123456789)
        
        assert result.request_id == request_id
        self.mock_http_client.post.assert_called_once()

    def test_login_invalid_phone(self):
        """Test login with invalid phone number."""
        with pytest.raises(ValueError, match="Phone number must be between 79000000000 and 79999999999"):
            self.auth_service.login(123456789)

    def test_password_login_valid(self):
        """Test password login with valid credentials."""
        from uuid import uuid4
        
        mock_response = Mock()
        user_id = uuid4()
        mock_response.json.return_value = {
            "token": "test-token",
            "user_id": str(user_id)
        }
        self.mock_http_client.post.return_value = mock_response

        result = self.auth_service.password_login(79123456789, "password123")
        
        assert result.token == "test-token"
        assert result.user_id == user_id
        self.mock_http_client.post.assert_called_once()

    def test_phone_confirmation_valid(self):
        """Test phone confirmation with valid code."""
        mock_response = Mock()
        mock_response.json.return_value = {
            "success": True,
            "message": "Phone confirmed successfully"
        }
        self.mock_http_client.post.return_value = mock_response

        result = self.auth_service.phone_confirmation("test-request-id", 1234)
        
        assert result.success is True
        assert result.message == "Phone confirmed successfully"
        self.mock_http_client.post.assert_called_once()

    def test_phone_confirmation_invalid_code(self):
        """Test phone confirmation with invalid code."""
        with pytest.raises(ValueError, match="Code must be between 0 and 9999"):
            self.auth_service.phone_confirmation("test-request-id", 12345)

    def test_set_password_valid(self):
        """Test set password with valid password."""
        mock_response = Mock()
        mock_response.json.return_value = {
            "success": True,
            "token": "test-token"
        }
        self.mock_http_client.post.return_value = mock_response

        result = self.auth_service.set_password("test-request-id", "password123")
        
        assert result.success is True
        assert result.token == "test-token"
        self.mock_http_client.post.assert_called_once()

    def test_set_password_invalid(self):
        """Test set password with invalid password."""
        with pytest.raises(ValueError, match="Password must be at least 6 characters long"):
            self.auth_service.set_password("test-request-id", "123")

    def test_send_code(self):
        """Test send code functionality."""
        mock_response = Mock()
        mock_response.json.return_value = {"status": "sent"}
        self.mock_http_client.post.return_value = mock_response

        result = self.auth_service.send_code("test-request-id")
        
        assert result["status"] == "sent"
        self.mock_http_client.post.assert_called_once()

    def test_logout(self):
        """Test logout functionality."""
        mock_auth = Mock()
        mock_response = Mock()
        mock_response.json.return_value = {"status": "logged_out"}
        self.mock_http_client.post.return_value = mock_response

        result = self.auth_service.logout(mock_auth)
        
        assert result["status"] == "logged_out"
        self.mock_http_client.post.assert_called_once()


class TestSyncProfileService:
    """Unit tests for SyncProfileService."""

    def setup_method(self):
        """Set up test fixtures."""
        self.mock_http_client = Mock(spec=SyncHTTPClient)
        self.profile_service = SyncProfileService(self.mock_http_client)

    def test_get_profile_current_user(self):
        """Test get profile for current user."""
        from uuid import uuid4
        
        mock_response = Mock()
        user_id = uuid4()
        mock_response.json.return_value = {
            "id": str(user_id),
            "balance": 100.0,
            "first_name": "Test",
            "last_name": "User"
        }
        self.mock_http_client.get.return_value = mock_response
        mock_auth = Mock()

        result = self.profile_service.get_profile(mock_auth)
        
        assert result.id == user_id
        assert result.balance == 100.0
        assert result.first_name == "Test"
        assert result.last_name == "User"
        self.mock_http_client.get.assert_called_once()

    def test_get_profile_with_user_id(self):
        """Test get profile with specific user ID."""
        from uuid import uuid4
        user_id = uuid4()
        
        mock_response = Mock()
        mock_response.json.return_value = {
            "id": str(user_id),
            "balance": 50.0,
            "first_name": "Test",
            "last_name": "User"
        }
        self.mock_http_client.get.return_value = mock_response
        mock_auth = Mock()

        result = self.profile_service.get_profile(mock_auth, user_id)
        
        assert result.id == user_id
        assert result.balance == 50.0
        self.mock_http_client.get.assert_called_once()

    def test_topup_balance_valid_amount(self):
        """Test topup balance with valid amount."""
        from uuid import uuid4
        
        mock_response = Mock()
        payment_id = uuid4()
        mock_response.json.return_value = {
            "id": str(payment_id),
            "amount": 100.0,
            "status": "pending",
            "payment_url": "https://payment.example.com"
        }
        self.mock_http_client.get.return_value = mock_response
        mock_auth = Mock()

        result = self.profile_service.topup_balance(100.0, mock_auth)
        
        assert result.id == payment_id
        assert result.amount == 100.0
        assert result.status == "pending"
        assert result.payment_url == "https://payment.example.com"
        self.mock_http_client.get.assert_called_once()

    def test_topup_balance_invalid_amount(self):
        """Test topup balance with invalid amount."""
        mock_auth = Mock()
        
        with pytest.raises(ValueError, match="Amount must be at least 10"):
            self.profile_service.topup_balance(5.0, mock_auth)


class TestSyncOrdersService:
    """Unit tests for SyncOrdersService."""

    def setup_method(self):
        """Set up test fixtures."""
        self.mock_http_client = Mock(spec=SyncHTTPClient)
        self.orders_service = SyncOrdersService(self.mock_http_client)

    def test_create_order_with_file_path(self):
        """Test create order with file path."""
        # Create temporary file
        with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as f:
            f.write(b"test audio content")
            temp_file_path = f.name

        try:
            from uuid import uuid4
            
            mock_response = Mock()
            order_id = uuid4()
            mock_response.json.return_value = {
                "order_id": str(order_id),
                "message": "Order created successfully"
            }
            self.mock_http_client.post.return_value = mock_response
            mock_auth = Mock()

            result = self.orders_service.create_order(
                "Test Order",
                1,
                temp_file_path,
                mock_auth,
                tags=["test"],
                comments=["Test comment"]
            )
            
            assert result.order_id == order_id
            assert result.message == "Order created successfully"
            self.mock_http_client.post.assert_called_once()

        finally:
            # Cleanup
            Path(temp_file_path).unlink(missing_ok=True)

    def test_create_order_with_nonexistent_file(self):
        """Test create order with non-existent file."""
        mock_auth = Mock()
        
        with pytest.raises(FileNotFoundError):
            self.orders_service.create_order(
                "Test Order",
                1,
                "nonexistent_file.mp3",
                mock_auth
            )

    def test_get_order(self):
        """Test get order by ID."""
        from uuid import uuid4
        from datetime import datetime
        
        mock_response = Mock()
        order_id = uuid4()
        service_type_id = uuid4()
        created_at = datetime.now()
        
        mock_response.json.return_value = {
            "order_id": str(order_id),
            "service_type": str(service_type_id),
            "status": "processing",
            "price": 50.0,
            "created_at": created_at.isoformat(),
            "tags": [],
            "comments": []
        }
        self.mock_http_client.get.return_value = mock_response
        mock_auth = Mock()

        result = self.orders_service.get_order("test-order-id", mock_auth)
        
        assert result.order_id == order_id
        assert result.service_type == service_type_id
        assert result.status == "processing"
        assert result.price == 50.0
        self.mock_http_client.get.assert_called_once()

    def test_list_orders(self):
        """Test list orders."""
        from uuid import uuid4
        from datetime import datetime
        
        mock_response = Mock()
        order1_id = uuid4()
        order2_id = uuid4()
        service_type_id = uuid4()
        created_at = datetime.now()
        
        mock_response.json.return_value = [
            {
                "order_id": str(order1_id),
                "service_type": str(service_type_id),
                "status": "completed",
                "price": 100.0,
                "created_at": created_at.isoformat(),
                "tags": [],
                "comments": []
            },
            {
                "order_id": str(order2_id),
                "service_type": str(service_type_id),
                "status": "processing",
                "price": 75.0,
                "created_at": created_at.isoformat(),
                "tags": [],
                "comments": []
            }
        ]
        self.mock_http_client.get.return_value = mock_response
        mock_auth = Mock()

        result = self.orders_service.list_orders(mock_auth, page=1)
        
        assert len(result) == 2
        assert result[0].order_id == order1_id
        assert result[0].status == "completed"
        assert result[1].order_id == order2_id
        assert result[1].status == "processing"
        self.mock_http_client.get.assert_called_once()

    def test_list_orders_with_filters(self):
        """Test list orders with filters."""
        mock_response = Mock()
        mock_response.json.return_value = []
        self.mock_http_client.get.return_value = mock_response
        mock_auth = Mock()

        result = self.orders_service.list_orders(
            mock_auth,
            service_type="transcription",
            status="completed",
            tags=["test"],
            page=1
        )
        
        assert result == []
        self.mock_http_client.get.assert_called_once()

    def test_pay_order(self):
        """Test pay order."""
        mock_response = Mock()
        mock_response.json.return_value = {"payment_url": "https://payment.example.com"}
        self.mock_http_client.post.return_value = mock_response
        mock_auth = Mock()

        result = self.orders_service.pay_order("test-order-id", mock_auth)
        
        assert result["payment_url"] == "https://payment.example.com"
        self.mock_http_client.post.assert_called_once()

    def test_get_service_types(self):
        """Test get service types."""
        mock_response = Mock()
        mock_response.json.return_value = [
            {"id": 1, "name": "Transcription"},
            {"id": 2, "name": "Translation"}
        ]
        self.mock_http_client.get.return_value = mock_response
        mock_auth = Mock()

        result = self.orders_service.get_service_types(mock_auth)
        
        assert len(result) == 2
        assert result[0].id == 1
        assert result[0].name == "Transcription"
        self.mock_http_client.get.assert_called_once()

    def test_summarize_order(self):
        """Test summarize order."""
        mock_response = Mock()
        mock_response.json.return_value = {"summary": "Order summary text"}
        self.mock_http_client.post.return_value = mock_response
        mock_auth = Mock()

        result = self.orders_service.summarize_order("test-order-id", mock_auth)
        
        assert result["summary"] == "Order summary text"
        self.mock_http_client.post.assert_called_once()


class TestSyncClientIntegration:
    """Integration tests for sync client."""

    @patch('secreton_api_client.client.SyncHTTPClient')
    def test_full_workflow(self, mock_http_client_class):
        """Test full workflow with mocked HTTP client."""
        # Setup mock
        mock_http_client = Mock()
        mock_http_client_class.return_value = mock_http_client
        
        # Mock responses
        from uuid import uuid4
        
        request_id = uuid4()
        user_id = uuid4()
        
        login_response = Mock()
        login_response.json.return_value = {"request_id": str(request_id)}
        
        profile_response = Mock()
        profile_response.json.return_value = {
            "id": str(user_id),
            "balance": 100.0,
            "first_name": "Test",
            "last_name": "User"
        }
        
        orders_response = Mock()
        orders_response.json.return_value = []
        
        # Configure mock to return different responses for different calls
        def mock_get(*args, **kwargs):
            if 'profile' in str(args[0]):
                return profile_response
            else:
                return orders_response
        
        mock_http_client.post.return_value = login_response
        mock_http_client.get.side_effect = mock_get

        # Test workflow
        with SyncSecretOnClient("https://api.example.com") as client:
            # Login
            login_result = client.auth.login(79123456789)
            assert login_result.request_id == request_id
            
            # Set token
            client.set_token("test-token")
            
            # Get profile
            profile = client.profile.get_profile(auth=client.get_auth())
            assert profile.id == user_id
            assert profile.balance == 100.0
            
            # List orders
            orders = client.orders.list_orders(auth=client.get_auth())
            assert orders == []
