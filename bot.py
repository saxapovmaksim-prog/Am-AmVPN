import asyncio
import sqlite3
from datetime import datetime, timedelta

from aiogram import Bot, Dispatcher, types, F
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import CommandStart
from aiogram.enums import ParseMode

# ===== НАСТРОЙКИ =====
BOT_TOKEN = "8277007634:AAFJaW4pws234-gOuC2CsbFXJZ0DLKFTo4Q"
CRYPTO_TOKEN = "555209:AAvWWWiQt0ERfGAjTGozQDu1HEAZICFi4ZW"

ADMINS = [2032012311]  # твой ID

bot = Bot(token=BOT_TOKEN, parse_mode=ParseMode.HTML)
dp = Dispatcher()

# ===== БАЗА =====
db = sqlite3.connect("db.db")
cursor = db.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER PRIMARY KEY,
    reg_date TEXT,
    sub_until TEXT
)
""")

db.commit()

# ===== МЕНЮ =====
def main_menu(user_id):
    buttons = [
        [InlineKeyboardButton(text="Личный кабинет", callback_data="profile")],
        [InlineKeyboardButton(text="Выбрать тариф", callback_data="tariffs")],
        [InlineKeyboardButton(text="Скачать VPN", callback_data="download")],
        [InlineKeyboardButton(text="Поддержка", callback_data="support")]
    ]

    if user_id in ADMINS:
        buttons.append([InlineKeyboardButton(text="Админ панель", callback_data="admin")])

    return InlineKeyboardMarkup(inline_keyboard=buttons)

# ===== START =====
@dp.message(CommandStart())
async def start(message: types.Message):
    user_id = message.from_user.id

    cursor.execute("SELECT * FROM users WHERE user_id=?", (user_id,))
    if not cursor.fetchone():
        cursor.execute(
            "INSERT INTO users VALUES (?, ?, ?)",
            (user_id, datetime.now().strftime("%Y-%m-%d"), None)
        )
        db.commit()

    await message.answer(
        "Добро пожаловать в VPN сервис\n\nГлавное меню:",
        reply_markup=main_menu(user_id)
    )

# ===== ПРОФИЛЬ =====
@dp.callback_query(F.data == "profile")
async def profile(callback: types.CallbackQuery):
    user_id = callback.from_user.id

    cursor.execute("SELECT reg_date, sub_until FROM users WHERE user_id=?", (user_id,))
    data = cursor.fetchone()

    reg = data[0]
    sub = data[1] if data[1] else "Нет"

    text = f"""
<b>Личный кабинет</b>

ID: <code>{user_id}</code>
Дата регистрации: {reg}
Подписка до: {sub}
"""

    await callback.message.edit_text(text, reply_markup=main_menu(user_id))

# ===== ТАРИФЫ =====
@dp.callback_query(F.data == "tariffs")
async def tariffs(callback: types.CallbackQuery):
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="1 месяц - 99₽ (1.1$)", callback_data="buy_1")],
        [InlineKeyboardButton(text="3 месяца - 299₽ (3.3$)", callback_data="buy_3")],
        [InlineKeyboardButton(text="1 год - 600₽ (6.6$)", callback_data="buy_12")],
        [InlineKeyboardButton(text="Назад", callback_data="back")]
    ])

    await callback.message.edit_text("Выберите тариф:", reply_markup=kb)

# ===== ОПЛАТА =====
@dp.callback_query(F.data.startswith("buy_"))
async def buy(callback: types.CallbackQuery):
    months = int(callback.data.split("_")[1])

    prices = {1: 1.1, 3: 3.3, 12: 6.6}
    price = prices[months]

    url = f"https://t.me/CryptoBot?start=invoice_{price}"

    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Оплатить", url=url)],
        [InlineKeyboardButton(text="Проверить оплату", callback_data=f"check_{months}")],
        [InlineKeyboardButton(text="Назад", callback_data="tariffs")]
    ])

    await callback.message.edit_text(
        f"Оплата тарифа на {months} мес.\nСумма: {price}$",
        reply_markup=kb
    )

# ===== ПРОВЕРКА (заглушка) =====
@dp.callback_query(F.data.startswith("check_"))
async def check(callback: types.CallbackQuery):
    await callback.answer("Оплата не найдена", show_alert=True)

# ===== СКАЧАТЬ VPN =====
@dp.callback_query(F.data == "download")
async def download(callback: types.CallbackQuery):
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Для ПК", url="https://google.com")],
        [InlineKeyboardButton(text="Для Android", url="https://google.com")],
        [InlineKeyboardButton(text="Назад", callback_data="back")]
    ])

    await callback.message.edit_text("Скачать VPN:", reply_markup=kb)

# ===== ПОДДЕРЖКА =====
user_support = {}

@dp.callback_query(F.data == "support")
async def support(callback: types.CallbackQuery):
    user_support[callback.from_user.id] = True
    await callback.message.edit_text("Напишите сообщение в поддержку:")

@dp.message()
async def handle_messages(message: types.Message):
    user_id = message.from_user.id

    if user_id in user_support:
        for admin in ADMINS:
            await bot.send_message(admin, f"Обращение от {user_id}:\n{message.text}")
        await message.answer("Сообщение отправлено в поддержку")
        user_support.pop(user_id)

# ===== АДМИНКА =====
@dp.callback_query(F.data == "admin")
async def admin(callback: types.CallbackQuery):
    if callback.from_user.id not in ADMINS:
        return

    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Список пользователей", callback_data="users")],
        [InlineKeyboardButton(text="Назад", callback_data="back")]
    ])

    await callback.message.edit_text("Админ панель:", reply_markup=kb)

@dp.callback_query(F.data == "users")
async def users(callback: types.CallbackQuery):
    cursor.execute("SELECT user_id FROM users")
    users = cursor.fetchall()

    text = "Список пользователей:\n\n"
    for u in users:
        text += f"{u[0]}\n"

    await callback.message.edit_text(text)

# ===== НАЗАД =====
@dp.callback_query(F.data == "back")
async def back(callback: types.CallbackQuery):
    await callback.message.edit_text(
        "Главное меню:",
        reply_markup=main_menu(callback.from_user.id)
    )

# ===== ЗАПУСК =====
async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
