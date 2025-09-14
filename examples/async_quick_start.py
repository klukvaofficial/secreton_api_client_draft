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
