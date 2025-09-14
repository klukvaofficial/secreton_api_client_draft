# Secreton API Client

🚀 **Официальная Python библиотека для работы с Secreton API**

Мощный и простой в использовании клиент для обработки аудиофайлов через Secreton API. Поддерживает как синхронные, так и асинхронные операции.

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: Apache 2.0](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

## ⚡ Быстрый старт

`uv remove secreton_api_client`

`uv add "git+https://oauth2:glpat-_TBYYKWRteBtnXM-CG4xA286MQp1Omh4cWozCw.01.121o4a3r0@gitlab.com/saner99/secreton_api_client.git"`

```python
from secreton_api_client import AsyncSecretOnClient

async def main():
    async with AsyncSecretOnClient("https://api.secreton.ru", token="your-token") as client:
        # Создать заказ
        order = await client.orders.create_order(
            order_name="Совещание 100500",
            service_type=1,
            file="audio.ogg",
            auth=client.get_auth()
        )

        # Оплатить и получить результат
        await client.orders.pay_order(order.order_id, client.get_auth())
        print(f"✅ Заказ {order.order_id} создан и оплачен!")
```

## 📦 Установка

### pip

```bash
pip install secreton-api-client
```

### uv

```bash
uv add secreton-api-client
```

### poetry

```bash
poetry add secreton-api-client
```

### pipx (для CLI использования)

```bash
pipx install secreton-api-client
```

## 🔧 Основные возможности

- **🔐 Полная аутентификация** - регистрация, логин, подтверждение по SMS
- **👤 Управление профилем** - просмотр информации, пополнение баланса
- **📄 Работа с заказами** - создание, оплата, мониторинг статуса
- **⚡ Синхронный и асинхронный API** - выбирайте подходящий стиль
- **🛡️ Надёжная обработка ошибок** - детальная информация о проблемах
- **📝 Type hints** - полная поддержка статической типизации

## 📚 Примеры использования

### Регистрация нового пользователя

<details>
<summary><b>Асинхронная версия</b></summary>

```python
from secreton_api_client import AsyncSecretOnClient

async def register_user():
    async with AsyncSecretOnClient("https://api.secreton.ru") as client:
        # Отправляем SMS код
        login_resp = await client.auth.login(79123456789)

        # Подтверждаем телефон
        code = int(input("Введите код из SMS: "))
        await client.auth.phone_confirmation(login_resp.request_id, code)

        # Устанавливаем пароль и получаем токен
        pwd_resp = await client.auth.set_password(login_resp.request_id, "passEwoDrd123")
        return pwd_resp.token
```

</details>

<details>
<summary><b>Синхронная версия</b></summary>

```python
from secreton_api_client import SyncSecretOnClient

def register_user():
    with SyncSecretOnClient("https://api.secreton.ru") as client:
        # Отправляем SMS код
        login_resp = client.auth.login(79123456789)

        # Подтверждаем телефон
        code = int(input("Введите код из SMS: "))
        client.auth.phone_confirmation(login_resp.request_id, code)

        # Устанавливаем пароль и получаем токен
        pwd_resp = client.auth.set_password(login_resp.request_id, "passEwoDrd123")
        return pwd_resp.token
```

</details>

### Создание и мониторинг заказа

```python
from secreton_api_client import AsyncSecretOnClient
import asyncio

async def process_document():
    async with AsyncSecretOnClient("https://api.secreton.ru", token="your-token") as client:
        auth = client.get_auth()

        # Создаём заказ
        order = await client.orders.create_order(
            order_name="Совещание 100500",
            service_type=1,
            file="audio.mp4",
            auth=auth,
            tags=["urgent", "legal"]
        )

        # Оплачиваем
        await client.orders.pay_order(order.order_id, auth)
        print(f"💳 Заказ {order.order_id} оплачен")

        # Мониторим выполнение
        while True:
            status = await client.orders.get_order(order.order_id, auth)
            print(f"📊 Статус: {status.status}")

            if status.status == "completed":
                result = await client.orders.summarize_order(order.order_id, auth)
                print(f"🎉 Результат: {result}")
                break
            elif status.status == "failed":
                print("❌ Обработка не удалась")
                break

            await asyncio.sleep(10)
```

### Управление профилем и балансом

```python
async def manage_profile():
    async with AsyncSecretOnClient("https://api.secreton.ru", token="your-token") as client:
        auth = client.get_auth()

        # Получаем информацию о профиле
        profile = await client.profile.get_profile(auth)
        print(f"👤 Баланс: {profile.balance}₽")

        # Пополняем баланс
        if profile.balance < 100:
            topup = await client.profile.topup_balance(500.0, auth)
            print(f"💰 Ссылка для пополнения: {topup.payment_url}")
```

## 🔍 Обработка ошибок

```python
from secreton_api_client.exceptions import AuthenticationError, ValidationError, FileError

try:
    order = await client.orders.create_order(...)
except AuthenticationError:
    print("🔑 Токен недействителен")
except ValidationError as e:
    print(f"❌ Ошибка валидации: {e.message}")
    for field, error in e.validation_errors.items():
        print(f"  • {field}: {error}")
except FileError as e:
    print(f"📁 Проблема с файлом: {e.file_path}")
```

## 📖 API Reference

### Клиенты

| Класс              | Описание                                               |
| ----------------------- | -------------------------------------------------------------- |
| `AsyncSecretOnClient` | Асинхронный клиент для работы с API |
| `SyncSecretOnClient`  | Синхронный клиент для работы с API   |

### Сервисы

| Сервис | Методы                                                            | Назначение                  |
| ------------ | ----------------------------------------------------------------------- | ------------------------------------- |
| `auth`     | `login()`, `phone_confirmation()`, `set_password()`               | Аутентификация          |
| `profile`  | `get_profile()`, `topup_balance()`                                  | Управление профилем |
| `orders`   | `create_order()`, `get_order()`, `list_orders()`, `pay_order()` | Работа с заказами      |

### Основные модели

```python
from secreton_api_client.models import UserProfile, OrderViewModel, ServiceType

# Профиль пользователя
profile: UserProfile = await client.profile.get_profile(auth)
print(f"ID: {profile.id}, Balance: {profile.balance}")

# Информация о заказе
order: OrderViewModel = await client.orders.get_order(order_id, auth)
print(f"Status: {order.status}, Price: {order.price}")

# Доступные сервисы
services: List[ServiceType] = await client.orders.get_service_types(auth)
for service in services:
    print(f"{service.name}: {service.price}₽")
```

## ⚙️ Конфигурация

### Параметры клиента

```python
client = AsyncSecretOnClient(
    base_url="https://api.secreton.ru",
    token="your-token",           # Опционально
    timeout=30.0,                 # Таймаут запросов
    verify_ssl=True,              # Проверка SSL
    user_agent="MyApp/1.0"        # Пользовательский User-Agent
)
```

### Переменные окружения

```bash
export SECRETON_API_URL="https://api.secreton.ru"
export SECRETON_API_TOKEN="your-token"
export SECRETON_TIMEOUT="30"
```

## 🚨 Типы исключений

| Исключение    | Код HTTP | Описание                              |
| ----------------------- | ----------- | --------------------------------------------- |
| `ValidationError`     | 400, 422    | Ошибки валидации данных  |
| `AuthenticationError` | 401         | Неверная аутентификация |
| `PermissionError`     | 403         | Недостаточно прав             |
| `NotFoundError`       | 404         | Ресурс не найден                |
| `RateLimitError`      | 429         | Превышен лимит запросов  |
| `ServerError`         | 5xx         | Ошибки сервера                   |
| `FileError`           | -           | Проблемы с файлами            |

## 📋 Требования

- **Python 3.8+**
- `httpx` - HTTP клиент
- `pydantic` - валидация данных

## 🔒 Безопасность

- Токены сохраняются с ограниченными правами доступа (`0o600`)
- Поддержка HTTPS и проверки SSL сертификатов
- Автоматическая обработка rate limiting

## 🤝 Вклад в проект

1. Форкните репозиторий
2. Создайте ветку для новой функции (`git checkout -b feature/amazing-feature`)
3. Зафиксируйте изменения (`git commit -m 'Add amazing feature'`)
4. Отправьте в ветку (`git push origin feature/amazing-feature`)
5. Откройте Pull Request

## 📄 Лицензия

Этот проект лицензирован под Apache License 2.0 - см. файл [LICENSE](LICENSE) для деталей.

## 📞 Поддержка

- 📧 **Email**: support@secreton.ru
- 📚 **Документация**: [docs.secreton.ru](https://docs.secreton.ru)
- 🐛 **Баг-репорты**: [GitHub Issues](https://github.com/secreton/python-client/issues)
- 💬 **Telegram**: [@secreton_support](https://t.me/secreton_support)

## 📈 Версии и изменения

Версии библиотеки соответствуют версиям Secreton API. Подробная информация о изменениях доступна в:

- **[CHANGELOG.md](CHANGELOG.md)** - полный список изменений
- **[GitHub Releases](https://github.com/secreton/python-client/releases)** - релизы с описанием

---

<div align="center">

**[🏠 Главная](https://secreton.ru) • [📖 Документация](https://docs.secreton.ru) • [🛠️ API Reference](https://docs.secreton.ru/api) • [💬 Поддержка](https://t.me/secreton_support)**

Сделано с ❤️ командой [Secreton](https://secreton.ru)
