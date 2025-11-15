# Services

## Authentication Service

### AuthService

Service for authentication operations.

**Parameters:**

- `http_client` (`<class 'secreton_api_client.http_client.HTTPClient'>`): 

**Methods:**

- `__init__(self, http_client: secreton_api_client.http_client.HTTPClient) -> None`: Initialize authentication service.
- `login(self, phone: int) -> secreton_api_client.models.auth.RegisterResponse`: Initiate login process with phone number.
- `logout(self, auth: httpx.Auth) -> Dict`: Logout current user.
- `password_login(self, phone: int, password: str) -> secreton_api_client.models.auth.LoginResponse`: Login with phone and password.
- `phone_confirmation(self, request_id: Union[str, uuid.UUID], code: int) -> secreton_api_client.models.auth.PhoneConfirmationResponse`: Confirm phone number with SMS code.
- `send_code(self, request_id: Union[str, uuid.UUID]) -> Dict`: Resend SMS confirmation code.
- `set_password(self, request_id: Union[str, uuid.UUID], password: str) -> secreton_api_client.models.auth.PasswordSetResponse`: Set password after phone confirmation.



## Orders Service

### OrdersService

Service for order operations.

**Parameters:**

- `http_client` (`<class 'secreton_api_client.http_client.HTTPClient'>`): 

**Methods:**

- `__init__(self, http_client: secreton_api_client.http_client.HTTPClient) -> None`: Initialize orders service.
- `create_order(self, order_name: str, service_type: uuid.UUID, file: Union[BinaryIO, pathlib._local.Path, str], auth: httpx.Auth, comments: Optional[List[str]] = None, tags: Optional[List[str]] = None, not_save: bool = False) -> secreton_api_client.models.orders.OrderCreateResponse`: Create new order with file upload.
- `get_order(self, order_id: Union[str, uuid.UUID], auth: httpx.Auth) -> secreton_api_client.models.orders.OrderViewModel`: Get order details by ID.
- `get_service_types(self, auth: httpx.Auth) -> List[secreton_api_client.models.orders.ServiceType]`: Get available service types.
- `list_orders(self, auth: httpx.Auth, service_type: Optional[uuid.UUID] = None, status: Optional[str] = None, tags: Optional[List[str]] = None, order: Optional[str] = None, page: int = 1) -> List[secreton_api_client.models.orders.OrderViewModel]`: List orders with optional filters.
- `pay_order(self, order_id: Union[str, uuid.UUID], auth: httpx.Auth) -> Dict`: Pay for an order.
- `summarize_order(self, order_id: Union[str, uuid.UUID], auth: httpx.Auth) -> Dict`: Create order summary.



## Profile Service

### ProfileService

Service for profile operations.

**Parameters:**

- `http_client` (`<class 'secreton_api_client.http_client.HTTPClient'>`): 

**Methods:**

- `__init__(self, http_client: secreton_api_client.http_client.HTTPClient) -> None`: Initialize profile service.
- `get_profile(self, auth: httpx.Auth, user_id: Optional[uuid.UUID] = None) -> secreton_api_client.models.profile.UserProfile`: Get user profile information.
- `topup_balance(self, amount: float, auth: httpx.Auth, user_id: Optional[uuid.UUID] = None) -> secreton_api_client.models.profile.BalanceTopupResponse`: Top up user balance.

