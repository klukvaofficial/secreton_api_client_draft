# Exceptions

### APIClientError

Base exception for all API client errors.

**Parameters:**

- `message` (`<class 'str'>`): 
- `status_code` (`typing.Optional[int]`) (default: `None`): 

**Methods:**

- `__init__(self, message: str, status_code: Optional[int] = None) -> None`: Initialize API client error.

**Attributes:**

- `args`: getset_descriptor



### AuthenticationError

Authentication failed (401, 403).

**Parameters:**

- `message` (`<class 'str'>`): 
- `status_code` (`typing.Optional[int]`) (default: `None`): 

**Methods:**

- `__init__(self, message: str, status_code: Optional[int] = None) -> None`: Initialize authentication error.

**Attributes:**

- `args`: getset_descriptor



### ValidationError

Request validation failed (422).

**Parameters:**

- `message` (`<class 'str'>`): 
- `status_code` (`typing.Optional[int]`) (default: `None`): 
- `validation_errors` (`typing.Optional[typing.Dict[str, typing.Any]]`) (default: `None`): 

**Methods:**

- `__init__(self, message: str, status_code: Optional[int] = None, validation_errors: Optional[Dict[str, Any]] = None) -> None`: Initialize validation error.

**Attributes:**

- `args`: getset_descriptor



### FileError

File operation error.

**Parameters:**

- `message` (`<class 'str'>`): 
- `file_path` (`typing.Optional[str]`) (default: `None`): 

**Methods:**

- `__init__(self, message: str, file_path: Optional[str] = None) -> None`: Initialize file error.

**Attributes:**

- `args`: getset_descriptor



### NotFoundError

Resource not found (404).

**Parameters:**

- `message` (`<class 'str'>`): 
- `status_code` (`typing.Optional[int]`) (default: `None`): 

**Methods:**

- `__init__(self, message: str, status_code: Optional[int] = None) -> None`: Initialize not found error.

**Attributes:**

- `args`: getset_descriptor



### ServerError

Server error (5xx).

**Parameters:**

- `message` (`<class 'str'>`): 
- `status_code` (`typing.Optional[int]`) (default: `None`): 

**Methods:**

- `__init__(self, message: str, status_code: Optional[int] = None) -> None`: Initialize server error.

**Attributes:**

- `args`: getset_descriptor



### HTTPError

Generic HTTP error for non-specific status codes.

**Parameters:**

- `message` (`<class 'str'>`): 
- `status_code` (`typing.Optional[int]`) (default: `None`): 

**Methods:**

- `__init__(self, message: str, status_code: Optional[int] = None) -> None`: Initialize HTTP error.

**Attributes:**

- `args`: getset_descriptor



### RateLimitError

Rate limit exceeded (429).

**Parameters:**

- `message` (`<class 'str'>`): 
- `status_code` (`typing.Optional[int]`) (default: `None`): 
- `retry_after` (`typing.Optional[int]`) (default: `None`): 

**Methods:**

- `__init__(self, message: str, status_code: Optional[int] = None, retry_after: Optional[int] = None) -> None`: Initialize rate limit error.

**Attributes:**

- `args`: getset_descriptor



