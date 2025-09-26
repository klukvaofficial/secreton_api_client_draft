# Обработка ошибок

Библиотека предоставляет детализированные исключения для различных ситуаций.

## Иерархия исключений

::: secreton_api_client.exceptions.APIClientError
    options:
      heading_level: 3

::: secreton_api_client.exceptions.AuthenticationError
    options:
      heading_level: 3

::: secreton_api_client.exceptions.ValidationError
    options:
      heading_level: 3

## Примеры обработки

```python
from secreton_api_client import SyncSecretOnClient
from secreton_api_client.exceptions import (
    AuthenticationError,
    ValidationError,
    FileError
)

try:
    with SyncSecretOnClient(token="bad-token") as client:
        auth = client.get_auth()
        profile = client.profile.get_profile(auth)

except AuthenticationError as e:
    print(f"Ошибка аутентификации: {e.message}")

except ValidationError as e:
    print(f"Ошибка валидации: {e.message}")
    if e.validation_errors:
        for field, error in e.validation_errors.items():
            print(f"  {field}: {error}")

except FileError as e:
    print(f"Ошибка с файлом: {e.message}")
    if e.file_path:
        print(f"  Файл: {e.file_path}")
```