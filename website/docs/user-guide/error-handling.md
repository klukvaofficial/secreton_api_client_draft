# Обработка ошибок

Библиотека предоставляет детализированные исключения для различных ситуаций.

## Иерархия исключений

API документация для исключений будет сгенерирована автоматически. Основные классы исключений:

- `APIClientError` - базовый класс для всех ошибок API
- `AuthenticationError` - ошибки аутентификации
- `ValidationError` - ошибки валидации данных
- `FileError` - ошибки работы с файлами
- `NotFoundError` - ресурс не найден
- `ServerError` - ошибки сервера

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

Полная документация по исключениям доступна в разделе [API Reference - Exceptions](../api-reference/exceptions.md).

