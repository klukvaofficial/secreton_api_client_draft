# Быстрый старт

Это руководство поможет вам быстро начать работу с SecretOn API Client. За 5 минут вы научитесь создавать заказы, оплачивать их и получать результаты.

## Предварительные требования

1. Установленный пакет: `pip install secreton-api-client`
2. Действующий токен аутентификации ([как получить](authentication.md))
3. Аудиофайл для обработки (например, `audio.mp3`)

## Выберите ваш стиль

=== "Синхронный (проще)"

    Подходит для простых скриптов и обучения:

    ```python
    from secreton_api_client import SyncSecretOnClient

    with SyncSecretOnClient(token="your-token") as client:
        auth = client.get_auth()
        profile = client.profile.get_profile(auth)
        print(f"Баланс: {profile.balance}₽")
    ```

=== "Асинхронный (производительнее)"

    Подходит для веб-приложений и высокой производительности:

    ```python
    import asyncio
    from secreton_api_client import AsyncSecretOnClient

    async def main():
        async with AsyncSecretOnClient(token="your-token") as client:
            auth = client.get_auth()
            profile = await client.profile.get_profile(auth)
            print(f"Баланс: {profile.balance}₽")

    asyncio.run(main())
    ```

## Полные примеры workflow

=== "Синхронный полный цикл"

    Этот пример показывает полный процесс: от проверки баланса до получения результата.

    ```python title="Синхронный workflow с обработкой ошибок"
    --8<-- "examples/sync_quick_start.py"
    ```

    **Что делает этот пример:**

    1. 🔐 Создаёт клиента с токеном
    2. 👤 Проверяет профиль и баланс
    3. 📋 Получает доступные сервисы
    4. 📦 Создаёт заказ на обработку файла
    5. 💳 Оплачивает заказ
    6. ⏳ Мониторит выполнение каждые 15 секунд
    7. 🎉 Получает результат при завершении

=== "Асинхронный полный цикл"

    Асинхронная версия того же workflow с неблокирующими операциями.

    ```python title="Асинхронный workflow с обработкой ошибок"
    --8<-- "examples/async_quick_start.py"
    ```

    **Преимущества асинхронной версии:**

    - ⚡ Неблокирующее ожидание результатов
    - 🔄 Возможность обрабатывать несколько заказов параллельно
    - 🌐 Идеально для веб-приложений (FastAPI, aiohttp)
    - 📈 Лучшая производительность при множественных запросах

## Пошаговый разбор

### 1. Создание клиента

```python
# Синхронный
with SyncSecretOnClient(
    base_url="https://api.secreton.ru",  # Обычно можно не указывать
    token="your-token-here"
) as client:
    # Работа с API

# Асинхронный
async with AsyncSecretOnClient(token="your-token") as client:
    # Работа с API
```

!!! tip "Context Manager"
Всегда используйте `with` / `async with` - это обеспечивает правильное закрытие соединений

### 2. Проверка профиля

```python
# Получаем объект аутентификации
auth = client.get_auth()

# Проверяем профиль (синхронно/асинхронно)
profile = await client.profile.get_profile(auth)  # async версия
profile = client.profile.get_profile(auth)        # sync версия

print(f"Баланс: {profile.balance}₽")
```

### 3. Создание заказа

```python
# Получаем доступные сервисы
service_types = await client.orders.get_service_types(auth)
selected_service = service_types[0]  # Выбираем первый доступный

# Создаём заказ
order = await client.orders.create_order(
    order_name="Мой первый заказ",
    service_type=selected_service.id,
    file="path/to/audio.mp3",  # Путь к вашему файлу
    auth=auth,
    tags=["test", "quickstart"]  # Опционально
)

print(f"Заказ создан: {order.order_id}")
```

### 4. Оплата заказа

```python
# Оплачиваем заказ
await client.orders.pay_order(order.order_id, auth)
print("💳 Заказ оплачен!")
```

### 5. Мониторинг выполнения

```python
import time  # для sync
import asyncio  # для async

while True:
    # Проверяем статус
    order_status = await client.orders.get_order(order.order_id, auth)
    print(f"Статус: {order_status.status}")

    if order_status.status == "completed":
        # Получаем результат
        result = await client.orders.summarize_order(order.order_id, auth)
        print(f"🎉 Результат: {result}")
        break
    elif order_status.status in ["failed", "cancelled"]:
        print("❌ Заказ завершился с ошибкой")
        break

    await asyncio.sleep(15)  # async версия
    time.sleep(15)           # sync версия
```

## Запуск примеров

1. **Скопируйте** один из примеров выше
2. **Замените** `"your-existing-auth-token-here"` на ваш реальный токен
3. **Убедитесь**, что файл `audio.mp3` существует в папке со скриптом
4. **Запустите**:

```bash
# Синхронный пример
python sync_quick_start.py

# Асинхронный пример
python async_quick_start.py
```

## Что дальше?

После успешного запуска примера изучите:

- 🛡️ [Обработка ошибок](../user-guide/error-handling.md)
- 💻 [Пример Telegram бота](../examples/telegram-bot.md) - веб-интеграции, боты
- 📖 [API Reference](../api-reference/client.md) - полная документация

## Получение помощи

Если что-то не работает:

1. ✅ **Проверьте токен** - он должен быть действующим
2. ✅ **Проверьте файл** - убедитесь что `audio.mp3` существует
3. ✅ **Проверьте баланс** - на счету должно быть достаточно средств
4. ✅ **Проверьте интернет** - соединение с API должно работать

Частые проблемы и решения в разделе [Error Handling](../user-guide/error-handling.md).
