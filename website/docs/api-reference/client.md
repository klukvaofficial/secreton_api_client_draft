# Client Classes

## SyncSecretOnClient

### SyncSecretOnClient

Synchronous client for Secreton API.

This is the primary interface for interacting with the Secreton API synchronously.
It provides access to all service endpoints through a unified interface.

Example:
    with SyncSecretOnClient("https://api.secreton.ru") as client:
        # Login
        login_resp = client.auth.login(phone=79123456789)

        # Set token after authentication
        client.set_token("your-auth-token")

        # Use authenticated services
        profile = client.profile.get_profile(auth=client.get_auth())

**Parameters:**

- `base_url` (`<class 'str'>`): 
- `token` (`typing.Optional[str]`) (default: `None`): 
- `timeout` (`<class 'float'>`) (default: `30.0`): 
- `verify_ssl` (`<class 'bool'>`) (default: `True`): 
- `user_agent` (`typing.Optional[str]`) (default: `None`): 

**Methods:**

- `__enter__(self)`: Context manager entry.
- `__exit__(self, exc_type, exc_val, exc_tb)`: Context manager exit.
- `__init__(self, base_url: str, token: Optional[str] = None, timeout: float = 30.0, verify_ssl: bool = True, user_agent: Optional[str] = None) -> None`: Initialize Secreton API client.
- `close(self) -> None`: Close HTTP client connection.
- `get_auth(self) -> Optional[secreton_api_client.auth.SecretOnAuth]`: Get current authentication object.
- `set_token(self, token: str) -> None`: Set or update authentication token.



## AsyncSecretOnClient

### AsyncSecretOnClient

Asynchronous client for Secreton API.

This is the primary interface for interacting with the Secreton API asynchronously.
It provides access to all service endpoints through a unified interface.

Example:
    async with AsyncSecretOnClient("https://api.secreton.ru") as client:
        # Login
        login_resp = await client.auth.login(phone=79123456789)

        # Set token after authentication
        client.set_token("your-auth-token")

        # Use authenticated services
        profile = await client.profile.get_profile(auth=client.get_auth())

**Parameters:**

- `base_url` (`<class 'str'>`): 
- `token` (`typing.Optional[str]`) (default: `None`): 
- `timeout` (`<class 'float'>`) (default: `30.0`): 
- `verify_ssl` (`<class 'bool'>`) (default: `True`): 
- `user_agent` (`typing.Optional[str]`) (default: `None`): 

**Methods:**

- `__init__(self, base_url: str, token: Optional[str] = None, timeout: float = 30.0, verify_ssl: bool = True, user_agent: Optional[str] = None) -> None`: Initialize Secreton API client.
- `close(self) -> None`: Close HTTP client connection.
- `get_auth(self) -> Optional[secreton_api_client.auth.SecretOnAuth]`: Get current authentication object.
- `set_token(self, token: str) -> None`: Set or update authentication token.

