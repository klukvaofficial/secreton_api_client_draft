"""Tests for sync and async clients."""

import pytest
from unittest.mock import Mock, patch

from secreton_api_client import SyncSecretOnClient, AsyncSecretOnClient


class TestSyncClient:
    """Test synchronous client."""
    
    def test_sync_client_initialization(self):
        """Test sync client initialization."""
        client = SyncSecretOnClient("https://api.example.com")
        
        assert client.base_url == "https://api.example.com"
        assert client.token is None
        assert hasattr(client, 'auth')
        assert hasattr(client, 'http_client')
        
    def test_sync_client_with_token(self):
        """Test sync client with token."""
        client = SyncSecretOnClient("https://api.example.com", token="test-token")
        
        assert client.token == "test-token"
        assert hasattr(client, 'profile')
        assert hasattr(client, 'orders')
        
    def test_sync_client_set_token(self):
        """Test setting token on sync client."""
        client = SyncSecretOnClient("https://api.example.com")
        
        client.set_token("new-token")
        
        assert client.token == "new-token"
        assert hasattr(client, 'profile')
        assert hasattr(client, 'orders')
        
    def test_sync_client_context_manager(self):
        """Test sync client context manager."""
        with SyncSecretOnClient("https://api.example.com") as client:
            assert client.base_url == "https://api.example.com"


class TestAsyncClient:
    """Test asynchronous client."""
    
    def test_async_client_initialization(self):
        """Test async client initialization."""
        client = AsyncSecretOnClient("https://api.example.com")
        
        assert client.base_url == "https://api.example.com"
        assert client.token is None
        assert hasattr(client, 'auth')
        assert hasattr(client, 'http_client')
        
    def test_async_client_with_token(self):
        """Test async client with token."""
        client = AsyncSecretOnClient("https://api.example.com", token="test-token")
        
        assert client.token == "test-token"
        assert hasattr(client, 'profile')
        assert hasattr(client, 'orders')
        
    def test_async_client_set_token(self):
        """Test setting token on async client."""
        client = AsyncSecretOnClient("https://api.example.com")
        
        client.set_token("new-token")
        
        assert client.token == "new-token"
        assert hasattr(client, 'profile')
        assert hasattr(client, 'orders')
        
    @pytest.mark.asyncio
    async def test_async_client_context_manager(self):
        """Test async client context manager."""
        async with AsyncSecretOnClient("https://api.example.com") as client:
            assert client.base_url == "https://api.example.com"


class TestClientDifferences:
    """Test differences between sync and async clients."""
    
    def test_client_types_are_different(self):
        """Test that sync and async clients are different classes."""
        sync_client = SyncSecretOnClient("https://api.example.com")
        async_client = AsyncSecretOnClient("https://api.example.com")
        
        assert type(sync_client) != type(async_client)
        assert isinstance(sync_client, SyncSecretOnClient)
        assert isinstance(async_client, AsyncSecretOnClient)
        
    def test_sync_client_uses_sync_services(self):
        """Test that sync client uses sync services."""
        client = SyncSecretOnClient("https://api.example.com", token="test-token")
        
        # Check that services are sync versions
        from secreton_api_client.sync_services import SyncAuthService, SyncProfileService, SyncOrdersService
        
        assert isinstance(client.auth, SyncAuthService)
        assert isinstance(client.profile, SyncProfileService)
        assert isinstance(client.orders, SyncOrdersService)
        
    def test_async_client_uses_async_services(self):
        """Test that async client uses async services."""
        client = AsyncSecretOnClient("https://api.example.com", token="test-token")
        
        # Check that services are async versions
        from secreton_api_client.services import AuthService, ProfileService, OrdersService
        
        assert isinstance(client.auth, AuthService)
        assert isinstance(client.profile, ProfileService)
        assert isinstance(client.orders, OrdersService)
