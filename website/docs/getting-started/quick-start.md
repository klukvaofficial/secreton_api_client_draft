# Быстрый старт

Это руководство поможет вам быстро начать работу с SecretOn API Client. За 5 минут вы научитесь создавать заказы, оплачивать их и получать результаты.

## Предварительные требования

1. Установленный пакет: `pip install secreton-api-client`
2. Действующий токен аутентификации ([как получить](authentication.md))
3. Аудиофайл для обработки (например, `audio.mp3`)

## Выберите ваш стиль

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

<Tabs>
<TabItem value="sync" label="Синхронный (проще)">

Подходит для простых скриптов и обучения:

```python
from secreton_api_client import SyncSecretOnClient

with SyncSecretOnClient(token="your-token") as client:
    auth = client.get_auth()
    profile = client.profile.get_profile(auth)
    print(f"Баланс: {profile.balance}₽")
```

</TabItem>
<TabItem value="async" label="Асинхронный (производительнее)">

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

</TabItem>
</Tabs>

## Полные примеры workflow

<Tabs>
<TabItem value="sync-full" label="Синхронный полный цикл">

Этот пример показывает полный процесс: от проверки баланса до получения результата.

```python title="Синхронный workflow с обработкой ошибок"
"""(Синхронный вариант) Работа с заказами при наличии токена с базовой обработкой ошибок"""

from secreton_api_client import SyncSecretOnClient
from secreton_api_client.exceptions import (
    AuthenticationError,
    ValidationError,
    NotFoundError,
    FileError,
    ServerError,
    APIClientError,
)
import time


def sync_quick_start():
    """Быстрый workflow для пользователя с готовым токеном."""

    # Создаём клиента с готовым токеном
    token = "your-existing-auth-token-here"

    try:
        with SyncSecretOnClient(
            base_url="https://api.secreton.ru", token=token
        ) as client:
            auth = client.get_auth()

            # Проверяем профиль
            print("👤 Проверяем профиль...")
            try:
                profile = client.profile.get_profile(auth)
                print(f"Баланс: {profile.balance}₽")

                # Проверяем достаточность баланса
                if profile.balance < 100:
                    print("⚠️ Низкий баланс. Рекомендуется пополнение.")

            except AuthenticationError:
                print(
                    "❌ Токен недействителен или истёк. Необходима повторная авторизация."
                )
                return False

            # Создаём и оплачиваем заказ
            print("📦 Создаём заказ...")

            try:
                # Получаем доступные сервисы
                service_types = client.orders.get_service_types(auth)
                if not service_types:
                    print("❌ Нет доступных сервисов")
                    return False

                selected_service = service_types[0]  # Выбираем первый доступный
                print(f"📋 Выбран сервис: {selected_service.name}")

            except APIClientError as e:
                print(f"❌ Ошибка получения сервисов: {e.message}")
                return False

            try:
                # Создаём заказ
                order = client.orders.create_order(
                    order_name="Новый заказ",
                    service_type=selected_service.id,
                    file="audio.mp3",
                    auth=auth,
                    tags=["express", "priority"],
                )

                print(f"✅ Заказ создан: {order.order_id}")

            except FileError as e:
                print(f"❌ Ошибка с файлом: {e.message}")
                if e.file_path:
                    print(f"   Проблемный файл: {e.file_path}")
                return False

            except ValidationError as e:
                print(f"❌ Ошибка валидации заказа: {e.message}")
                if e.validation_errors:
                    for field, error in e.validation_errors.items():
                        print(f"   • {field}: {error}")
                return False

            except APIClientError as e:
                print(f"❌ Ошибка создания заказа: {e.message}")
                return False

            try:
                # Сразу оплачиваем
                client.orders.pay_order(order.order_id, auth)
                print("💳 Заказ оплачен!")

            except ValidationError as e:
                if "insufficient balance" in e.message.lower():
                    print("❌ Недостаточно средств для оплаты")
                else:
                    print(f"❌ Ошибка оплаты: {e.message}")
                return False

            except APIClientError as e:
                print(f"❌ Ошибка оплаты: {e.message}")
                return False

            # Мониторим выполнение
            print("⏳ Ожидаем результат...")
            max_attempts = 40  # Максимум 10 минут ожидания
            attempt = 0

            while attempt < max_attempts:
                try:
                    time.sleep(15)  # Проверяем каждые 15 секунд
                    attempt += 1

                    order_status = client.orders.get_order(order.order_id, auth)
                    print(f"📊 Статус: {order_status.status} (попытка {attempt})")

                    if order_status.status == "completed":
                        try:
                            # Получаем результат
                            result = client.orders.summarize_order(order.order_id, auth)
                            print("🎉 Заказ готов!")
                            print("📄 Результат:", result)
                            return True

                        except APIClientError as e:
                            print(
                                f"⚠️ Заказ выполнен, но не удалось получить результат: {e.message}"
                            )
                            return True  # Заказ всё равно выполнен

                    elif order_status.status == "failed":
                        print("❌ Заказ не выполнен")
                        return False

                    elif order_status.status in ["cancelled", "expired"]:
                        print(f"❌ Заказ {order_status.status}")
                        return False

                except NotFoundError:
                    print("❌ Заказ не найден")
                    return False

                except APIClientError as e:
                    print(f"⚠️ Ошибка проверки статуса: {e.message}")
                    # Продолжаем попытки при временных ошибках
                    continue

            print("⏰ Превышено время ожидания. Заказ может быть ещё в обработке.")
            return False

    except AuthenticationError as e:
        print(f"❌ Ошибка аутентификации: {e.message}")
        print("🔑 Проверьте корректность токена")
        return False

    except ServerError as e:
        print(f"❌ Ошибка сервера: {e.message}")
        print("⏳ Попробуйте позже")
        return False

    except APIClientError as e:
        print(f"❌ Общая ошибка API: {e.message}")
        return False

    except Exception as e:
        print(f"❌ Неожиданная ошибка: {str(e)}")
        return False


def main():
    """Главная функция с дополнительной обработкой."""
    print("🚀 Запуск быстрого workflow с заказами")

    success = sync_quick_start()

    if success:
        print("\n✅ Workflow выполнен успешно!")
    else:
        print("\n❌ Workflow завершился с ошибками")
        print("💡 Проверьте:")
        print("   • Корректность токена")
        print("   • Наличие файла 'audio.mp3'")
        print("   • Баланс на счету")
        print("   • Подключение к интернету")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n👋 Процесс прерван пользователем")
    except Exception as e:
        print(f"\n💥 Критическая ошибка: {e}")
```

