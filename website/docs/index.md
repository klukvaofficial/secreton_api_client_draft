# SecretOn API Client

Современный Python клиент для работы с SecretOn API.

[![PyPI version](https://badge.fury.io/py/secreton-api-client.svg)](https://badge.fury.io/py/secreton-api-client)
[![Python Support](https://img.shields.io/pypi/pyversions/secreton-api-client.svg)](https://pypi.org/project/secreton-api-client/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## Особенности

- 🚀 **Синхронный и асинхронный API** - выбирайте подходящий стиль
- 🔒 **Безопасность** - встроенная аутентификация и обработка токенов
- 📦 **Управление заказами** - создание, оплата, мониторинг
- 👤 **Профиль пользователя** - получение информации о балансе
- ⚡ **Type hints** - полная поддержка типизации
- 🛡️ **Обработка ошибок** - детальные исключения для каждого случая

## Быстрый старт

### Установка

```bash
pip install secreton-api-client
```

### Синхронное использование

```python
from secreton_api_client import SyncSecretOnClient

with SyncSecretOnClient(token="your-token") as client:
    auth = client.get_auth()

    # Получаем профиль
    profile = client.profile.get_profile(auth)
    print(f"Баланс: {profile.balance}₽")

    # Создаем заказ
    order = client.orders.create_order(
        order_name="Новый заказ",
        service_type=1,
        file="audio.mp3",
        auth=auth
    )
    print(f"Заказ создан: {order.order_id}")
```

### Асинхронное использование

```python
import asyncio
from secreton_api_client import AsyncSecretOnClient

async def main():
    async with AsyncSecretOnClient(token="your-token") as client:
        auth = client.get_auth()

        # Получаем профиль
        profile = await client.profile.get_profile(auth)
        print(f"Баланс: {profile.balance}₽")

asyncio.run(main())
```

## Навигация

- [📖 Getting Started](getting-started/installation.md) - начните здесь
- [💻 Examples](examples/examples.md) - примеры кода
- [📚 API Reference](api-reference/client.md) - полная документация API

