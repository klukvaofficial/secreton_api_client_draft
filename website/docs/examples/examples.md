# Полный workflow с заказами

:::tip Готовый пример
Этот пример показывает полный цикл работы с API
:::

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

<Tabs>
<TabItem value="sync" label="Синхронный вариант">

Полные примеры доступны в репозитории:
- `examples/sync_quick_start.py` - полный синхронный workflow
- `examples/sync_auth.py` - синхронная аутентификация

</TabItem>
<TabItem value="async" label="Асинхронный вариант">

Полные примеры доступны в репозитории:
- `examples/async_quick_start.py` - полный асинхронный workflow
- `examples/async_auth.py` - асинхронная аутентификация

</TabItem>
</Tabs>

## Простая работа с профилем

<Tabs>
<TabItem value="sync-profile" label="Синхронный вариант">

```python
from secreton_api_client import SyncSecretOnClient

with SyncSecretOnClient(token="your-token") as client:
    auth = client.get_auth()
    profile = client.profile.get_profile(auth)

    print(f"Баланс: {profile.balance}₽")
    print(f"ID пользователя: {profile.user_id}")
```

</TabItem>
<TabItem value="async-profile" label="Асинхронный вариант">

```python
import asyncio
from secreton_api_client import AsyncSecretOnClient

async def main():
    async with AsyncSecretOnClient(token="your-token") as client:
        auth = client.get_auth()
        profile = await client.profile.get_profile(auth)

        print(f"Баланс: {profile.balance}₽")
        print(f"ID пользователя: {profile.user_id}")

asyncio.run(main())
```

</TabItem>
</Tabs>

## Создание и мониторинг заказа

<Tabs>
<TabItem value="sync-order" label="Синхронный вариант">

```python
from secreton_api_client import SyncSecretOnClient
import time

with SyncSecretOnClient(token="your-token") as client:
    auth = client.get_auth()

    # Создаем заказ
    order = client.orders.create_order(
        order_name="Тестовый заказ",
        service_type=1,
        file="audio.wav",
        auth=auth
    )

    # Оплачиваем
    client.orders.pay_order(order.order_id, auth)

    # Ждем завершения
    while True:
        status = client.orders.get_order(order.order_id, auth)
        print(f"Статус: {status.status}")

        if status.status == "completed":
            result = client.orders.summarize_order(order.order_id, auth)
            print(f"Результат: {result}")
            break

        time.sleep(10)
```

</TabItem>
<TabItem value="async-order" label="Асинхронный вариант">

```python
import asyncio
from secreton_api_client import AsyncSecretOnClient

async def main():
    async with AsyncSecretOnClient(token="your-token") as client:
        auth = client.get_auth()

        # Создаем заказ
        order = await client.orders.create_order(
            order_name="Тестовый заказ",
            service_type=1,
            file="audio.wav",
            auth=auth
        )

        # Оплачиваем
        await client.orders.pay_order(order.order_id, auth)

        # Ждем завершения
        while True:
            status = await client.orders.get_order(order.order_id, auth)
            print(f"Статус: {status.status}")

            if status.status == "completed":
                result = await client.orders.summarize_order(order.order_id, auth)
                print(f"Результат: {result}")
                break

            await asyncio.sleep(10)

asyncio.run(main())
```

</TabItem>
</Tabs>

## Параллельная обработка нескольких заказов

<Tabs>
<TabItem value="sync-parallel" label="Синхронный вариант">

```python
from secreton_api_client import SyncSecretOnClient
import time

def process_multiple_files():
    files = ["audio1.wav", "audio2.wav", "audio3.wav"]

    with SyncSecretOnClient(token="your-token") as client:
        auth = client.get_auth()

        orders = []

        # Создаем все заказы
        for file_path in files:
            order = client.orders.create_order(
                order_name=f"Заказ для {file_path}",
                service_type=1,
                file=file_path,
                auth=auth
            )
            client.orders.pay_order(order.order_id, auth)
            orders.append(order.order_id)
            print(f"✅ Создан заказ: {order.order_id}")

        # Мониторим все заказы
        completed = []
        while len(completed) < len(orders):
            for order_id in orders:
                if order_id not in completed:
                    status = client.orders.get_order(order_id, auth)

                    if status.status == "completed":
                        result = client.orders.summarize_order(order_id, auth)
                        print(f"🎉 Готов {order_id}: {result}")
                        completed.append(order_id)
                    elif status.status in ["failed", "cancelled"]:
                        print(f"❌ Ошибка {order_id}: {status.status}")
                        completed.append(order_id)

            if len(completed) < len(orders):
                time.sleep(15)

process_multiple_files()
```

</TabItem>
<TabItem value="async-parallel" label="Асинхронный вариант">

