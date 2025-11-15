# API Reference

Полная документация API для SecretOn API Client библиотеки. Все классы, методы и модели автоматически генерируются из исходного кода Python.

## Клиенты

Основные классы для работы с API:

- **[Client Classes](client.md)** - `SyncSecretOnClient` и `AsyncSecretOnClient`
  - Синхронный и асинхронный интерфейсы
  - Управление аутентификацией
  - Настройка HTTP клиента

## Сервисы

Сервисы предоставляют доступ к различным эндпоинтам API:

- **[Services](services.md)** - `AuthService`, `OrdersService`, `ProfileService`
  - Аутентификация и регистрация
  - Управление заказами
  - Работа с профилем пользователя

## Модели данных

Модели данных для запросов и ответов API:

- **[Data Models](models.md)** - Pydantic модели
  - Модели аутентификации (`LoginResponse`, `RegisterResponse`)
  - Модели заказов (`OrderViewModel`, `OrderCommentModel`, `OrderTagModel`)
  - Модели профиля (`UserProfile`)

## Исключения

Иерархия исключений для обработки ошибок:

- **[Exceptions](exceptions.md)** - Классы исключений
  - `APIClientError` - базовый класс
  - `AuthenticationError` - ошибки аутентификации
  - `ValidationError` - ошибки валидации
  - `FileError` - ошибки работы с файлами
  - `NotFoundError` - ресурс не найден
  - `ServerError` - ошибки сервера
  - `RateLimitError` - превышен лимит запросов

## Быстрый поиск

### По функциональности

- **Аутентификация**: [AuthService](services.md#authentication-service) | [Authentication Models](models.md#authentication-models) | [AuthenticationError](exceptions.md#authenticationerror)
- **Заказы**: [OrdersService](services.md#orders-service) | [Order Models](models.md#order-models)
- **Профиль**: [ProfileService](services.md#profile-service) | [Profile Models](models.md#profile-models)

### По типу

- **Классы клиентов**: [SyncSecretOnClient](client.md#synsecretonclient) | [AsyncSecretOnClient](client.md#asyncsecretonclient)
- **Сервисы**: [Services](services.md)
- **Модели**: [Models](models.md)
- **Ошибки**: [Exceptions](exceptions.md)

## Примечания

- Вся документация автоматически генерируется из Python docstrings
- При изменении исходного кода документация обновляется автоматически
- Для получения актуальной документации запустите `python scripts/generate_api_docs.py`

