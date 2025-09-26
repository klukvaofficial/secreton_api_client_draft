import tempfile
import logging
import sqlite3
import threading
import time
from pathlib import Path
from typing import Optional, Dict
from datetime import datetime
from contextlib import contextmanager

from telegram import Update, Bot, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ConversationHandler,
    filters,
    ContextTypes,
)

from secreton_api_client import SyncSecretOnClient
from secreton_api_client.exceptions import (
    AuthenticationError,
    ValidationError,
    FileError,
    APIClientError,
)

# Настройка логирования
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Состояния конversации
WAITING_FOR_TOKEN = 1


class SyncUserDatabase:
    """Синхронная база данных пользователей."""

    def __init__(self, db_path: str = "users_sync.db"):
        self.db_path = db_path
        self._lock = threading.RLock()  # Для thread-safety
        self.init_db()

    @contextmanager
    def get_connection(self):
        """Thread-safe подключение к БД."""
        with self._lock:
            conn = sqlite3.connect(self.db_path, check_same_thread=False)
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


class SecretOnSyncBot:
    def __init__(self, telegram_token: str):
        self.application = Application.builder().token(telegram_token).build()
        self.db = SyncUserDatabase()

        # Поддерживаемые форматы
        self.supported_audio = {".mp3", ".wav", ".m4a", ".flac", ".aac", ".ogg"}
        self.supported_video = {".mp4", ".avi", ".mov", ".mkv", ".webm"}
        self.supported_formats = self.supported_audio | self.supported_video

        self.register_handlers()

    def register_handlers(self):
        """Регистрация всех синхронных обработчиков."""

        # Обработчик регистрации (ConversationHandler)
        registration_handler = ConversationHandler(
            entry_points=[CommandHandler("register", self.start_registration)],
            states={
                WAITING_FOR_TOKEN: [
                    MessageHandler(
                        filters.TEXT & ~filters.COMMAND, self.handle_token_input
                    )
                ]
            },
            fallbacks=[CommandHandler("cancel", self.cancel_registration)],
        )

        self.application.add_handler(registration_handler)

        # Команды
        self.application.add_handler(CommandHandler("start", self.cmd_start))
        self.application.add_handler(CommandHandler("help", self.cmd_help))
        self.application.add_handler(CommandHandler("balance", self.cmd_balance))
        self.application.add_handler(CommandHandler("profile", self.cmd_profile))
        self.application.add_handler(CommandHandler("logout", self.cmd_logout))
        self.application.add_handler(CommandHandler("stats", self.cmd_stats))

        # Обработчики файлов
        self.application.add_handler(
            MessageHandler(filters.AUDIO | filters.VOICE, self.handle_audio)
        )
        self.application.add_handler(MessageHandler(filters.VIDEO, self.handle_video))
        self.application.add_handler(
            MessageHandler(filters.Document.ALL, self.handle_document)
        )

        # Callback queries
        self.application.add_handler(CallbackQueryHandler(self.handle_callback))

        # Текстовые сообщения
        self.application.add_handler(MessageHandler(filters.TEXT, self.handle_text))

    def check_user_registered(self, user_id: int) -> bool:
        """Синхронная проверка регистрации."""
        return self.db.is_user_registered(user_id)

    def cmd_start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Синхронный обработчик команды /start."""
        user = update.effective_user
        user_id = user.id

        if self.check_user_registered(user_id):
            self.db.update_activity(user_id)

            # Клавиатура для зарегистрированных пользователей
            keyboard = [
                [InlineKeyboardButton("💰 Баланс", callback_data="check_balance")],
                [InlineKeyboardButton("👤 Профиль", callback_data="show_profile")],
                [InlineKeyboardButton("📊 Статистика", callback_data="show_stats")],
                [InlineKeyboardButton("🚪 Выйти", callback_data="logout")],
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)

            welcome_text = (
                f"👋 С возвращением, **{user.full_name}**!\n\n"
                "🤖 **SecretOn Multi-User Bot (Sync Version)**\n\n"
                "Вы зарегистрированы и можете обрабатывать файлы.\n\n"
                "📎 Отправьте аудио или видео файл для обработки!"
            )

            update.message.reply_text(
                welcome_text, parse_mode="Markdown", reply_markup=reply_markup
            )
        else:
            # Клавиатура для незарегистрированных пользователей
            keyboard = [
                [
                    InlineKeyboardButton(
                        "🔑 Регистрация", callback_data="start_register"
                    )
                ],
                [InlineKeyboardButton("📚 Справка", callback_data="show_help")],
                [InlineKeyboardButton("📊 Статистика", callback_data="show_stats")],
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)

            welcome_text = (
                f"👋 Привет, **{user.full_name}**!\n\n"
                "🤖 **SecretOn Multi-User Bot (Sync Version)**\n\n"
                "**Особенности синхронного бота:**\n"
                "• Использует `python-telegram-bot` библиотеку\n"
                "• Все операции выполняются синхронно\n"
                "• `SyncSecretOnClient` работает нативно\n"
                "• Thread-safe база данных SQLite\n\n"
                "Для использования необходима регистрация с вашим SecretOn токеном."
            )

            update.message.reply_text(
                welcome_text, parse_mode="Markdown", reply_markup=reply_markup
            )

    def cmd_help(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Синхронная справка."""
        user_id = update.effective_user.id

        if not self.check_user_registered(user_id):
            help_text = (
                "ℹ️ **Справка - Незарегистрированный пользователь**\n\n"
                "**SecretOn Multi-User Bot (Sync Version)**\n\n"
                "Этот бот использует **синхронный подход**:\n"
                "• `python-telegram-bot` вместо `aiogram`\n"
                "• `SyncSecretOnClient` без async/await\n"
                "• Синхронная SQLite база данных\n"
                "• Thread-safe операции\n\n"
                "**Для начала работы:**\n"
                "1. Получите токен на сайте SecretOn\n"
                "2. Используйте /register\n"
                "3. Введите ваш персональный токен\n"
                "4. Отправляйте файлы!"
            )
        else:
            help_text = (
                "ℹ️ **Справка - Зарегистрированный пользователь**\n\n"
                "**Поддерживаемые файлы:**\n"
                f"🎵 Аудио: {', '.join(self.supported_audio)}\n"
                f"🎬 Видео: {', '.join(self.supported_video)}\n\n"
                "**Команды:**\n"
                "/balance - проверить баланс\n"
                "/profile - информация о профиле\n"
                "/logout - выйти из аккаунта\n"
                "/stats - статистика бота\n\n"
                "**Синхронная обработка:**\n"
                "• Блокирующие операции\n"
                "• Последовательное выполнение\n"
                "• Простая отладка\n"
                "• Нативная работа с SyncSecretOnClient"
            )

        update.message.reply_text(help_text, parse_mode="Markdown")

    def start_registration(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Начало синхронной регистрации."""
        user_id = update.effective_user.id

        if self.check_user_registered(user_id):
            update.message.reply_text(
                "✅ **Вы уже зарегистрированы!**\n\n"
                "Для смены токена используйте /logout, затем /register."
            )
            return ConversationHandler.END

        register_text = (
            "🔑 **Синхронная регистрация**\n\n"
            "Для работы с ботом нужен ваш **SecretOn API токен**.\n\n"
            "**Получение токена:**\n"
            "1. 🌐 Откройте сайт SecretOn\n"
            "2. 👤 Войдите в личный кабинет\n"
            "3. ⚙️ Перейдите в настройки API\n"
            "4. 📋 Скопируйте токен\n\n"
            "**Особенности синхронной версии:**\n"
            "• Токен проверяется синхронно\n"
            "• Блокирующая операция\n"
            "• Простая обработка ошибок\n\n"
            "📝 **Отправьте ваш токен следующим сообщением:**"
        )

        update.message.reply_text(register_text, parse_mode="Markdown")
        return WAITING_FOR_TOKEN

    def handle_token_input(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Синхронная обработка ввода токена."""
        token = update.message.text.strip()
        user = update.effective_user

        if len(token) < 10:
            update.message.reply_text(
                "❌ **Токен слишком короткий**\n\n"
                "Убедитесь, что вы скопировали полный токен.\n"
                "Попробуйте еще раз или /cancel для отмены:"
            )
            return WAITING_FOR_TOKEN

        # Удаляем сообщение с токеном для безопасности
        try:
            update.message.delete()
        except Exception:
            pass

        check_msg = context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="🔄 **Проверяю токен синхронно...**\n\nОжидайте, может занять время.",
        )

        # СИНХРОННАЯ проверка токена
        try:
            with SyncSecretOnClient(token=token) as client:
                auth = client.get_auth()
                profile = client.profile.get_profile(auth)

                # Токен валиден, регистрируем пользователя СИНХРОННО
                self.db.register_user(
                    user_id=user.id,
                    username=user.username or "",
                    full_name=user.full_name,
                    secreton_token=token,
                )

                success_text = (
                    "🎉 **Регистрация успешна! (Sync Client)**\n\n"
                    f"👤 **Пользователь:** {user.full_name}\n"
                    f"💰 **Ваш баланс:** {profile.balance}₽\n"
                    f"🔧 **Режим:** Синхронный\n\n"
                    "✅ **Теперь можете отправлять файлы для обработки!**"
                )

                context.bot.edit_message_text(
                    chat_id=check_msg.chat_id,
                    message_id=check_msg.message_id,
                    text=success_text,
                    parse_mode="Markdown",
                )

                return ConversationHandler.END

        except AuthenticationError:
            context.bot.edit_message_text(
                chat_id=check_msg.chat_id,
                message_id=check_msg.message_id,
                text=(
                    "❌ **Неверный токен (Sync Check)**\n\n"
                    "Токен не прошёл синхронную проверку.\n\n"
                    "**Возможные причины:**\n"
                    "• Токен скопирован не полностью\n"
                    "• Токен истёк или отозван\n\n"
                    "Попробуйте /register снова."
                ),
                parse_mode="Markdown",
            )
            return ConversationHandler.END

        except Exception as e:
            logger.error(f"Ошибка синхронной проверки токена: {e}")
            context.bot.edit_message_text(
                chat_id=check_msg.chat_id,
                message_id=check_msg.message_id,
                text=f"❌ **Ошибка:** {str(e)}\n\nПопробуйте позже.",
                parse_mode="Markdown",
            )
            return ConversationHandler.END

    def cancel_registration(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Отмена регистрации."""
        update.message.reply_text("🚫 **Регистрация отменена**")
        return ConversationHandler.END

    def cmd_balance(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Синхронная проверка баланса."""
        user_id = update.effective_user.id

        if not self.check_user_registered(user_id):
            update.message.reply_text(
                "❌ Вы не зарегистрированы. Используйте /register"
            )
            return

        token = self.db.get_user_token(user_id)
        check_msg = update.message.reply_text("💰 Проверяю ваш баланс синхронно...")

        # СИНХРОННАЯ проверка баланса
        try:
            with SyncSecretOnClient(token=token) as client:
                auth = client.get_auth()
                profile = client.profile.get_profile(auth)

                self.db.update_activity(user_id)

                balance_text = (
                    f"💰 **Ваш баланс SecretOn (Sync)**\n\n"
                    f"💳 **Баланс:** {profile.balance}₽\n"
                    f"👤 **SecretOn ID:** {getattr(profile, 'user_id', 'N/A')}\n"
                    f"🤖 **Telegram ID:** {user_id}\n"
                    f"🔧 **Клиент:** Синхронный\n\n"
                    f"📊 **Статус:** {'Активен' if profile.balance > 0 else 'Требуется пополнение'}"
                )

                if profile.balance < 10:
                    balance_text += "\n\n⚠️ **Низкий баланс!**"

                context.bot.edit_message_text(
                    chat_id=check_msg.chat_id,
                    message_id=check_msg.message_id,
                    text=balance_text,
                    parse_mode="Markdown",
                )

        except AuthenticationError:
            context.bot.edit_message_text(
                chat_id=check_msg.chat_id,
                message_id=check_msg.message_id,
                text="❌ **Токен недействителен**\n\nИспользуйте /logout и /register",
            )
        except Exception as e:
            context.bot.edit_message_text(
                chat_id=check_msg.chat_id,
                message_id=check_msg.message_id,
                text=f"❌ **Ошибка:** {str(e)}",
            )

    def cmd_profile(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Синхронная информация о профиле."""
        user_id = update.effective_user.id

        if not self.check_user_registered(user_id):
            update.message.reply_text("❌ Не зарегистрированы. /register")
            return

        token = self.db.get_user_token(user_id)

        # СИНХРОННОЕ получение профиля
        try:
            with SyncSecretOnClient(token=token) as client:
                auth = client.get_auth()
                profile = client.profile.get_profile(auth)

                # Данные из локальной БД (синхронно)
                with self.db.get_connection() as conn:
                    cursor = conn.execute(
                        "SELECT registered_at, last_activity FROM users WHERE user_id = ?",
                        (user_id,),
                    )
                    user_data = cursor.fetchone()

                profile_text = (
                    f"👤 **Профиль (Sync Version)**\n\n"
                    f"**Telegram:**\n"
                    f"• Имя: {update.effective_user.full_name}\n"
                    f"• Username: @{update.effective_user.username or 'не указан'}\n"
                    f"• ID: `{user_id}`\n\n"
                    f"**SecretOn API:**\n"
                    f"• Баланс: {profile.balance}₽\n"
                    f"• ID: {getattr(profile, 'user_id', 'N/A')}\n"
                    f"• Клиент: Синхронный\n\n"
                    f"**Активность в боте:**\n"
                    f"• Зарегистрирован: {user_data[0][:16] if user_data else 'N/A'}\n"
                    f"• Последний раз: {user_data[1][:16] if user_data else 'N/A'}"
                )

                update.message.reply_text(profile_text, parse_mode="Markdown")
                self.db.update_activity(user_id)

        except Exception as e:
            logger.error(f"Ошибка получения профиля {user_id}: {e}")
            update.message.reply_text(f"❌ Ошибка: {str(e)}")

    def cmd_logout(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Синхронный выход из аккаунта."""
        user_id = update.effective_user.id

        if not self.check_user_registered(user_id):
            update.message.reply_text("❌ Вы не зарегистрированы.")
            return

        # Подтверждение через инлайн клавиатуру
        keyboard = [
            [
                InlineKeyboardButton(
                    "✅ Да, выйти", callback_data=f"confirm_logout_{user_id}"
                )
            ],
            [InlineKeyboardButton("❌ Отменить", callback_data="cancel_logout")],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        update.message.reply_text(
            "⚠️ **Подтверждение выхода (Sync)**\n\n"
            "Вы уверены? После выхода потребуется повторная регистрация.",
            reply_markup=reply_markup,
            parse_mode="Markdown",
        )

    def cmd_stats(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Синхронная статистика бота."""
        stats = self.db.get_user_stats()

        stats_text = (
            f"📊 **Статистика SecretOn Bot (Sync)**\n\n"
            f"👥 **Пользователи:**\n"
            f"• Активных: {stats['active']}\n"
            f"• Всего: {stats['total']}\n\n"
            f"🔧 **Технические характеристики:**\n"
            f"• Библиотека: python-telegram-bot\n"
            f"• Клиент: SyncSecretOnClient\n"
            f"• База данных: SQLite (синхронная)\n"
            f"• Форматов: {len(self.supported_formats)}\n\n"
            f"ℹ️ Для регистрации: /register"
        )

        update.message.reply_text(stats_text, parse_mode="Markdown")

    def handle_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик инлайн кнопок."""
        query = update.callback_query
        query.answer()

        data = query.data
        user_id = update.effective_user.id

        if data == "start_register":
            # Запускаем регистрацию через callback
            context.bot.send_message(
                chat_id=query.message.chat_id,
                text="🔑 Используйте команду /register для начала регистрации.",
            )

        elif data == "check_balance":
            # Проверяем баланс через callback
            self.cmd_balance(update, context)

        elif data == "show_profile":
            self.cmd_profile(update, context)

        elif data == "show_stats":
            self.cmd_stats(update, context)

        elif data == "show_help":
            self.cmd_help(update, context)

        elif data.startswith("confirm_logout_"):
            logout_user_id = int(data.split("_")[-1])
            if user_id == logout_user_id:
                # СИНХРОННЫЙ logout
                self.db.deactivate_user(user_id)
                query.edit_message_text(
                    "👋 **Вы вышли из аккаунта (Sync)**\n\n"
                    "Токен удален. Используйте /register для повторной регистрации."
                )
            else:
                query.edit_message_text("❌ Ошибка авторизации")

        elif data == "cancel_logout":
            query.edit_message_text("✅ **Выход отменен**")

    def handle_audio(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Синхронная обработка аудио файлов."""
        if not self.check_user_registered(update.effective_user.id):
            update.message.reply_text("❌ Регистрация обязательна. /register")
            return

        # Определяем тип файла
        if update.message.audio:
            file_info = update.message.audio
            file_name = file_info.file_name or f"audio_{update.message.message_id}.mp3"
            file_type = "🎵 Аудио"
        elif update.message.voice:
            file_info = update.message.voice
            file_name = f"voice_{update.message.message_id}.ogg"
            file_type = "🎤 Голосовое"
        else:
            update.message.reply_text("❌ Неподдерживаемый тип файла")
            return

        self.process_file_sync(
            update,
            context,
            file_info,
            file_name,
            getattr(file_info, "duration", 0),
            file_type,
        )

    def handle_video(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Синхронная обработка видео."""
        if not self.check_user_registered(update.effective_user.id):
            update.message.reply_text("❌ Регистрация обязательна. /register")
            return

        video = update.message.video
        file_name = video.file_name or f"video_{update.message.message_id}.mp4"

        self.process_file_sync(
            update, context, video, file_name, video.duration, "🎬 Видео"
        )

    def handle_document(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Синхронная обработка документов."""
        if not self.check_user_registered(update.effective_user.id):
            update.message.reply_text("❌ Регистрация обязательна. /register")
            return

        document = update.message.document
        file_name = document.file_name or f"document_{update.message.message_id}"

        # Проверяем расширение
        file_path = Path(file_name)
        if file_path.suffix.lower() not in self.supported_formats:
            update.message.reply_text(
                f"❌ **Неподдерживаемый формат:** `{file_path.suffix}`\n\n"
                f"**Поддерживается:** {', '.join(self.supported_formats)}",
                parse_mode="Markdown",
            )
            return

        self.process_file_sync(
            update, context, document, file_name, None, "📄 Документ"
        )

    def process_file_sync(
        self,
        update: Update,
        context: ContextTypes.DEFAULT_TYPE,
        file_info,
        file_name: str,
        duration: Optional[int],
        file_type: str,
    ):
        """СИНХРОННАЯ обработка файла."""
        user_id = update.effective_user.id
        token = self.db.get_user_token(user_id)

        # Информация о файле
        size_mb = file_info.file_size / (1024 * 1024) if file_info.file_size else 0

        info_text = f"**{file_type} получен (SYNC Processing)**\n\n"
        info_text += f"👤 **От:** {update.effective_user.full_name}\n"
        info_text += f"📁 **Файл:** `{file_name}`\n"
        info_text += f"📏 **Размер:** {size_mb:.1f} MB\n"

        if duration:
            minutes, seconds = divmod(duration, 60)
            info_text += f"⏱ **Длительность:** {minutes}:{seconds:02d}\n"

        info_text += f"🔧 **Обработчик:** Синхронный python-telegram-bot\n"
        info_text += f"🕒 **Время:** {datetime.now().strftime('%H:%M:%S')}\n\n"
        info_text += "⏳ **Статус:** Загрузка файла..."

        status_msg = update.message.reply_text(info_text, parse_mode="Markdown")

        temp_file_path = None
        try:
            # СИНХРОННАЯ загрузка файла
            file_obj = context.bot.get_file(file_info.file_id)

            file_path = Path(file_name)
            suffix = file_path.suffix or ".tmp"

            # Создаем временный файл
            with tempfile.NamedTemporaryFile(
                suffix=suffix, delete=False, prefix=f"secreton_sync_{user_id}_"
            ) as temp_file:
                temp_file_path = Path(temp_file.name)

            # СИНХРОННОЕ скачивание
            file_obj.download(custom_path=temp_file_path)

            logger.info(f"Файл скачан синхронно: {temp_file_path}")

            context.bot.edit_message_text(
                chat_id=status_msg.chat_id,
                message_id=status_msg.message_id,
                text=info_text.replace(
                    "Загрузка файла...",
                    "✅ Файл загружен\n🔄 Обработка через SYNC клиент...",
                ),
                parse_mode="Markdown",
            )

            # ПОЛНОСТЬЮ СИНХРОННАЯ обработка через SecretOn API
            result = self.process_with_sync_secreton(
                temp_file_path,
                file_name,
                context,
                status_msg,
                info_text,
                token,
                user_id,
            )

            if result:
                self.db.update_activity(user_id)

                final_text = info_text.replace(
                    "🔄 Обработка через SYNC клиент...",
                    "🎉 **Обработка завершена! (SYNC)**",
                )
                final_text += f"\n\n📄 **Результат:**\n"

                if len(result) <= 2000:
                    final_text += f"```\n{result}\n```"
                    context.bot.edit_message_text(
                        chat_id=status_msg.chat_id,
                        message_id=status_msg.message_id,
                        text=final_text,
                        parse_mode="Markdown",
                    )
                else:
                    context.bot.edit_message_text(
                        chat_id=status_msg.chat_id,
                        message_id=status_msg.message_id,
                        text=final_text,
                        parse_mode="Markdown",
                    )

                    # Отправляем результат файлом
                    with tempfile.NamedTemporaryFile(
                        mode="w", suffix=".txt", delete=False, encoding="utf-8"
                    ) as result_file:
                        result_file.write(result)
                        result_file_path = result_file.name

                    context.bot.send_document(
                        chat_id=update.effective_chat.id,
                        document=open(result_file_path, "rb"),
                        filename=f"result_sync_{file_path.stem}_{user_id}.txt",
                        caption=f"📄 **Результат (SYNC)**\n`{file_name}`",
                    )

                    # Удаляем временный файл результата
                    Path(result_file_path).unlink()

            else:
                context.bot.edit_message_text(
                    chat_id=status_msg.chat_id,
                    message_id=status_msg.message_id,
                    text=info_text.replace(
                        "🔄 Обработка через SYNC клиент...", "❌ **Ошибка обработки**"
                    ),
                    parse_mode="Markdown",
                )

        except Exception as e:
            logger.error(
                f"Ошибка синхронной обработки файла {file_name} для пользователя {user_id}: {e}"
            )
            context.bot.edit_message_text(
                chat_id=status_msg.chat_id,
                message_id=status_msg.message_id,
                text=f"❌ **Ошибка (SYNC):**\n`{str(e)}`",
                parse_mode="Markdown",
            )

        finally:
            # Очистка временного файла
            if temp_file_path and temp_file_path.exists():
                try:
                    temp_file_path.unlink()
                    logger.info(f"Временный файл удален (sync): {temp_file_path}")
                except Exception as e:
                    logger.error(f"Не удалось удалить временный файл: {e}")

    def process_with_sync_secreton(
        self,
        file_path: Path,
        original_filename: str,
        context: ContextTypes.DEFAULT_TYPE,
        status_msg,
        base_info: str,
        user_token: str,
        user_id: int,
    ) -> Optional[str]:
        """ПОЛНОСТЬЮ СИНХРОННАЯ обработка через SecretOn API."""

        try:
            # ВСЁ СИНХРОННО - никакого async/await!
            with SyncSecretOnClient(token=user_token) as client:
                auth = client.get_auth()

                # Обновляем статус
                context.bot.edit_message_text(
                    chat_id=status_msg.chat_id,
                    message_id=status_msg.message_id,
                    text=base_info.replace(
                        "🔄 Обработка через SYNC клиент...",
                        "📋 Получаю сервисы (SYNC)...",
                    ),
                    parse_mode="Markdown",
                )

                # СИНХРОННО получаем сервисы
                services = client.orders.get_service_types(auth)
                if not services:
                    raise Exception("Нет доступных сервисов")

                service = services[0]
                logger.info(f"Выбран сервис (sync): {service.name}")

                # СИНХРОННО проверяем баланс
                context.bot.edit_message_text(
                    chat_id=status_msg.chat_id,
                    message_id=status_msg.message_id,
                    text=base_info.replace(
                        "📋 Получаю сервисы (SYNC)...", "💰 Проверяю баланс (SYNC)..."
                    ),
                    parse_mode="Markdown",
                )

                profile = client.profile.get_profile(auth)
                if profile.balance < service.price:
                    raise Exception(
                        f"Недостаточно средств.\n"
                        f"Требуется: {service.price}₽\n"
                        f"Доступно: {profile.balance}₽"
                    )

                # СИНХРОННО создаем заказ
                context.bot.edit_message_text(
                    chat_id=status_msg.chat_id,
                    message_id=status_msg.message_id,
                    text=base_info.replace(
                        "💰 Проверяю баланс (SYNC)...", "📦 Создаю заказ (SYNC)..."
                    ),
                    parse_mode="Markdown",
                )

                order = client.orders.create_order(
                    order_name=f"Sync Telegram Bot (User {user_id}): {original_filename}",
                    service_type=service.id,
                    file=str(file_path),
                    auth=auth,
                    tags=["telegram", "bot", "sync", f"user_{user_id}"],
                )

                logger.info(f"Заказ создан (sync): {order.order_id}")

                # СИНХРОННО оплачиваем
                client.orders.pay_order(order.order_id, auth)
                logger.info(f"Заказ оплачен (sync): {order.order_id}")

                # СИНХРОННЫЙ мониторинг
                context.bot.edit_message_text(
                    chat_id=status_msg.chat_id,
                    message_id=status_msg.message_id,
                    text=base_info.replace(
                        "📦 Создаю заказ (SYNC)...",
                        f"🔄 Мониторинг заказа (SYNC)\n📋 ID: `{order.order_id}`",
                    ),
                    parse_mode="Markdown",
                )

                max_attempts = 60  # 15 минут
                attempt = 0

                while attempt < max_attempts:
                    time.sleep(15)  # БЛОКИРУЮЩИЙ sleep!
                    attempt += 1

                    try:
                        # СИНХРОННАЯ проверка статуса
                        order_info = client.orders.get_order(order.order_id, auth)
                        status = order_info.status

                        # Обновляем прогресс
                        progress_text = base_info.replace(
                            "🔄 Мониторинг заказа (SYNC)",
                            f"🔄 **Обработка (SYNC)**\n\n"
                            f"📋 **Заказ:** `{order.order_id}`\n"
                            f"📊 **Статус:** `{status}`\n"
                            f"⏳ **Попытка:** {attempt}/{max_attempts}",
                        )

                        context.bot.edit_message_text(
                            chat_id=status_msg.chat_id,
                            message_id=status_msg.message_id,
                            text=progress_text,
                            parse_mode="Markdown",
                        )

                        if status == "completed":
                            # СИНХРОННО получаем результат
                            logger.info(f"Заказ завершен (sync): {order.order_id}")
                            result = client.orders.summarize_order(order.order_id, auth)
                            return result

                        elif status in ["failed", "cancelled", "expired"]:
                            raise Exception(f"Заказ завершился неуспешно: {status}")

                    except Exception as e:
                        logger.error(f"Ошибка проверки статуса (sync): {e}")
                        continue

                raise Exception("Превышено время ожидания")

        except Exception as e:
            error_msg = str(e)
            logger.error(f"Ошибка синхронной обработки: {error_msg}")

            context.bot.edit_message_text(
                chat_id=status_msg.chat_id,
                message_id=status_msg.message_id,
                text=base_info.replace(
                    "🔄 Обработка через SYNC клиент...",
                    f"❌ **Ошибка (SYNC):**\n{error_msg}",
                ),
                parse_mode="Markdown",
            )
            return None

    def handle_text(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработка текстовых сообщений."""
        if self.check_user_registered(update.effective_user.id):
            update.message.reply_text(
                "📎 **Отправьте файл для синхронной обработки**\n\n"
                "Поддерживаются аудио и видео файлы.\n"
                "/help для подробной информации."
            )
        else:
            update.message.reply_text(
                "👋 **Добро пожаловать!**\n\n"
                "/register для регистрации с SecretOn токеном."
            )

    def run(self):
        """Синхронный запуск бота."""
        logger.info("🚀 Запуск SecretOn Multi-User Bot (SYNC Version)...")

        # Статистика пользователей
        stats = self.db.get_user_stats()
        logger.info(f"👥 Пользователей: {stats['total']}, активных: {stats['active']}")

        # Запускаем бота СИНХРОННО
        self.application.run_polling()


# Главная функция для СИНХРОННОГО бота
def main():
    """Запуск синхронного multi-user бота."""

    TELEGRAM_TOKEN = "your-telegram-bot-token"

    bot = SecretOnSyncBot(telegram_token=TELEGRAM_TOKEN)

    try:
        bot.run()
    except KeyboardInterrupt:
        logger.info("👋 Синхронный бот остановлен пользователем")
    except Exception as e:
        logger.error(f"💥 Критическая ошибка: {e}")


if __name__ == "__main__":
    main()
