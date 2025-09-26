# Аутентификация

SecretOn API Client поддерживает два способа аутентификации:

1. **Прямое использование токена** - если у вас уже есть действующий токен
2. **Получение токена через логин/пароль** - для получения нового токена

## Использование существующего токена

Если у вас уже есть токен, просто передайте его при создании клиента:

=== "Синхронный"

    ```python
    from secreton_api_client import SyncSecretOnClient

    # Создание клиента с токеном
    with SyncSecretOnClient(
        base_url="https://api.secreton.ru",
        token="your-existing-token-here"
    ) as client:
        auth = client.get_auth()

        # Теперь можно делать авторизованные запросы
        profile = client.profile.get_profile(auth)
        print(f"Баланс: {profile.balance}₽")
    ```

=== "Асинхронный"

    ```python
    import asyncio
    from secreton_api_client import AsyncSecretOnClient

    async def main():
        async with AsyncSecretOnClient(
            base_url="https://api.secreton.ru",
            token="your-existing-token-here"
        ) as client:
            auth = client.get_auth()

            # Авторизованные запросы
            profile = await client.profile.get_profile(auth)
            print(f"Баланс: {profile.balance}₽")

    asyncio.run(main())
    ```

## Получение токена через логин/пароль

### Синхронный пример

```python title="Полный пример синхронной аутентификации"
--8<-- "examples/sync_auth.py"
```

### Асинхронный пример

```python title="Полный пример асинхронной аутентификации"
--8<-- "examples/async_auth.py"
```

## Основные принципы

### 1. Создание объекта аутентификации

```python
# После создания клиента с токеном
auth = client.get_auth()  # Возвращает объект Authentication

# Этот объект нужно передавать во все API методы
profile = await client.profile.get_profile(auth)
orders = await client.orders.get_service_types(auth)
```

### 2. Обработка ошибок аутентификации

```python
from secreton_api_client.exceptions import AuthenticationError

try:
    # Попытка аутентификации
    token = await client.authenticate("username", "password")
except AuthenticationError as e:
    print(f"Ошибка аутентификации: {e.message}")
    # Обработка ошибки (неверный логин/пароль, заблокированный аккаунт и т.д.)
```

### 3. Проверка валидности токена

```python
try:
    auth = client.get_auth()
    profile = await client.profile.get_profile(auth)
    print("Токен валиден")
except AuthenticationError:
    print("Токен недействителен или истёк")
    # Необходимо получить новый токен
```

## Безопасность

!!! warning "Безопасность токенов" - Никогда не храните токены в открытом виде в коде - Используйте переменные окружения или конфиги - Регулярно обновляйте токены - Не передавайте токены через небезопасные каналы

### Использование переменных окружения

```python
import os
from secreton_api_client import SyncSecretOnClient

# Получаем токен из переменной окружения
token = os.getenv("SECRETON_API_TOKEN")
if not token:
    raise ValueError("Токен не найден в переменных окружения")

with SyncSecretOnClient(token=token) as client:
    # Работа с API
    pass
```

### Сохранение токена после получения

```python
import json
from pathlib import Path

def save_token(token: str, filename: str = "token.json"):
    """Сохранение токена в файл."""
    token_data = {"token": token}
    Path(filename).write_text(json.dumps(token_data))

def load_token(filename: str = "token.json") -> str:
    """Загрузка токена из файла."""
    try:
        token_data = json.loads(Path(filename).read_text())
        return token_data["token"]
    except FileNotFoundError:
        return None

# Использование
token = load_token()
if not token:
    # Получаем новый токен
    with SyncSecretOnClient() as client:
        token = client.authenticate("username", "password")
        save_token(token)

# Используем токен
with SyncSecretOnClient(token=token) as client:
    # Работа с API
    pass
```

## Типичные ошибки

### 1. Неверный формат токена

```python
# ❌ Неправильно
token = "Bearer your-token"  # Не нужно добавлять "Bearer"

# ✅ Правильно
token = "your-token"
```

### 2. Забыли создать объект auth

```python
# ❌ Неправильно
profile = client.profile.get_profile()  # Отсутствует auth

# ✅ Правильно
auth = client.get_auth()
profile = client.profile.get_profile(auth)
```

### 3. Неправильный URL базового сервиса

```python
# ❌ Неправильно
client = SyncSecretOnClient(base_url="https://secreton.ru")  # Не API URL

# ✅ Правильно
client = SyncSecretOnClient(base_url="https://api.secreton.ru")
```

## Следующие шаги

После успешной аутентификации переходите к:

- [Быстрый старт](quick-start.md) - первые шаги с API
- [Работа с заказами](../user-guide/orders.md) - создание и управление заказами
- [Примеры кода](../examples/) - готовые решения