```python
import asyncio
from secreton_api_client import AsyncSecretOnClient

async def process_multiple_files():
    files = ["audio1.wav", "audio2.wav", "audio3.wav"]

    async with AsyncSecretOnClient(token="your-token") as client:
        auth = client.get_auth()

        # Создаем все заказы параллельно
        create_tasks = []
        for file_path in files:
            task = create_single_order(client, auth, file_path)
            create_tasks.append(task)

        orders = await asyncio.gather(*create_tasks)
        print(f"✅ Создано {len(orders)} заказов")

        # Мониторим все заказы параллельно
        monitor_tasks = []
        for order_id in orders:
            task = monitor_single_order(client, auth, order_id)
            monitor_tasks.append(task)

        results = await asyncio.gather(*monitor_tasks)
        print(f"🎉 Завершено {len(results)} заказов")

async def create_single_order(client, auth, file_path):
    """Создание и оплата одного заказа."""
    order = await client.orders.create_order(
        order_name=f"Заказ для {file_path}",
        service_type=1,
        file=file_path,
        auth=auth
    )
    await client.orders.pay_order(order.order_id, auth)
    print(f"✅ Создан заказ: {order.order_id}")
    return order.order_id

async def monitor_single_order(client, auth, order_id):
    """Мониторинг одного заказа до завершения."""
    while True:
        status = await client.orders.get_order(order_id, auth)

        if status.status == "completed":
            result = await client.orders.summarize_order(order_id, auth)
            print(f"🎉 Готов {order_id}: {result}")
            return result
        elif status.status in ["failed", "cancelled"]:
            print(f"❌ Ошибка {order_id}: {status.status}")
            return None

        await asyncio.sleep(15)

asyncio.run(process_multiple_files())
```

</TabItem>
</Tabs>

## Обработка ошибок

<Tabs>
<TabItem value="sync-errors" label="Синхронный вариант">

```python
from secreton_api_client import SyncSecretOnClient
from secreton_api_client.exceptions import (
    AuthenticationError,
    ValidationError,
    FileError,
    APIClientError
)

try:
    with SyncSecretOnClient(token="your-token") as client:
        auth = client.get_auth()

        order = client.orders.create_order(
            order_name="Тестовый заказ",
            service_type=1,
            file="audio.wav",
            auth=auth
        )

        client.orders.pay_order(order.order_id, auth)
        print(f"✅ Заказ создан и оплачен: {order.order_id}")

except AuthenticationError:
    print("❌ Проблема с токеном аутентификации")

except FileError as e:
    print(f"❌ Проблема с файлом: {e.message}")
    if e.file_path:
        print(f"   Файл: {e.file_path}")

except ValidationError as e:
    print(f"❌ Ошибка валидации: {e.message}")
    if e.validation_errors:
        for field, error in e.validation_errors.items():
            print(f"   {field}: {error}")

except APIClientError as e:
    print(f"❌ Общая ошибка API: {e.message}")
```

</TabItem>
<TabItem value="async-errors" label="Асинхронный вариант">

```python
import asyncio
from secreton_api_client import AsyncSecretOnClient
from secreton_api_client.exceptions import (
    AuthenticationError,
    ValidationError,
    FileError,
    APIClientError
)

async def main():
    try:
        async with AsyncSecretOnClient(token="your-token") as client:
            auth = client.get_auth()

            order = await client.orders.create_order(
                order_name="Тестовый заказ",
                service_type=1,
                file="audio.wav",
                auth=auth
            )

            await client.orders.pay_order(order.order_id, auth)
            print(f"✅ Заказ создан и оплачен: {order.order_id}")

    except AuthenticationError:
        print("❌ Проблема с токеном аутентификации")

    except FileError as e:
        print(f"❌ Проблема с файлом: {e.message}")
        if e.file_path:
            print(f"   Файл: {e.file_path}")

    except ValidationError as e:
        print(f"❌ Ошибка валидации: {e.message}")
        if e.validation_errors:
            for field, error in e.validation_errors.items():
                print(f"   {field}: {error}")

    except APIClientError as e:
        print(f"❌ Общая ошибка API: {e.message}")

asyncio.run(main())
```

</TabItem>
</Tabs>

Эти примеры показывают:

1. **Полный workflow** - подтягивается из файлов примеров
2. **Простую работу с профилем** - базовые операции в обеих версиях
3. **Создание и мониторинг заказа** - пошаговый процесс
4. **Параллельную обработку** - демонстрирует преимущества async подхода
5. **Обработку ошибок** - одинаковые исключения в обеих версиях

Асинхронные версии показывают:
- Использование `async/await`
- Неблокирующие операции (`asyncio.sleep` вместо `time.sleep`)
- Параллельное выполнение с `asyncio.gather`
- Правильное использование `async with`