**Что делает этот пример:**

1. 🔐 Создаёт клиента с токеном
2. 👤 Проверяет профиль и баланс
3. 📋 Получает доступные сервисы
4. 📦 Создаёт заказ на обработку файла
5. 💳 Оплачивает заказ
6. ⏳ Мониторит выполнение каждые 15 секунд
7. 🎉 Получает результат при завершении

</TabItem>
<TabItem value="async-full" label="Асинхронный полный цикл">

Асинхронная версия того же workflow с неблокирующими операциями.

```python title="Асинхронный workflow с обработкой ошибок"
"""(Асинхронный вариант) Работа с заказами при наличии токена с базовой обработкой ошибок"""

import asyncio
from secreton_api_client import AsyncSecretOnClient
from secreton_api_client.exceptions import (
    AuthenticationError,
    ValidationError,
    NotFoundError,
    FileError,
    ServerError,
    APIClientError,
)


async def async_quick_start():
    """Быстрый workflow для пользователя с готовым токеном."""

    # Создаём клиента с готовым токеном
    token = "your-existing-auth-token-here"

    try:
        async with AsyncSecretOnClient(
            base_url="https://api.secreton.ru", token=token
        ) as client:
            auth = client.get_auth()

            # Проверяем профиль
            print("👤 Проверяем профиль...")
            try:
                profile = await client.profile.get_profile(auth)
                print(f"Баланс: {profile.balance}₽")

                # Проверяем достаточность баланса
                if profile.balance < 100:
                    print("⚠️ Низкий баланс. Рекомендуется пополнение.")

            except AuthenticationError:
                print(
                    "❌ Токен недействителен или истёк. Необходима повторная авторизация."
                )
                return False

            # Создаём и оплачиваем заказ
            print("📦 Создаём заказ...")

            try:
                # Получаем доступные сервисы
                service_types = await client.orders.get_service_types(auth)
                if not service_types:
                    print("❌ Нет доступных сервисов")
                    return False

                selected_service = service_types[0]  # Выбираем первый доступный
                print(f"📋 Выбран сервис: {selected_service.name}")

            except APIClientError as e:
                print(f"❌ Ошибка получения сервисов: {e.message}")
                return False

            try:
                # Создаём заказ
                order = await client.orders.create_order(
                    order_name="Новый заказ",
                    service_type=selected_service.id,
                    file="audio.mp3",
                    auth=auth,
                    tags=["express", "priority"],
                )

                print(f"✅ Заказ создан: {order.order_id}")

            except FileError as e:
                print(f"❌ Ошибка с файлом: {e.message}")
                if e.file_path:
                    print(f"   Проблемный файл: {e.file_path}")
                return False

            except ValidationError as e:
                print(f"❌ Ошибка валидации заказа: {e.message}")
                if e.validation_errors:
                    for field, error in e.validation_errors.items():
                        print(f"   • {field}: {error}")
                return False

            except APIClientError as e:
                print(f"❌ Ошибка создания заказа: {e.message}")
                return False

            try:
                # Сразу оплачиваем
                await client.orders.pay_order(order.order_id, auth)
                print("💳 Заказ оплачен!")

            except ValidationError as e:
                if "insufficient balance" in e.message.lower():
                    print("❌ Недостаточно средств для оплаты")
                else:
                    print(f"❌ Ошибка оплаты: {e.message}")
                return False

            except APIClientError as e:
                print(f"❌ Ошибка оплаты: {e.message}")
                return False

            # Мониторим выполнение
            print("⏳ Ожидаем результат...")
            max_attempts = 40  # Максимум 10 минут ожидания
            attempt = 0

            while attempt < max_attempts:
                try:
                    await asyncio.sleep(15)  # Проверяем каждые 15 секунд
                    attempt += 1

                    order_status = await client.orders.get_order(order.order_id, auth)
                    print(f"📊 Статус: {order_status.status} (попытка {attempt})")

                    if order_status.status == "completed":
                        try:
                            # Получаем результат
                            result = await client.orders.summarize_order(
                                order.order_id, auth
                            )
                            print("🎉 Заказ готов!")
                            print("📄 Результат:", result)
                            return True

                        except APIClientError as e:
                            print(
                                f"⚠️ Заказ выполнен, но не удалось получить результат: {e.message}"
                            )
                            return True  # Заказ всё равно выполнен

                    elif order_status.status == "failed":
                        print("❌ Заказ не выполнен")
                        return False

                    elif order_status.status in ["cancelled", "expired"]:
                        print(f"❌ Заказ {order_status.status}")
                        return False

                except NotFoundError:
                    print("❌ Заказ не найден")
                    return False

                except APIClientError as e:
                    print(f"⚠️ Ошибка проверки статуса: {e.message}")
                    # Продолжаем попытки при временных ошибках
                    continue

            print("⏰ Превышено время ожидания. Заказ может быть ещё в обработке.")
            return False

    except AuthenticationError as e:
        print(f"❌ Ошибка аутентификации: {e.message}")
        print("🔑 Проверьте корректность токена")
        return False

    except ServerError as e:
        print(f"❌ Ошибка сервера: {e.message}")
        print("⏳ Попробуйте позже")
        return False

    except APIClientError as e:
        print(f"❌ Общая ошибка API: {e.message}")
        return False

    except Exception as e:
        print(f"❌ Неожиданная ошибка: {str(e)}")
        return False


async def main():
    """Главная функция с дополнительной обработкой."""
    print("🚀 Запуск быстрого workflow с заказами")

    success = await async_quick_start()

    if success:
        print("\n✅ Workflow выполнен успешно!")
    else:
        print("\n❌ Workflow завершился с ошибками")
        print("💡 Проверьте:")
        print("   • Корректность токена")
        print("   • Наличие файла 'audio.mp3'")
        print("   • Баланс на счету")
        print("   • Подключение к интернету")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 Процесс прерван пользователем")
    except Exception as e:
        print(f"\n💥 Критическая ошибка: {e}")
```

**Преимущества асинхронной версии:**

- ⚡ Неблокирующее ожидание результатов
- 🔄 Возможность обрабатывать несколько заказов параллельно
- 🌐 Идеально для веб-приложений (FastAPI, aiohttp)
- 📈 Лучшая производительность при множественных запросах

</TabItem>
</Tabs>

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

:::tip Context Manager
Всегда используйте `with` / `async with` - это обеспечивает правильное закрытие соединений
:::

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

