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
# ВАШИ НАСТРОЙКИ (ВСТАВЬТЕ 3 ТОКЕНА)
# ==========================================
BOT_TOKEN = "8637803848:AAHTK2zzOOtSUV2tsWJLckGYuNWV6tRCJRE" 
YOOMONEY_TOKEN = "4100119421936909.5708C060A9413FE2D03525B0F3C2FFD2780FF9A7B979527712BB947C16BEE28B2728CF9A6B66BC8FF64D030553F5C8BF8310097F3919ED9EF1B53F022E427E95DFC03B407B1F6A7EC8F778E0864DAA392E7D0F9C5DD43C7B1A4EB78EC63D61A8FA21ED6ECA5689326A9FD99951C97F10D998D5F2AA6099DC16E2B87142300ACC"
RECEIVER_WALLET = "41001XXXXXXXXX" 
ADMIN_ID = 2032012311 # ВАШ ID (уже вписан!)
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

init_db()

# --- ДИНАМИЧЕСКОЕ МЕНЮ (С КНОПКОЙ АДМИНА) ---
def get_main_menu(user_id):
    # Стандартные кнопки для всех
    kb = [
        [KeyboardButton(text="👤 Мой профиль"), KeyboardButton(text="🛒 Тарифы")],
        [KeyboardButton(text="🚀 Скачать VPN"), KeyboardButton(text="💬 Поддержка")]
    ]
    # Если это ВЫ, добавляем секретную кнопку
    if user_id == ADMIN_ID:
        kb.append([KeyboardButton(text="👑 Админ-панель")])
    
    return ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)

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
    
    # Бот выдает меню в зависимости от того, админ это или нет
    await message.answer(
        f"Привет, {message.from_user.first_name}!\nДобро пожаловать в **AmAm VPN** 🍬\n\nВыберите действие ниже 👇", 
        reply_markup=get_main_menu(user_id)
    )

# --- КНОПКИ НИЖНЕГО МЕНЮ ---
@dp.message(F.text == "👑 Админ-панель")
async def admin_panel_button(message: types.Message):
    if message.from_user.id != ADMIN_ID: 
        return # Если кто-то чужой как-то нажмет кнопку, бот проигнорирует
    
    conn = sqlite3.connect("database.db")
    count = conn.cursor().execute("SELECT COUNT(*) FROM users").fetchone()[0]
    conn.close()
    
    await message.answer(
        f"👑 **СЕКРЕТНАЯ АДМИН-ПАНЕЛЬ**\n\n"
        f"👥 Всего пользователей в базе: **{count}**\n"
        f"💰 Оплаты работают штатно.\n\n"
        f"*(Скоро мы добавим сюда рассылку и выдачу тестовых ключей)*", 
        parse_mode="Markdown"
    )

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
        new_key = f"AMAM-VPN-{price}-{int(time.time())}"
        update_user(int(user_id), tariff_name, new_key, 30)
        
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
