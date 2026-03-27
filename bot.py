# --- АВТО-УСТАНОВЩИК БИБЛИОТЕК (ЧТОБЫ НЕ БЫЛО ОШИБОК) ---
import sys
import subprocess

def install(package):
    subprocess.check_call([sys.executable, "-m", "pip", "install", package])

try:
    import aiogram
except ImportError:
    print("Устанавливаем aiogram...")
    install("aiogram")

try:
    import yoomoney
except ImportError:
    print("Устанавливаем yoomoney...")
    install("yoomoney")
# --------------------------------------------------------

import asyncio
import time
from aiogram import Bot, Dispatcher, types, F
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command
from aiogram.exceptions import TelegramBadRequest
from yoomoney import Quickpay, Client

# ==========================================
# ВАШИ НАСТРОЙКИ (ЗАПОЛНИТЕ ЭТИ 3 СТРОЧКИ!)
# ==========================================
BOT_TOKEN = "8637803848:AAHTK2zzOOtSUV2tsWJLckGYuNWV6tRCJRE" 
YOOMONEY_TOKEN = "4100119421936909.5708C060A9413FE2D03525B0F3C2FFD2780FF9A7B979527712BB947C16BEE28B2728CF9A6B66BC8FF64D030553F5C8BF8310097F3919ED9EF1B53F022E427E95DFC03B407B1F6A7EC8F778E0864DAA392E7D0F9C5DD43C7B1A4EB78EC63D61A8FA21ED6ECA5689326A9FD99951C97F10D998D5F2AA6099DC16E2B87142300ACC"
RECEIVER_WALLET = "41001XXXXXXXXX" # Номер кошелька ЮMoney (4100...)
# ==========================================

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()
users_db = {} # Временная база данных пользователей

# --- МЕНЮ БОТА ---
main_menu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="👤 Мой профиль"), KeyboardButton(text="🛒 Тарифы")],
        [KeyboardButton(text="🚀 Скачать VPN"), KeyboardButton(text="💬 Поддержка")]
    ],
    resize_keyboard=True
)

tariffs_menu = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="🍬 Сладкий (99 ₽)", callback_data="buy_99")],
        [InlineKeyboardButton(text="👑 Сахарная кома PRO (299 ₽)", callback_data="buy_299")]
    ]
)

# --- КОМАНДА /start ---
@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    user_id = message.from_user.id
    if user_id not in users_db:
        users_db[user_id] = {"tariff": "Бесплатный", "key": "Нет ключа. Купите тариф."}
        
    await message.answer(
        f"Привет, {message.from_user.first_name}!\nДобро пожаловать в **AmAm VPN** 🍬\n\nВыберите действие в меню ниже 👇",
        reply_markup=main_menu
    )

# --- КНОПКИ НИЖНЕГО МЕНЮ ---
@dp.message(F.text == "👤 Мой профиль")
async def show_profile(message: types.Message):
    user_data = users_db.get(message.from_user.id, {"tariff": "Бесплатный", "key": "Нет ключа"})
    text = f"👤 **Профиль:**\n\n💎 **Тариф:** {user_data['tariff']}\n🔐 **Ключ:** `{user_data['key']}`"
    await message.answer(text, parse_mode="Markdown")

@dp.message(F.text == "🛒 Тарифы")
async def show_tariffs(message: types.Message):
    await message.answer("⚡️ **Выберите тариф:**\n\n1. Сладкий (99₽) - до 5 устройств\n2. PRO (299₽) - до 10 устройств", reply_markup=tariffs_menu)

@dp.message(F.text == "🚀 Скачать VPN")
async def send_app(message: types.Message):
    await message.answer("Скачайте приложение по ссылке: [Скоро здесь будет APK]")

@dp.message(F.text == "💬 Поддержка")
async def send_support(message: types.Message):
    await message.answer("Поддержка: @ВашЛогин")

# --- ОПЛАТА ---
@dp.callback_query(F.data.startswith('buy_'))
async def process_buy(callback_query: types.CallbackQuery):
    price = int(callback_query.data.split('_')[1])
    payment_label = f"{callback_query.from_user.id}_{price}_{int(time.time())}"
    
    # Создаем ссылку на оплату
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
    
    if history.operations: # Если оплата найдена
        tariff_name = "Сладкий 🍬" if int(price) == 99 else "PRO 👑"
        new_key = f"AMAM-VPN-{price}-{int(time.time())}" # Генерируем уникальный ключ
        users_db[int(user_id)] = {"tariff": tariff_name, "key": new_key} # Сохраняем
        
        try:
            await callback_query.message.edit_text(f"✅ Успешно!\n\nТариф: {tariff_name}\nВаш ключ:\n`{new_key}`", parse_mode="Markdown")
        except TelegramBadRequest:
            pass
        await callback_query.answer()
    else:
        await callback_query.answer("⏳ Оплата еще не поступила. Подождите.", show_alert=True)

# --- ЗАПУСК БОТА ---
async def main():
    await bot.delete_webhook(drop_pending_updates=True) # Очищаем старые сообщения
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())
