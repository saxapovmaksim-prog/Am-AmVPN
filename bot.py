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
import random
import string
from datetime import datetime, timedelta

from aiogram import Bot, Dispatcher, types, F
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton, BufferedInputFile
from aiogram.filters import Command
from aiogram.exceptions import TelegramBadRequest
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from yoomoney import Quickpay, Client

# ==========================================
# ВАШИ НАСТРОЙКИ (ВСТАВЬТЕ 3 ТОКЕНА)
# ==========================================
BOT_TOKEN = "8637803848:AAHTK2zzOOtSUV2tsWJLckGYuNWV6tRCJRE" 
YOOMONEY_TOKEN = "4100119421936909.5708C060A9413FE2D03525B0F3C2FFD2780FF9A7B979527712BB947C16BEE28B2728CF9A6B66BC8FF64D030553F5C8BF8310097F3919ED9EF1B53F022E427E95DFC03B407B1F6A7EC8F778E0864DAA392E7D0F9C5DD43C7B1A4EB78EC63D61A8FA21ED6ECA5689326A9FD99951C97F10D998D5F2AA6099DC16E2B87142300ACC"
RECEIVER_WALLET = "41001XXXXXXXXX" 
ADMIN_ID = 2032012311 # Ваш ID
# ==========================================

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# --- СОСТОЯНИЯ (FSM) ДЛЯ АДМИНА ---
class AdminState(StatesGroup):
    waiting_for_custom_key = State()

# --- БАЗА ДАННЫХ (SQLite) ---
def init_db():
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()
    # Таблица пользователей
    cursor.execute('''CREATE TABLE IF NOT EXISTS users 
                      (id INTEGER PRIMARY KEY, tariff TEXT, key TEXT, expire_date TEXT)''')
    # Новая таблица для хранения свободных ключей
    cursor.execute('''CREATE TABLE IF NOT EXISTS vpn_keys 
                      (id INTEGER PRIMARY KEY, key_value TEXT UNIQUE, is_used INTEGER DEFAULT 0)''')
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

# --- МЕНЮ БОТА ---
def get_main_menu(user_id):
    kb = [
        [KeyboardButton(text="👤 Мой профиль"), KeyboardButton(text="🛒 Тарифы")],
        [KeyboardButton(text="🚀 Скачать VPN"), KeyboardButton(text="💬 Поддержка")]
    ]
    if user_id == ADMIN_ID: kb.append([KeyboardButton(text="👑 Админ-панель")])
    return ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)

tariffs_menu = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="🍬 Сладкий (99 ₽ / 30 дней)", callback_data="buy_99")],
    [InlineKeyboardButton(text="👑 PRO (299 ₽ / 30 дней)", callback_data="buy_299")]
])

# Inline-меню для Админ-панели
admin_menu = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="🎲 Сгенерировать 100 ключей", callback_data="admin_gen_100")],
    [InlineKeyboardButton(text="✍️ Создать свой ключ", callback_data="admin_create_custom")]
])


# --- КОМАНДЫ ---
@dp.message(Command("start"))
async def cmd_start(message: types.Message, state: FSMContext):
    await state.clear() # Сбрасываем состояния на всякий случай
    user_id = message.from_user.id
    if not get_user(user_id):
        update_user(user_id, "Бесплатный", "Нет ключа. Купите тариф.", 0)
    
    await message.answer(
        f"Привет, {message.from_user.first_name}!\nДобро пожаловать в **AmAm VPN** 🍬\n\nВыберите действие ниже 👇", 
        reply_markup=get_main_menu(user_id)
    )

# --- АДМИН-ПАНЕЛЬ ---
@dp.message(F.text == "👑 Админ-панель")
async def admin_panel_button(message: types.Message):
    if message.from_user.id != ADMIN_ID: return
    
    conn = sqlite3.connect("database.db")
    users_count = conn.cursor().execute("SELECT COUNT(*) FROM users").fetchone()[0]
    keys_count = conn.cursor().execute("SELECT COUNT(*) FROM vpn_keys WHERE is_used=0").fetchone()[0]
    conn.close()
    
    await message.answer(
        f"👑 **АДМИН-ПАНЕЛЬ**\n\n"
        f"👥 Пользователей: **{users_count}**\n"
        f"🔑 Свободных ключей в базе: **{keys_count}**\n\n"
        f"Выберите действие:", 
        reply_markup=admin_menu,
        parse_mode="Markdown"
    )

# Обработка кнопки "Сгенерировать 100 ключей"
@dp.callback_query(F.data == "admin_gen_100")
async def admin_gen_100(callback: types.CallbackQuery):
    if callback.from_user.id != ADMIN_ID: return
    
    # Генерируем 100 случайных ключей (длина 12, буквы и цифры)
    new_keys = []
    for _ in range(100):
        # Случайный ключ из 12 символов (Заглавные буквы + Цифры)
        key = ''.join(random.choices(string.ascii_uppercase + string.digits, k=12))
        new_keys.append(key)
        
    # Сохраняем в базу данных
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()
    for k in new_keys:
        try: cursor.execute("INSERT INTO vpn_keys (key_value) VALUES (?)", (k,))
        except sqlite3.IntegrityError: pass # Игнорируем дубликаты, если вдруг совпадут
    conn.commit()
    conn.close()
    
    # Собираем ключи в текстовый файл, чтобы отправить админу
    keys_text = "\n".join(new_keys)
    file = BufferedInputFile(keys_text.encode('utf-8'), filename="generated_100_keys.txt")
    
    await callback.message.answer_document(
        document=file,
        caption="✅ 100 ключей успешно сгенерированы и добавлены в базу данных!"
    )
    await callback.answer()

# Обработка кнопки "Создать свой ключ"
@dp.callback_query(F.data == "admin_create_custom")
async def admin_create_custom(callback: types.CallbackQuery, state: FSMContext):
    if callback.from_user.id != ADMIN_ID: return
    
    await callback.message.answer("✍️ Отправьте мне текст ключа.\nРекомендуемый формат: 12 символов (латинские буквы и цифры).")
    # Переводим бота в режим ожидания текста ключа
    await state.set_state(AdminState.waiting_for_custom_key)
    await callback.answer()

# Принимаем текст ключа от админа
@dp.message(AdminState.waiting_for_custom_key)
async def save_custom_key(message: types.Message, state: FSMContext):
    custom_key = message.text.strip().upper() # Убираем пробелы и делаем заглавными
    
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO vpn_keys (key_value) VALUES (?)", (custom_key,))
        conn.commit()
        await message.answer(f"✅ Ваш личный ключ `{custom_key}` успешно сохранен в базу!", parse_mode="Markdown")
    except sqlite3.IntegrityError:
        await message.answer("⚠️ Ошибка: Такой ключ уже существует в базе!")
    finally:
        conn.close()
        
    # Выходим из режима ожидания
    await state.clear()


# --- ПОЛЬЗОВАТЕЛЬСКОЕ МЕНЮ ---
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
        
        # Берем случайный ключ из нашей базы сгенерированных!
        conn = sqlite3.connect("database.db")
        cursor = conn.cursor()
        free_key_row = cursor.execute("SELECT key_value FROM vpn_keys WHERE is_used=0 LIMIT 1").fetchone()
        
        if free_key_row:
            new_key = free_key_row[0]
            cursor.execute("UPDATE vpn_keys SET is_used=1 WHERE key_value=?", (new_key,))
            conn.commit()
        else:
            # Если ключи в базе закончились (Вы забыли нажать сгенерировать)
            new_key = f"AMAM-VPN-{price}-{int(time.time())}"
        conn.close()

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
