"""
Telegram-бот ЧелКИТ "Профи" - КНОПКИ В 2-3 СТОЛБЦА
Как в @GETSIM - компактное меню
Запуск: python bot_columns.py
"""

import logging
import sqlite3
import datetime
import asyncio
import os
from aiogram import Bot, Dispatcher, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery, FSInputFile
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.memory import MemoryStorage

# ========== ТОКЕН ==========
TOKEN = "8687792341:AAH2DVd9QjCk9UgVwPw7KHA1Mt1LISnZKKI"
ADMIN_ID = 1007268735  # ЗАМЕНИ НА СВОЙ ID

# Логирование
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ========== ПАПКИ ==========
os.makedirs("images", exist_ok=True)
os.makedirs("user_docs", exist_ok=True)

# ========== БАЗА ДАННЫХ ==========
def init_db():
    try:
        conn = sqlite3.connect('chelkit.db')
        c = conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS users
                    (user_id INTEGER PRIMARY KEY, 
                     full_name TEXT, 
                     phone TEXT, 
                     reg_date TEXT,
                     last_active TEXT)''')
        conn.commit()
        conn.close()
        logger.info("✅ База данных готова")
        return True
    except Exception as e:
        logger.error(f"❌ Ошибка БД: {e}")
        return False

# ========== КНОПКИ В НЕСКОЛЬКО СТОЛБЦОВ ==========

def get_main_menu_keyboard():
    """Главное меню - кнопки в 2 столбца (как в @GETSIM)"""
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            # Первая строка - 2 кнопки
            [
                InlineKeyboardButton(text="📚 Специальности", callback_data="specialties"),
                InlineKeyboardButton(text="📄 Документы", callback_data="documents")
            ],
            # Вторая строка - 2 кнопки
            [
                InlineKeyboardButton(text="🏠 Общежитие", callback_data="dormitory"),
                InlineKeyboardButton(text="⏰ Сроки", callback_data="deadlines")
            ],
            # Третья строка - 2 кнопки
            [
                InlineKeyboardButton(text="📞 Контакты", callback_data="contacts"),
                InlineKeyboardButton(text="🎯 Льготы", callback_data="benefits")
            ],
            # Четвертая строка - 2 кнопки
            [
                InlineKeyboardButton(text="💰 Стипендии", callback_data="scholarship"),
                InlineKeyboardButton(text="🎓 Целевое", callback_data="target")
            ],
            # Пятая строка - 2 кнопки
            [
                InlineKeyboardButton(text="❓ Задать вопрос", callback_data="ask"),
                InlineKeyboardButton(text="📎 Отправить", callback_data="send_docs")
            ],
            # Шестая строка - 1 кнопка на всю ширину
            [
                InlineKeyboardButton(text="⚙️ ПРОФИЛЬ", callback_data="profile")
            ]
        ]
    )
    return keyboard

def get_profile_keyboard():
    """Кнопки профиля в 2 столбца"""
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="📋 Мои данные", callback_data="my_data"),
                InlineKeyboardButton(text="📝 Вопросы", callback_data="my_questions")
            ],
            [
                InlineKeyboardButton(text="📎 Документы", callback_data="my_docs"),
                InlineKeyboardButton(text="📊 Статистика", callback_data="stats")
            ],
            [
                InlineKeyboardButton(text="🔙 Назад в меню", callback_data="back_to_menu")
            ]
        ]
    )
    return keyboard

def get_phone_keyboard():
    """Клавиатура для телефона (Reply)"""
    from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="📱 Отправить телефон", request_contact=True)]
        ],
        resize_keyboard=True,
        one_time_keyboard=True
    )
    return keyboard

# ========== ТЕКСТЫ ==========

SPECIALTIES_TEXT = """
📚 *СПЕЦИАЛЬНОСТИ 2025-2026*

🔹 *08.02.08* Монтаж газоснабжения
   👉 3 г 10 мес

🔹 *09.02.07* Информационные системы
   👉 3 г 7 мес

🔹 *15.02.16* Технология машиностроения
   👉 3 г 10 мес

🔹 *23.02.07* Ремонт автотранспорта
   👉 3 г 10 мес

🔹 *43.02.15* Поварское дело
   👉 3 г 10 мес

🔹 *15.01.05* Сварщик
   👉 1 г 10 мес
"""

DOCUMENTS_TEXT = """
📄 *ДОКУМЕНТЫ*

✅ Паспорт
✅ Аттестат
✅ СНИЛС
✅ 4 фото 3x4
✅ Документы для льгот

📮 *Подача:* лично, email, Госуслуги
"""

DORMITORY_TEXT = """
🏠 *ОБЩЕЖИТИЕ*

📍 ул. Масленникова, 21а
🛏 Юноши: 40 мест
🛏 Девушки: 32 места
💰 1000 руб/мес
"""

DEADLINES_TEXT = """
⏰ *СРОКИ 2025*

📅 Начало: 20 июня
📅 Очная: до 15 августа
📅 Заочная: до 15 сентября

🕒 ПН-ЧТ: 9:00-16:30
🕒 ПТ: 9:00-16:00
"""

CONTACTS_TEXT = """
📞 *КОНТАКТЫ*

📞 8(351)254-59-88
📧 chelkit@yandex.ru
🌐 http://chtpgh.ru/
🏢 ул. Масленникова, 21
"""

BENEFITS_TEXT = """
🎯 *ЛЬГОТЫ*

✅ Дети-сироты
✅ Дети с инвалидностью
✅ Призеры олимпиад
✅ Дети военнослужащих
"""

# ========== ОБРАБОТЧИКИ ==========

async def show_main_menu(message: Message, bot: Bot):
    """Показывает главное меню с картинкой"""
    try:
        photo = FSInputFile("images/main_menu.jpg")
        await message.answer_photo(
            photo=photo,
            caption="🎓 *ЧелКИТ «Профи»*\nВыберите нужный раздел:",
            reply_markup=get_main_menu_keyboard()
        )
    except:
        await message.answer(
            "🎓 *ЧелКИТ «Профи»*\nВыберите нужный раздел:",
            reply_markup=get_main_menu_keyboard()
        )

async def cmd_start(message: Message):
    """Команда /start"""
    user_id = message.from_user.id
    
    # Проверка регистрации
    conn = sqlite3.connect('chelkit.db')
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
    user = c.fetchone()
    conn.close()
    
    if user:
        await show_main_menu(message, message.bot)
    else:
        await message.answer(
            "📱 *Для регистрации отправьте номер телефона:*",
            reply_markup=get_phone_keyboard()
        )

async def handle_contact(message: Message):
    """Получение контакта"""
    if message.contact:
        user_id = message.from_user.id
        phone = message.contact.phone_number
        full_name = message.from_user.full_name
        now = str(datetime.datetime.now())
        
        conn = sqlite3.connect('chelkit.db')
        c = conn.cursor()
        c.execute(
            "INSERT OR REPLACE INTO users VALUES (?, ?, ?, ?, ?)",
            (user_id, full_name, phone, now, now)
        )
        conn.commit()
        conn.close()
        
        # Убираем reply клавиатуру
        from aiogram.types import ReplyKeyboardRemove
        await message.answer(
            "✅ *Регистрация успешна!*",
            reply_markup=ReplyKeyboardRemove()
        )
        await show_main_menu(message, message.bot)
    else:
        await message.answer("Используйте кнопку отправки телефона")

async def handle_callback(callback: CallbackQuery, bot: Bot):
    """Обработка нажатий на кнопки"""
    data = callback.data
    
    # Показываем что обработали нажатие
    await callback.answer()
    
    # Удаляем старое сообщение с кнопками (опционально)
    await callback.message.delete()
    
    # Отправляем информацию с картинкой
    try:
        if data == "specialties":
            photo = FSInputFile("images/specialties.jpg")
            await callback.message.answer_photo(
                photo=photo,
                caption=SPECIALTIES_TEXT,
                reply_markup=get_main_menu_keyboard()
            )
        elif data == "documents":
            photo = FSInputFile("images/documents.jpg")
            await callback.message.answer_photo(
                photo=photo,
                caption=DOCUMENTS_TEXT,
                reply_markup=get_main_menu_keyboard()
            )
        elif data == "dormitory":
            photo = FSInputFile("images/dormitory.jpg")
            await callback.message.answer_photo(
                photo=photo,
                caption=DORMITORY_TEXT,
                reply_markup=get_main_menu_keyboard()
            )
        elif data == "deadlines":
            photo = FSInputFile("images/deadlines.jpg")
            await callback.message.answer_photo(
                photo=photo,
                caption=DEADLINES_TEXT,
                reply_markup=get_main_menu_keyboard()
            )
        elif data == "contacts":
            photo = FSInputFile("images/contacts.jpg")
            await callback.message.answer_photo(
                photo=photo,
                caption=CONTACTS_TEXT,
                reply_markup=get_main_menu_keyboard()
            )
        elif data == "benefits":
            photo = FSInputFile("images/benefits.jpg")
            await callback.message.answer_photo(
                photo=photo,
                caption=BENEFITS_TEXT,
                reply_markup=get_main_menu_keyboard()
            )
        elif data == "profile":
            await callback.message.answer(
                "⚙️ *ПРОФИЛЬ*\n\n"
                f"👤 {callback.from_user.full_name}\n"
                f"🆔 {callback.from_user.id}\n\n"
                f"📊 Всего запросов: 0",
                reply_markup=get_profile_keyboard()
            )
        elif data == "back_to_menu":
            await show_main_menu(callback.message, bot)
        elif data == "ask":
            await callback.message.answer(
                "❓ Напишите ваш вопрос:",
                reply_markup=get_main_menu_keyboard()
            )
        else:
            # Для остальных разделов без картинок
            await callback.message.answer(
                "🔄 Раздел в разработке",
                reply_markup=get_main_menu_keyboard()
            )
            
    except Exception as e:
        # Если картинки нет - просто текст
        if data == "specialties":
            await callback.message.answer(SPECIALTIES_TEXT, reply_markup=get_main_menu_keyboard())
        elif data == "documents":
            await callback.message.answer(DOCUMENTS_TEXT, reply_markup=get_main_menu_keyboard())
        elif data == "dormitory":
            await callback.message.answer(DORMITORY_TEXT, reply_markup=get_main_menu_keyboard())
        elif data == "deadlines":
            await callback.message.answer(DEADLINES_TEXT, reply_markup=get_main_menu_keyboard())
        elif data == "contacts":
            await callback.message.answer(CONTACTS_TEXT, reply_markup=get_main_menu_keyboard())
        elif data == "benefits":
            await callback.message.answer(BENEFITS_TEXT, reply_markup=get_main_menu_keyboard())
        else:
            await callback.message.answer("Выберите раздел", reply_markup=get_main_menu_keyboard())

# ========== ЗАПУСК ==========
async def main():
    print("=" * 50)
    print("ЗАПУСК БОТА С КНОПКАМИ В 2 СТОЛБЦА")
    print("=" * 50)
    
    if not init_db():
        return
    
    bot = Bot(token=TOKEN)
    dp = Dispatcher(storage=MemoryStorage())
    
    # Регистрация обработчиков
    dp.message.register(cmd_start, Command("start"))
    dp.message.register(handle_contact, F.contact)
    dp.callback_query.register(handle_callback)
    
    print("✅ Бот запущен!")
    print("📱 Открой Telegram и отправь /start")
    print("=" * 50)
    
    try:
        await dp.start_polling(bot)
    finally:
        await bot.session.close()

if __name__ == "__main__":
    asyncio.run(main())
