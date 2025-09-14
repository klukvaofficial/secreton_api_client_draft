"""(Асинхронный вариант) Регистрация с базовой обработкой ошибок"""

import asyncio
from secreton_api_client import AsyncSecretOnClient
from secreton_api_client.exceptions import (
    ValidationError,
    AuthenticationError,
    APIClientError,
)


async def compact_async_registration():
    try:
        async with AsyncSecretOnClient("https://api.secreton.ru") as client:
            # Логин и SMS
            phone = int(input("Телефон (79xxxxxxxxx): "))
            login_resp = await client.auth.login(phone)
            print(f"SMS отправлен (ID: {login_resp.request_id})")

            # Код
            code = int(input("Код из SMS: "))
            if not (
                await client.auth.phone_confirmation(login_resp.request_id, code)
            ).success:
                return print("❌ Неверный код")

            # Пароль
            password = input("Пароль (мин. 6 символов): ")
            pwd_resp = await client.auth.set_password(login_resp.request_id, password)

            if pwd_resp.success and pwd_resp.token:
                print(f"✅ Готово! Токен: {pwd_resp.token[:20]}...")
                return pwd_resp.token
            print("❌ Ошибка установки пароля")

    except ValidationError as e:
        print(f"❌ Ошибка валидации: {e.message}")
    except AuthenticationError as e:
        print(f"❌ Ошибка аутентификации: {e.message}")
    except APIClientError as e:
        print(f"❌ Ошибка API: {e.message}")
    except ValueError:
        print("❌ Неверный формат номера телефона или кода")


# Использование
asyncio.run(compact_async_registration())
