"""Synchronous services for Secreton API."""

from .auth import SyncAuthService
from .orders import SyncOrdersService
from .profile import SyncProfileService

__all__ = ["SyncAuthService", "SyncOrdersService", "SyncProfileService"]
