"""Synchronous orders service for Secreton API."""

from pathlib import Path
from typing import BinaryIO, Dict, List, Optional, Union
from uuid import UUID

import httpx

from ..sync_http_client import SyncHTTPClient
from ..models.orders import OrderCreateResponse, OrderViewModel, ServiceType


class SyncOrdersService:
    """Synchronous service for order operations."""

    def __init__(self, http_client: SyncHTTPClient) -> None:
        """Initialize orders service.

        Args:
            http_client: HTTP client instance
        """
        self.http_client = http_client
        self.endpoint_base = "/api/orders"

    def create_order(
        self,
        order_name: str,
        service_type: UUID,
        file: Union[BinaryIO, Path, str],
        auth: httpx.Auth,
        comments: Optional[List[str]] = None,
        tags: Optional[List[str]] = None,
        not_save: bool = False,
    ) -> OrderCreateResponse:
        """Create new order with file upload.

        Args:
            name: Order name
            service_type: Service type ID
            file: File object, Path, or file path string
            auth: Authentication object
            comments: Optional list of comments
            tags: Optional list of tags
            not_save: Don't save file flag

        Returns:
            Order creation response

        Raises:
            FileNotFoundError: If file doesn't exist
            ValidationError: If parameters are invalid
        """
        # Handle different file input types
        if isinstance(file, (str, Path)):
            file_path = Path(file)
            if not file_path.exists():
                raise FileNotFoundError(f"File not found: {file_path}")
            if not file_path.is_file():
                raise ValueError(f"Path is not a file: {file_path}")
            file_obj = file_path.open("rb")
            filename = file_path.name
        else:
            file_obj = file
            filename = getattr(file, "name", "upload")

        try:
            # Prepare multipart form data
            files = {"file": (filename, file_obj, "application/octet-stream")}
            form_data = {
                "name": order_name,
                "service_type": service_type,
                "not_save": not_save,
            }

            if comments:
                form_data["comments"] = comments
            if tags:
                form_data["tags"] = tags

            endpoint = f"{self.endpoint_base}/new"
            response = self.http_client.post(
                endpoint, auth=auth, form_data=form_data, files=files
            )

            return OrderCreateResponse(**response.json())

        finally:
            # Close file if we opened it
            if isinstance(file, (str, Path)):
                file_obj.close()

    def get_order(self, order_id: Union[str, UUID], auth: httpx.Auth) -> OrderViewModel:
        """Get order details by ID.

        Args:
            order_id: Order ID
            auth: Authentication object

        Returns:
            Order details

        Raises:
            NotFoundError: If order doesn't exist
            AuthenticationError: If not authorized
        """
        endpoint = f"{self.endpoint_base}/view"
        params = {"order_id": str(order_id)}

        response = self.http_client.get(endpoint, auth=auth, params=params)
        return OrderViewModel(**response.json())

    def list_orders(
        self,
        auth: httpx.Auth,
        service_type: Optional[str] = None,
        status: Optional[str] = None,
        tags: Optional[List[str]] = None,
        order: Optional[str] = None,
        page: int = 1,
    ) -> List[OrderViewModel]:
        """List orders with optional filters.

        Args:
            auth: Authentication object
            service_type: Filter by service type
            status: Filter by status
            tags: Filter by tags
            order: Sort order
            page: Page number

        Returns:
            List of orders
        """
        endpoint = f"{self.endpoint_base}/"
        params = {"page": page}

        if service_type:
            params["service_type"] = service_type
        if status:
            params["status"] = status
        if tags:
            params["tags"] = tags
        if order:
            params["order"] = order

        response = self.http_client.get(endpoint, auth=auth, params=params)
        return [OrderViewModel(**order) for order in response.json()]

    def pay_order(self, order_id: Union[str, UUID], auth: httpx.Auth) -> Dict:
        """Pay for an order.

        Args:
            order_id: Order ID to pay
            auth: Authentication object

        Returns:
            Payment response
        """
        endpoint = f"{self.endpoint_base}/pay"
        form_data = {"order_id": str(order_id)}

        response = self.http_client.post(
            endpoint,
            auth=auth,
            form_data=form_data,
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )
        return response.json()

    def get_service_types(self, auth: httpx.Auth) -> List[ServiceType]:
        """Get available service types.

        Args:
            auth: Authentication object

        Returns:
            List of service types
        """
        endpoint = f"{self.endpoint_base}/service_types"

        response = self.http_client.get(endpoint, auth=auth)
        return [ServiceType(**st) for st in response.json()]

    def summarize_order(self, order_id: Union[str, UUID], auth: httpx.Auth) -> Dict:
        """Create order summary.

        Args:
            order_id: Order ID to summarize
            auth: Authentication object

        Returns:
            Summary response
        """
        endpoint = f"{self.endpoint_base}/order/{order_id}/summarize"

        response = self.http_client.post(endpoint, auth=auth)
        return response.json()
