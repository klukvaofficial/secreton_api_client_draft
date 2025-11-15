# Многопользовательский Telegram-bot

:::tip Готовый пример
Это пример бота для Telegram на **secreton_api_client** и **python-telegram-bot** / **Aiogram**
:::

## Реализация:

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

<Tabs>
<TabItem value="sync" label="Синхронный (python-telegram-bot)">

Полный пример доступен в репозитории: `examples/sync_telegram_bot.py`

</TabItem>
<TabItem value="async" label="Асинхронный (Aiogram)">

Полный пример доступен в репозитории: `examples/async_telegram_bot.py`

</TabItem>
</Tabs>

## Основные отличия и возможности:

### 🔧 **Архитектурные особенности:**

**Асинхронная версия:**

- ✅ работает на **aiogram**
- ✅ Полностью неблокирующая обработка
- ✅ `aiosqlite` для асинхронной работы с БД
- ✅ Нативная интеграция с `AsyncSecretOnClient`
- ✅ Возможность параллельной обработки файлов от разных пользователей

**Синхронная версия:**

- ✅ работает на **python-telegram-bot**
- ✅ Нативная интеграция с `SyncSecretOnClient`
- ❌ **Блокирующие операции** - одни пользователь за раз
- ❌ **Нет параллелизма** - последовательная обработка
- ✅ **Меньше сложности** в коде

### 👥 **Система пользователей:**

- Персональная регистрация с токенами SecretOn API
- Безопасное хранение токенов в SQLite базе
- Проверка валидности токенов при регистрации
- Индивидуальные балансы и история активности
- Команды управления аккаунтом (/logout, /profile)

### 🗃️ **База данных:**

```sql
CREATE TABLE users (
    user_id INTEGER PRIMARY KEY,        -- Telegram ID
    username TEXT,                      -- @username
    full_name TEXT,                     -- Полное имя
    secreton_token TEXT NOT NULL,       -- Персональный токен SecretOn
    registered_at TIMESTAMP,            -- Дата регистрации
    last_activity TIMESTAMP,            -- Последняя активность
    is_active BOOLEAN DEFAULT 1         -- Статус активности
);
```

### 📁 **Поддержка больших файлов:**

- Интеграция с локальным Bot API Server
- Поддержка файлов до 2GB
- Работа с `pathlib` и `tempfile`
- Автоматическая очистка временных файлов

### 🔒 **Безопасность:**

- Автоматическое удаление сообщений с токенами
- Локальное хранение токенов (не в памяти)
- Проверка прав доступа перед обработкой файлов
- Логирование всех критических операций

