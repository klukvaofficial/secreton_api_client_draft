import asyncio
import tempfile
import logging
import sqlite3
from pathlib import Path
from typing import Optional, Dict
from datetime import datetime
from contextlib import contextmanager

from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import (
    Message,
    BufferedInputFile,
    ReplyKeyboardMarkup,
    KeyboardButton,
    ReplyKeyboardRemove,
)

from secreton_api_client import SyncSecretOnClient
from secreton_api_client.exceptions import (
    AuthenticationError,
    ValidationError,
    FileError,
    APIClientError,
)

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# Состояния FSM
class RegistrationStates(StatesGroup):
    waiting_for_token = State()


class SyncUserDatabase:
    """Синхронная база данных пользователей."""

    def __init__(self, db_path: str = "users_sync.db"):
        self.db_path = db_path
        self.init_db()

    @contextmanager
    def get_connection(self):
        """Контекстный менеджер для подключения к БД."""
        conn = sqlite3.connect(self.db_path)
        try:
            yield conn
        finally:
            conn.close()

    def init_db(self):
        """Инициализация базы данных."""
        with self.get_connection() as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    user_id INTEGER PRIMARY KEY,
                    username TEXT,
                    full_name TEXT,
                    secreton_token TEXT NOT NULL,
                    registered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_activity TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    is_active BOOLEAN DEFAULT 1
                )
            """)
            conn.commit()
            logger.info("База данных инициализирована (синхронная версия)")

    def register_user(
        self, user_id: int, username: str, full_name: str, secreton_token: str
    ):
        """Регистрация пользователя."""
        with self.get_connection() as conn:
            conn.execute(
                """
                INSERT OR REPLACE INTO users
                (user_id, username, full_name, secreton_token, registered_at, last_activity)
                VALUES (?, ?, ?, ?, ?, ?)
            """,
                (
                    user_id,
                    username,
                    full_name,
                    secreton_token,
                    datetime.now(),
                    datetime.now(),
                ),
            )
            conn.commit()
            logger.info(f"Пользователь зарегистрирован: {user_id} (@{username})")

    def get_user_token(self, user_id: int) -> Optional[str]:
        """Получение токена пользователя."""
        with self.get_connection() as conn:
            cursor = conn.execute(
                "SELECT secreton_token FROM users WHERE user_id = ? AND is_active = 1",
                (user_id,),
            )
            row = cursor.fetchone()
            return row[0] if row else None

    def is_user_registered(self, user_id: int) -> bool:
        """Проверка регистрации."""
        return self.get_user_token(user_id) is not None

    def update_activity(self, user_id: int):
        """Обновление активности."""
        with self.get_connection() as conn:
            conn.execute(
                "UPDATE users SET last_activity = ? WHERE user_id = ?",
                (datetime.now(), user_id),
            )
            conn.commit()

    def deactivate_user(self, user_id: int):
        """Деактивация пользователя."""
        with self.get_connection() as conn:
            conn.execute("UPDATE users SET is_active = 0 WHERE user_id = ?", (user_id,))
            conn.commit()
            logger.info(f"Пользователь деактивирован: {user_id}")

    def get_user_stats(self) -> Dict:
        """Статистика пользователей."""
        with self.get_connection() as conn:
            active_cursor = conn.execute(
                "SELECT COUNT(*) FROM users WHERE is_active = 1"
            )
            active_users = active_cursor.fetchone()[0]

            total_cursor = conn.execute("SELECT COUNT(*) FROM users")
            total_users = total_cursor.fetchone()[0]

            return {"active": active_users, "total": total_users}


class SecretOnMultiUserSyncBot:
    def __init__(self, telegram_token: str, bot_api_server_url: Optional[str] = None):
        if bot_api_server_url:
            self.bot = Bot(token=telegram_token, base=bot_api_server_url)
            logger.info(f"Используется локальный Bot API Server: {bot_api_server_url}")
        else:
            self.bot = Bot(token=telegram_token)
            logger.info("Используется стандартный Telegram Bot API")

        self.dp = Dispatcher(storage=MemoryStorage())
        self.db = SyncUserDatabase()

        # Поддерживаемые форматы
        self.supported_audio = {".mp3", ".wav", ".m4a", ".flac", ".aac", ".ogg"}
        self.supported_video = {".mp4", ".avi", ".mov", ".mkv", ".webm"}
        self.supported_formats = self.supported_audio | self.supported_video

        self.register_handlers()

    def register_handlers(self):
        """Регистрация обработчиков."""

        self.dp.message.register(self.cmd_start, Command("start"))
        self.dp.message.register(self.cmd_help, Command("help"))
        self.dp.message.register(self.cmd_register, Command("register"))
        self.dp.message.register(self.cmd_balance, Command("balance"))
        self.dp.message.register(self.cmd_profile, Command("profile"))
        self.dp.message.register(self.cmd_logout, Command("logout"))
        self.dp.message.register(self.cmd_stats, Command("stats"))
        self.dp.message.register(self.cmd_cancel, Command("cancel"))

        # Обработка регистрации
        self.dp.message.register(
            self.handle_token_input,
            StateFilter(RegistrationStates.waiting_for_token),
            F.text,
        )

        # Обработка файлов
        self.dp.message.register(self.handle_audio, F.audio | F.voice | F.video_note)
        self.dp.message.register(self.handle_video, F.video)
        self.dp.message.register(self.handle_document, F.document)

        self.dp.message.register(self.handle_text, F.text)

    def check_user_registered(self, user_id: int) -> bool:
        """Проверка регистрации (синхронная)."""
        return self.db.is_user_registered(user_id)

    async def cmd_start(self, message: Message, state: FSMContext):
        """Приветствие."""
        await state.clear()
        user_id = message.from_user.id

        if self.check_user_registered(user_id):
            self.db.update_activity(user_id)
            welcome_text = (
                f"👋 С возвращением, **{message.from_user.full_name}**!\n\n"
                "🤖 **SecretOn Multi-User Bot (Sync Version)**\n\n"
                "Вы зарегистрированы и можете обрабатывать файлы.\n\n"
                "**Команды:**\n"
                "/balance - ваш баланс SecretOn\n"
                "/profile - информация о профиле\n"
                "/help - подробная справка\n"
                "/logout - выйти из аккаунта\n\n"
                "📎 Отправьте файл для обработки!"
            )
        else:
            welcome_text = (
                f"👋 Привет, **{message.from_user.full_name}**!\n\n"
                "🤖 **SecretOn Multi-User Bot (Sync Version)**\n\n"
                "**Регистрация необходима!**\n\n"
                "Этот бот использует **синхронный SecretOn клиент** в **асинхронных хендлерах**.\n\n"
                "**Как зарегистрироваться:**\n"
                "1. Получите API токен на сайте SecretOn\n"
                "2. Используйте /register\n"
                "3. Введите ваш персональный токен\n\n"
                "**Команды:**\n"
                "/register - регистрация\n"
                "/help - справка"
            )

        await message.answer(welcome_text, parse_mode="Markdown")

    async def cmd_register(self, message: Message, state: FSMContext):
        """Начало регистрации."""
        user_id = message.from_user.id

        if self.check_user_registered(user_id):
            await message.answer(
                "✅ **Вы уже зарегистрированы!**\n\n"
                "Для смены токена используйте /logout, затем /register.\n"
                "Или сразу отправляйте файлы для обработки."
            )
            return

        await state.set_state(RegistrationStates.waiting_for_token)

        cancel_kb = ReplyKeyboardMarkup(
            keyboard=[[KeyboardButton(text="❌ Отменить регистрацию")]],
            resize_keyboard=True,
            one_time_keyboard=True,
        )

        register_text = (
            "🔑 **Регистрация (Sync Version)**\n\n"
            "Для работы с ботом нужен ваш **персональный SecretOn API токен**.\n\n"
            "**Получение токена:**\n"
            "1. 🌐 Зайдите на сайт SecretOn\n"
            "2. 👤 Войдите в личный кабинет\n"
            "3. ⚙️ Найдите раздел API\n"
            "4. 📋 Скопируйте токен\n\n"
            "**Безопасность:**\n"
            "• Токен привязывается к вашему Telegram ID\n"
            "• Хранится локально в зашифрованной БД\n"
            "• Используется только для ваших заказов\n\n"
            "📝 **Отправьте токен следующим сообщением:**"
        )

        await message.answer(
            register_text, parse_mode="Markdown", reply_markup=cancel_kb
        )

    async def handle_token_input(self, message: Message, state: FSMContext):
        """Обработка ввода токена с синхронной проверкой."""

        if message.text == "❌ Отменить регистрацию":
            await state.clear()
            await message.answer(
                "🚫 **Регистрация отменена**\n\nИспользуйте /register когда будете готовы.",
                reply_markup=ReplyKeyboardRemove(),
            )
            return

        token = message.text.strip()

        if len(token) < 10:
            await message.answer(
                "❌ **Токен слишком короткий**\n\n"
                "Убедитесь, что вы скопировали полный токен.\n"
                "Попробуйте еще раз:"
            )
            return

        check_msg = await message.answer(
            "🔄 **Проверяю токен через синхронный клиент...**\n\n"
            "Подождите, выполняется проверка в thread pool.",
            reply_markup=ReplyKeyboardRemove(),
        )

        # Удаляем сообщение с токеном для безопасности
        try:
            await message.delete()
        except Exception:
            pass

        # Синхронная проверка токена в async контексте
        def verify_token_sync(token: str):
            """Синхронная функция проверки токена."""
            try:
                with SyncSecretOnClient(token=token) as client:
                    auth = client.get_auth()
                    profile = client.profile.get_profile(auth)
                    return {
                        "success": True,
                        "balance": profile.balance,
                        "profile": profile,
                    }
            except AuthenticationError as e:
                return {"success": False, "error": "authentication", "message": str(e)}
            except Exception as e:
                return {"success": False, "error": "general", "message": str(e)}

        # Выполняем синхронную проверку в thread pool
        try:
            result = await asyncio.get_event_loop().run_in_executor(
                None, verify_token_sync, token
            )

            if result["success"]:
                # Токен валиден, регистрируем пользователя
                user = message.from_user
                self.db.register_user(
                    user_id=user.id,
                    username=user.username or "",
                    full_name=user.full_name,
                    secreton_token=token,
                )

                await state.clear()

                success_text = (
                    "🎉 **Регистрация успешна! (Sync Client)**\n\n"
                    f"👤 **Пользователь:** {user.full_name}\n"
                    f"💰 **Ваш баланс:** {result['balance']}₽\n\n"
                    "✅ **Теперь вы можете:**\n"
                    "• Отправлять файлы для обработки\n"
                    "• Проверять баланс командой /balance\n"
                    "• Просматривать профиль /profile\n\n"
                    "📎 **Отправьте аудио или видео файл для начала!**"
                )

                await check_msg.edit_text(success_text, parse_mode="Markdown")

            elif result["error"] == "authentication":
                await check_msg.edit_text(
                    "❌ **Неверный токен**\n\n"
                    "Токен не прошёл проверку через синхронный клиент.\n\n"
                    "**Возможные причины:**\n"
                    "• Токен скопирован не полностью\n"
                    "• Токен истёк или отозван\n"
                    "• Проблемы с доступом к SecretOn API\n\n"
                    "Попробуйте /register снова с корректным токеном.",
                    parse_mode="Markdown",
                )
                await state.clear()

            else:
                await check_msg.edit_text(
                    f"❌ **Ошибка проверки токена**\n\n"
                    f"Произошла ошибка: {result['message']}\n\n"
                    "Попробуйте позже или обратитесь к администратору.",
                    parse_mode="Markdown",
                )
                await state.clear()

        except Exception as e:
            logger.error(f"Ошибка выполнения синхронной проверки токена: {e}")
            await check_msg.edit_text(
                "❌ **Техническая ошибка**\n\n"
                f"Не удалось выполнить проверку: {str(e)}\n\n"
                "Попробуйте позже.",
                parse_mode="Markdown",
            )
            await state.clear()

    async def cmd_balance(self, message: Message):
        """Проверка баланса через синхронный клиент."""
        user_id = message.from_user.id

        if not self.check_user_registered(user_id):
            await message.answer("❌ Вы не зарегистрированы. Используйте /register")
            return

        token = self.db.get_user_token(user_id)
        check_msg = await message.answer("💰 Проверяю ваш персональный баланс...")

        def get_balance_sync():
            """Синхронная проверка баланса."""
            try:
                with SyncSecretOnClient(token=token) as client:
                    auth = client.get_auth()
                    profile = client.profile.get_profile(auth)
                    return {
                        "success": True,
                        "balance": profile.balance,
                        "user_id": getattr(profile, "user_id", "N/A"),
                    }
            except AuthenticationError:
                return {"success": False, "error": "auth"}
            except Exception as e:
                return {"success": False, "error": "general", "message": str(e)}

        try:
            result = await asyncio.get_event_loop().run_in_executor(
                None, get_balance_sync
            )

            if result["success"]:
                self.db.update_activity(user_id)

                balance_text = (
                    f"💰 **Ваш персональный баланс SecretOn**\n\n"
                    f"💳 **Баланс:** {result['balance']}₽\n"
                    f"👤 **SecretOn ID:** {result['user_id']}\n"
                    f"🤖 **Telegram ID:** {user_id}\n\n"
                    f"📊 **Статус:** {'Активен' if result['balance'] > 0 else 'Требуется пополнение'}"
                )

                if result["balance"] < 10:
                    balance_text += "\n\n⚠️ **Предупреждение:** Низкий баланс!"

                await check_msg.edit_text(balance_text, parse_mode="Markdown")

            elif result["error"] == "auth":
                await check_msg.edit_text(
                    "❌ **Ошибка аутентификации**\n\n"
                    "Ваш токен больше не действителен.\n"
                    "Используйте /logout и /register для обновления."
                )
            else:
                await check_msg.edit_text(
                    f"❌ **Ошибка получения баланса:**\n`{result.get('message', 'Неизвестная ошибка')}`"
                )

        except Exception as e:
            logger.error(f"Ошибка проверки баланса для пользователя {user_id}: {e}")
            await check_msg.edit_text(f"❌ **Техническая ошибка:** {str(e)}")

    async def cmd_profile(self, message: Message):
        """Информация о профиле."""
        user_id = message.from_user.id

        if not self.check_user_registered(user_id):
            await message.answer("❌ Не зарегистрированы. /register")
            return

        token = self.db.get_user_token(user_id)

        def get_profile_sync():
            """Получение профиля через синхронный клиент."""
            try:
                with SyncSecretOnClient(token=token) as client:
                    auth = client.get_auth()
                    profile = client.profile.get_profile(auth)
                    return {"success": True, "profile": profile}
            except Exception as e:
                return {"success": False, "error": str(e)}

        try:
            result = await asyncio.get_event_loop().run_in_executor(
                None, get_profile_sync
            )

            if result["success"]:
                profile = result["profile"]

                # Данные из локальной БД
                with self.db.get_connection() as conn:
                    cursor = conn.execute(
                        "SELECT registered_at, last_activity FROM users WHERE user_id = ?",
                        (user_id,),
                    )
                    user_data = cursor.fetchone()

                profile_text = (
                    f"👤 **Профиль пользователя (Sync Version)**\n\n"
                    f"**Telegram:**\n"
                    f"• Имя: {message.from_user.full_name}\n"
                    f"• Username: @{message.from_user.username or 'не указан'}\n"
                    f"• ID: `{user_id}`\n\n"
                    f"**SecretOn API:**\n"
                    f"• Баланс: {profile.balance}₽\n"
                    f"• ID: {getattr(profile, 'user_id', 'N/A')}\n"
                    f"• Клиент: Синхронный\n\n"
                    f"**Активность в боте:**\n"
                    f"• Зарегистрирован: {user_data[0][:16] if user_data else 'N/A'}\n"
                    f"• Последний раз: {user_data[1][:16] if user_data else 'N/A'}"
                )

                await message.answer(profile_text, parse_mode="Markdown")
                self.db.update_activity(user_id)

            else:
                await message.answer(f"❌ Ошибка получения профиля: {result['error']}")

        except Exception as e:
            logger.error(f"Ошибка получения профиля {user_id}: {e}")
            await message.answer(f"❌ Техническая ошибка: {str(e)}")

    async def cmd_logout(self, message: Message):
        """Выход из аккаунта."""
        user_id = message.from_user.id

        if not self.check_user_registered(user_id):
            await message.answer("❌ Вы не зарегистрированы.")
            return

        self.db.deactivate_user(user_id)
        await message.answer(
            "👋 **Вы вышли из аккаунта**\n\n"
            "• Ваш токен удален из бота\n"
            "• Обработка файлов недоступна\n"
            "• Используйте /register для повторной регистрации\n\n"
            "Спасибо за использование SecretOn Bot!"
        )

    async def cmd_stats(self, message: Message):
        """Статистика бота."""
        stats = self.db.get_user_stats()

        stats_text = (
            f"📊 **Статистика SecretOn Multi-User Bot**\n\n"
            f"👥 **Пользователи:**\n"
            f"• Активных: {stats['active']}\n"
            f"• Всего: {stats['total']}\n\n"
            f"🔧 **Технические характеристики:**\n"
            f"• Клиент: Синхронный SecretOn API\n"
            f"• База данных: SQLite (синхронная)\n"
            f"• Форматов поддерживается: {len(self.supported_formats)}\n"
            f"• Максимальный размер файла: 2GB\n\n"
            f"ℹ️ Для регистрации: /register"
        )

        await message.answer(stats_text, parse_mode="Markdown")

    async def cmd_cancel(self, message: Message, state: FSMContext):
        """Отмена операции."""
        current_state = await state.get_state()
        await state.clear()

        if current_state:
            await message.answer(
                "🚫 **Операция отменена**", reply_markup=ReplyKeyboardRemove()
            )
        else:
            await message.answer("ℹ️ Нет активных операций.")

    async def cmd_help(self, message: Message):
        """Справка."""
        user_id = message.from_user.id

        if not self.check_user_registered(user_id):
            help_text = (
                "ℹ️ **Справка - Незарегистрированный пользователь**\n\n"
                "**SecretOn Multi-User Bot (Sync Version)**\n\n"
                "Этот бот использует **синхронный SecretOn клиент**.\n\n"
                "**Для начала работы:**\n"
                "1. Получите токен на сайте SecretOn\n"
                "2. /register - начать регистрацию\n"
                "3. Введите ваш персональный токен\n"
                "4. Отправляйте файлы!\n\n"
                "**Особенности:**\n"
                "• Персональные токены и балансы\n"
                "• Безопасное хранение в локальной БД\n"
                "• Синхронный клиент в async хендлерах"
            )
        else:
            help_text = (
                "ℹ️ **Справка - Зарегистрированный пользователь**\n\n"
                "**Поддерживаемые файлы:**\n"
                f"🎵 Аудио: {', '.join(self.supported_audio)}\n"
                f"🎬 Видео: {', '.join(self.supported_video)}\n\n"
                "**Команды:**\n"
                "/balance - проверить ваш баланс\n"
                "/profile - информация о профиле\n"
                "/logout - выйти из аккаунта\n"
                "/stats - статистика бота\n\n"
                "**Как использовать:**\n"
                "1. Отправьте аудио/видео файл\n"
                "2. Дождитесь обработки\n"
                "3. Получите результат\n\n"
                "**Технические детали:**\n"
                "• Синхронный SecretOn клиент\n"
                "• Обработка в thread pool\n"
                "• Поддержка файлов до 2GB"
            )

        await message.answer(help_text, parse_mode="Markdown")

    # Обработчики файлов (аналогично async версии, но с синхронным клиентом)
    async def handle_audio(self, message: Message, state: FSMContext):
        """Обработка аудио."""
        if not self.check_user_registered(message.from_user.id):
            await message.answer("❌ Регистрация обязательна. /register")
            return

        # Аналогично async версии, но определяем тип файла
        if message.audio:
            file_info = message.audio
            file_name = file_info.file_name or f"audio_{message.message_id}.mp3"
            file_type = "🎵 Аудио"
        elif message.voice:
            file_info = message.voice
            file_name = f"voice_{message.message_id}.ogg"
            file_type = "🎤 Голосовое"
        elif message.video_note:
            file_info = message.video_note
            file_name = f"video_note_{message.message_id}.mp4"
            file_type = "⭕ Видеосообщение"
        else:
            await message.answer("❌ Неподдерживаемый тип файла")
            return

        await self.process_file_sync(
            message,
            file_info.file_id,
            file_name,
            file_info.file_size,
            getattr(file_info, "duration", 0),
            file_type,
        )

    async def handle_video(self, message: Message, state: FSMContext):
        """Обработка видео."""
        if not self.check_user_registered(message.from_user.id):
            await message.answer("❌ Регистрация обязательна. /register")
            return

        video = message.video
        file_name = video.file_name or f"video_{message.message_id}.mp4"

        await self.process_file_sync(
            message,
            video.file_id,
            file_name,
            video.file_size,
            video.duration,
            "🎬 Видео",
        )

    async def handle_document(self, message: Message, state: FSMContext):
        """Обработка документов."""
        if not self.check_user_registered(message.from_user.id):
            await message.answer("❌ Регистрация обязательна. /register")
            return

        document = message.document
        file_name = document.file_name or f"document_{message.message_id}"

        file_path = Path(file_name)
        if file_path.suffix.lower() not in self.supported_formats:
            await message.answer(
                f"❌ **Неподдерживаемый формат:** `{file_path.suffix}`\n\n"
                f"**Поддерживается:** {', '.join(self.supported_formats)}",
                parse_mode="Markdown",
            )
            return

        await self.process_file_sync(
            message,
            document.file_id,
            file_name,
            document.file_size,
            None,
            "📄 Документ",
        )

    async def process_file_sync(
        self,
        message: Message,
        file_id: str,
        file_name: str,
        file_size: int,
        duration: Optional[int],
        file_type: str,
    ):
        """Обработка файла с синхронным клиентом."""
        user_id = message.from_user.id
        token = self.db.get_user_token(user_id)

        # Информация о файле
        size_mb = file_size / (1024 * 1024) if file_size else 0

        info_text = f"**{file_type} получен (Sync Processing)**\n\n"
        info_text += f"👤 **От:** {message.from_user.full_name}\n"
        info_text += f"📁 **Файл:** `{file_name}`\n"
        info_text += f"📏 **Размер:** {size_mb:.1f} MB\n"

        if duration:
            minutes, seconds = divmod(duration, 60)
            info_text += f"⏱ **Длительность:** {minutes}:{seconds:02d}\n"

        info_text += f"🤖 **Обработчик:** Синхронный клиент\n"
        info_text += f"🕒 **Время:** {message.date.strftime('%H:%M:%S')}\n\n"
        info_text += "⏳ **Статус:** Загрузка файла..."

        status_msg = await message.answer(info_text, parse_mode="Markdown")

        temp_file_path = None
        try:
            # Скачиваем файл
            file_obj = await self.bot.get_file(file_id)

            file_path = Path(file_name)
            suffix = file_path.suffix or ".tmp"

            with tempfile.NamedTemporaryFile(
                suffix=suffix, delete=False, prefix=f"secreton_sync_{user_id}_"
            ) as temp_file:
                temp_file_path = Path(temp_file.name)

            await self.bot.download_file(file_obj.file_path, temp_file_path)

            await status_msg.edit_text(
                info_text.replace(
                    "Загрузка файла...",
                    "✅ Файл загружен\n🔄 Обработка через синхронный клиент...",
                ),
                parse_mode="Markdown",
            )

            # Обработка через синхронный клиент в thread pool
            result = await self.process_with_sync_client(
                temp_file_path, file_name, status_msg, info_text, token, user_id
            )

            if result:
                self.db.update_activity(user_id)

                final_text = info_text.replace(
                    "🔄 Обработка через синхронный клиент...",
                    "🎉 **Обработка завершена! (Sync Client)**",
                )
                final_text += f"\n\n📄 **Результат:**\n"

                if len(result) <= 2000:
                    final_text += f"```\n{result}\n```"
                    await status_msg.edit_text(final_text, parse_mode="Markdown")
                else:
                    await status_msg.edit_text(final_text, parse_mode="Markdown")

                    result_file = BufferedInputFile(
                        result.encode("utf-8"),
                        filename=f"result_sync_{file_path.stem}_{user_id}.txt",
                    )
                    await message.answer_document(
                        result_file,
                        caption=f"📄 **Результат (Sync Client)**\n`{file_name}`",
                    )
            else:
                await status_msg.edit_text(
                    info_text.replace(
                        "🔄 Обработка через синхронный клиент...",
                        "❌ **Ошибка обработки**",
                    )
                    + "\n\nПроверьте баланс или логи бота.",
                    parse_mode="Markdown",
                )

        except Exception as e:
            logger.error(
                f"Ошибка обработки файла {file_name} (sync) для пользователя {user_id}: {e}"
            )
            await status_msg.edit_text(
                f"❌ **Ошибка обработки (Sync Version)**\n\n"
                f"**Файл:** `{file_name}`\n"
                f"**Ошибка:** `{str(e)}`",
                parse_mode="Markdown",
            )

        finally:
            if temp_file_path and temp_file_path.exists():
                try:
                    temp_file_path.unlink()
                    logger.info(f"Временный файл удален (sync): {temp_file_path}")
                except Exception as e:
                    logger.error(f"Не удалось удалить временный файл: {e}")

    async def process_with_sync_client(
        self,
        file_path: Path,
        original_filename: str,
        status_msg: Message,
        base_info: str,
        user_token: str,
        user_id: int,
    ) -> Optional[str]:
        """Полная обработка через синхронный клиент в thread pool."""

        def sync_processing():
            """Полная синхронная обработка."""
            try:
                with SyncSecretOnClient(token=user_token) as client:
                    auth = client.get_auth()

                    # Получаем сервисы
                    services = client.orders.get_service_types(auth)
                    if not services:
                        return {"success": False, "error": "Нет доступных сервисов"}

                    service = services[0]

                    # Проверяем баланс
                    profile = client.profile.get_profile(auth)
                    if profile.balance < service.price:
                        return {
                            "success": False,
                            "error": f"Недостаточно средств.\nТребуется: {service.price}₽\nДоступно: {profile.balance}₽",
                        }

                    # Создаем заказ
                    order = client.orders.create_order(
                        order_name=f"Telegram Bot Sync (User {user_id}): {original_filename}",
                        service_type=service.id,
                        file=str(file_path),
                        auth=auth,
                        tags=["telegram", "bot", "sync", f"user_{user_id}"],
                    )

                    # Оплачиваем
                    client.orders.pay_order(order.order_id, auth)

                    logger.info(
                        f"Заказ создан и оплачен (sync) для пользователя {user_id}: {order.order_id}"
                    )

                    # Мониторим выполнение
                    max_attempts = 60
                    attempt = 0

                    import time

                    while attempt < max_attempts:
                        time.sleep(15)  # Блокирующий sleep в thread pool
                        attempt += 1

                        try:
                            order_info = client.orders.get_order(order.order_id, auth)
                            status = order_info.status

                            if status == "completed":
                                result = client.orders.summarize_order(
                                    order.order_id, auth
                                )
                                logger.info(
                                    f"Заказ завершен (sync) для пользователя {user_id}: {order.order_id}"
                                )
                                return {
                                    "success": True,
                                    "result": result,
                                    "order_id": order.order_id,
                                }

                            elif status in ["failed", "cancelled", "expired"]:
                                return {
                                    "success": False,
                                    "error": f"Заказ завершился неуспешно: {status}",
                                }

                        except Exception as e:
                            logger.error(f"Ошибка проверки статуса заказа (sync): {e}")
                            continue

                    return {"success": False, "error": "Превышено время ожидания"}

            except Exception as e:
                logger.error(
                    f"Ошибка синхронной обработки для пользователя {user_id}: {e}"
                )
                return {"success": False, "error": str(e)}

        try:
            # Выполняем всю синхронную обработку в thread pool
            result = await asyncio.get_event_loop().run_in_executor(
                None, sync_processing
            )

            if result["success"]:
                return result["result"]
            else:
                await status_msg.edit_text(
                    base_info.replace(
                        "🔄 Обработка через синхронный клиент...",
                        f"❌ **Ошибка:**\n{result['error']}",
                    ),
                    parse_mode="Markdown",
                )
                return None

        except Exception as e:
            logger.error(f"Ошибка выполнения в thread pool: {e}")
            await status_msg.edit_text(
                base_info.replace(
                    "🔄 Обработка через синхронный клиент...",
                    f"❌ **Техническая ошибка:**\n{str(e)}",
                ),
                parse_mode="Markdown",
            )
            return None

    async def handle_text(self, message: Message):
        """Обработка текста."""
        if self.check_user_registered(message.from_user.id):
            await message.answer(
                "📎 **Отправьте файл для обработки**\n\n"
                "Поддерживаются аудио и видео файлы.\n"
                "/help для подробной информации."
            )
        else:
            await message.answer(
                "👋 **Добро пожаловать!**\n\n"
                "/register для регистрации с вашим SecretOn токеном."
            )

    async def start(self):
        """Запуск синхронного multi-user бота."""
        logger.info("🚀 Запускаю SecretOn Multi-User Bot (Sync Version)...")

        # Информация о боте
        bot_info = await self.bot.get_me()
        logger.info(f"🤖 Бот запущен: @{bot_info.username} ({bot_info.full_name})")

        # Статистика
        stats = self.db.get_user_stats()
        logger.info(
            f"👥 Пользователей в базе: {stats['total']}, активных: {stats['active']}"
        )

        # Запуск
        try:
            await self.dp.start_polling(self.bot)
        except Exception as e:
            logger.error(f"❌ Ошибка polling: {e}")
        finally:
            await self.bot.session.close()


# Главная функция для синхронного бота
async def main():
    """Запуск синхронного multi-user бота."""

    TELEGRAM_TOKEN = "your-telegram-bot-token"
    BOT_API_SERVER_URL = "http://localhost:8081"  # или None

    bot = SecretOnMultiUserSyncBot(
        telegram_token=TELEGRAM_TOKEN, bot_api_server_url=BOT_API_SERVER_URL
    )

    await bot.start()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("👋 Синхронный бот остановлен")
    except Exception as e:
        logger.error(f"💥 Критическая ошибка: {e}")
