# --- АВТО-УСТАНОВЩИК БИБЛИОТЕК ---
import sys, subprocess
def install(package): subprocess.check_call([sys.executable, "-m", "pip", "install", package])
try: import aiogram
except ImportError: install("aiogram")
try: import yoomoney
except ImportError: install("yoomoney")

import asyncio
import time
import sqlite3
from datetime import datetime, timedelta
from aiogram import Bot, Dispatcher, types, F
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command
from aiogram.exceptions import TelegramBadRequest
from yoomoney import Quickpay, Client

# ==========================================
# ВАШИ НАСТРОЙКИ (ЗАПОЛНИТЕ 4 СТРОЧКИ!)
# ==========================================
BOT_TOKEN = "ВАШ_ТОКЕН_БОТА" 
YOOMONEY_TOKEN = "ВАШ_ТОКЕН_ЮМАНИ"
RECEIVER_WALLET = "41001XXXXXXXXX" # Номер кошелька ЮMoney
ADMIN_ID = 123456789 # ВАШ ТЕЛЕГРАМ ID (узнать в @getmyid_bot)
# ==========================================

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# --- БАЗА ДАННЫХ (SQLite) ---
def init_db():
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS users 
                      (id INTEGER PRIMARY KEY, tariff TEXT, key TEXT, expire_date TEXT)''')
    conn.commit()
    conn.close()

def get_user(user_id):
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()
    cursor.execute("SELECT tariff, key, expire_date FROM users WHERE id=?", (user_id,))
    res = cursor.fetchone()
    conn.close()
    return res

def update_user(user_id, tariff, key, days):
    expire_date = (datetime.now() + timedelta(days=days)).strftime("%Y-%m-%d %H:%M")
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()
    cursor.execute("INSERT OR REPLACE INTO users (id, tariff, key, expire_date) VALUES (?, ?, ?, ?)", 
                   (user_id, tariff, key, expire_date))
    conn.commit()
    conn.close()

# Инициализируем БД при старте
init_db()

# --- МЕНЮ БОТА ---
main_menu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="👤 Мой профиль"), KeyboardButton(text="🛒 Тарифы")],
        [KeyboardButton(text="🚀 Скачать VPN"), KeyboardButton(text="💬 Поддержка")]
    ], resize_keyboard=True
)

tariffs_menu = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="🍬 Сладкий (99 ₽ / 30 дней)", callback_data="buy_99")],
    [InlineKeyboardButton(text="👑 PRO (299 ₽ / 30 дней)", callback_data="buy_299")]
])

# --- КОМАНДЫ ---
@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    user_id = message.from_user.id
    if not get_user(user_id):
        update_user(user_id, "Бесплатный", "Нет ключа. Купите тариф.", 0)
    await message.answer(f"Привет, {message.from_user.first_name}!\nДобро пожаловать в **AmAm VPN** 🍬\n\nВыберите действие ниже 👇", reply_markup=main_menu)

@dp.message(Command("admin"))
async def cmd_admin(message: types.Message):
    if message.from_user.id != ADMIN_ID: return
    conn = sqlite3.connect("database.db")
    count = conn.cursor().execute("SELECT COUNT(*) FROM users").fetchone()[0]
    conn.close()
    await message.answer(f"👑 **АДМИН-ПАНЕЛЬ**\n\n👥 Всего пользователей в БД: {count}\n\n*(Позже мы добавим сюда рассылку и выдачу бесплатных ключей)*", parse_mode="Markdown")

# --- КНОПКИ НИЖНЕГО МЕНЮ ---
@dp.message(F.text == "👤 Мой профиль")
async def show_profile(message: types.Message):
    user = get_user(message.from_user.id)
    if not user: return await message.answer("Нажмите /start")
    tariff, key, expire_date = user
    text = f"👤 **Ваш Профиль:**\n\n💎 **Тариф:** {tariff}\n⏳ **Активен до:** {expire_date if tariff != 'Бесплатный' else '∞'}\n\n🔐 **Ваш ключ:**\n`{key}`"
    await message.answer(text, parse_mode="Markdown")

@dp.message(F.text == "🛒 Тарифы")
async def show_tariffs(message: types.Message):
    await message.answer("⚡️ **Выберите тариф:**", reply_markup=tariffs_menu)

@dp.message(F.text == "🚀 Скачать VPN")
async def send_app(message: types.Message):
    await message.answer("Скачайте приложение: [Скоро здесь будет APK]")

@dp.message(F.text == "💬 Поддержка")
async def send_support(message: types.Message):
    await message.answer("Поддержка: @ВашЛогин")

# --- ОПЛАТА ---
@dp.callback_query(F.data.startswith('buy_'))
async def process_buy(callback_query: types.CallbackQuery):
    price = int(callback_query.data.split('_')[1])
    payment_label = f"{callback_query.from_user.id}_{price}_{int(time.time())}"
    quickpay = Quickpay(receiver=RECEIVER_WALLET, quickpay_form="shop", targets="Оплата VPN", paymentType="SB", sum=price, label=payment_label)
    
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Оплатить", url=quickpay.base_url)],
        [InlineKeyboardButton(text="🔄 Я оплатил!", callback_data=f"check_{payment_label}")]
    ])
    await callback_query.message.edit_text(f"Оплата тарифа: {price} ₽", reply_markup=kb)

@dp.callback_query(F.data.startswith('check_'))
async def check_payment(callback_query: types.CallbackQuery):
    _, user_id, price, _ = callback_query.data.split('_')
    label = callback_query.data.replace("check_", "")
    
    client = Client(YOOMONEY_TOKEN)
    history = client.operation_history(label=label)
    
    if history.operations:
        tariff_name = "Сладкий 🍬" if int(price) == 99 else "PRO 👑"
        new_key = f"AMAM-VPN-{price}-{int(time.time())}" # Пока фейковый ключ
        update_user(int(user_id), tariff_name, new_key, 30) # Выдаем на 30 дней
        
        try:
            await callback_query.message.edit_text(f"✅ Успешно!\nТариф: {tariff_name}\nКлюч:\n`{new_key}`", parse_mode="Markdown")
        except TelegramBadRequest: pass
        await callback_query.answer()
    else:
        await callback_query.answer("⏳ Оплата еще не поступила. Подождите.", show_alert=True)

# --- ЗАПУСК БОТА ---
async def main():
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())
