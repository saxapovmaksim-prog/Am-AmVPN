import asyncio
import time
from aiogram import Bot, Dispatcher, types, F
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command
from aiogram.exceptions import TelegramBadRequest
from yoomoney import Quickpay, Client

# === ВАШИ ДАННЫЕ ===
BOT_TOKEN = "8637803848:AAHTK2zzOOtSUV2tsWJLckGYuNWV6tRCJRE" # Вставьте токен от AmAm VPN!
YOOMONEY_TOKEN = "4100119421936909.5708C060A9413FE2D03525B0F3C2FFD2780FF9A7B979527712BB947C16BEE28B2728CF9A6B66BC8FF64D030553F5C8BF8310097F3919ED9EF1B53F022E427E95DFC03B407B1F6A7EC8F778E0864DAA392E7D0F9C5DD43C7B1A4EB78EC63D61A8FA21ED6ECA5689326A9FD99951C97F10D998D5F2AA6099DC16E2B87142300ACC"
RECEIVER_WALLET = "41001XXXXXXXXX"

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# Временная "база данных" в памяти (для теста)
# В реальности тут будет подключение к SQLite или PostgreSQL
users_db = {}

# --- КЛАВИАТУРЫ ---
# Нижнее меню (Reply)
main_menu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="👤 Мой профиль"), KeyboardButton(text="🛒 Тарифы")],
        [KeyboardButton(text="🚀 Скачать приложение (APK)")],
        [KeyboardButton(text="💬 Поддержка")]
    ],
    resize_keyboard=True
)

# Меню тарифов (Inline)
tariffs_menu = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="Сладкий (99 ₽ / мес)", callback_data="buy_99")],
        [InlineKeyboardButton(text="Сахарная кома PRO (299 ₽ / мес)", callback_data="buy_299")]
    ]
)

# --- ОБРАБОТЧИКИ СООБЩЕНИЙ ---

@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    user_id = message.from_user.id
    # Регистрируем пользователя, если его нет
    if user_id not in users_db:
        users_db[user_id] = {
            "tariff": "Голодный (Бесплатный)",
            "key": "Нет ключа. Нажмите 'Тарифы', чтобы купить."
        }
        
    await message.answer(
        f"🍬 Добро пожаловать в **AmAm VPN**, {message.from_user.first_name}!\n\n"
        "Мы съедаем все блокировки. Выберите нужное действие в меню ниже 👇",
        reply_markup=main_menu,
        parse_mode="Markdown"
    )

# Обработка кнопок нижнего меню
@dp.message(F.text == "👤 Мой профиль")
async def show_profile(message: types.Message):
    user_id = message.from_user.id
    user_data = users_db.get(user_id, {"tariff": "Голодный (Бесплатный)", "key": "Нет ключа"})
    
    text = (
        "👤 **Ваш профиль:**\n\n"
        f"🔑 **ID:** `{user_id}`\n"
        f"💎 **Тариф:** {user_data['tariff']}\n\n"
        f"🔐 **Ваш ключ доступа:**\n`{user_data['key']}`\n\n"
        "*(Нажмите на ключ, чтобы скопировать)*"
    )
    await message.answer(text, parse_mode="Markdown")

@dp.message(F.text == "🛒 Тарифы")
async def show_tariffs(message: types.Message):
    await message.answer(
        "⚡️ **Выберите тариф:**\n\n"
        "**1. Сладкий (99 ₽)**\n"
        "• Отличная скорость\n• До 5 устройств\n\n"
        "**2. Сахарная кома PRO (299 ₽)**\n"
        "• Максимальная скорость\n• До 10 устройств",
        reply_markup=tariffs_menu,
        parse_mode="Markdown"
    )

@dp.message(F.text == "🚀 Скачать приложение (APK)")
async def send_app(message: types.Message):
    await message.answer(
        "🤖 **Приложение AmAm VPN для Android:**\n\n"
        "*(Здесь бот будет отправлять .apk файл, когда мы его соберем)*\n\n"
        "Инструкция:\n1. Установите приложение.\n2. Перейдите в раздел 'Профиль'.\n3. Вставьте ваш ключ доступа.",
        parse_mode="Markdown"
    )

@dp.message(F.text == "💬 Поддержка")
async def send_support(message: types.Message):
    await message.answer("Если у вас возникли проблемы, напишите нашему менеджеру: @ВашЮзернейм")

# --- ЛОГИКА ОПЛАТЫ ---

@dp.callback_query(F.data.startswith('buy_'))
async def process_buy(callback_query: types.CallbackQuery):
    price = int(callback_query.data.split('_')[1])
    tariff_name = "Сладкий" if price == 99 else "Сахарная кома PRO"
    
    payment_label = f"{callback_query.from_user.id}_{price}_{int(time.time())}"
    
    quickpay = Quickpay(
        receiver=RECEIVER_WALLET,
        quickpay_form="shop",
        targets=f"Оплата тарифа {tariff_name}",
        paymentType="SB", 
        sum=price,
        label=payment_label
    )
    
    check_keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=f"Оплатить {price} ₽", url=quickpay.base_url)],
        [InlineKeyboardButton(text="🔄 Я оплатил! (Проверить)", callback_data=f"check_{payment_label}")]
    ])
    
    await callback_query.message.edit_text(
        f"🛒 Оплата тарифа **{tariff_name}** ({price} ₽)\n\n"
        "Перейдите по ссылке ниже для оплаты. После перевода нажмите кнопку 'Я оплатил!'",
        reply_markup=check_keyboard,
        parse_mode="Markdown"
    )

@dp.callback_query(F.data.startswith('check_'))
async def check_payment(callback_query: types.CallbackQuery):
    # Разбираем метку: check_ID_PRICE_TIME
    data_parts = callback_query.data.split('_')
    label = f"{data_parts[1]}_{data_parts[2]}_{data_parts[3]}"
    user_id = int(data_parts[1])
    price = int(data_parts[2])
    
    client = Client(YOOMONEY_TOKEN)
    history = client.operation_history(label=label)
    
    if history.operations:
        # Успешная оплата! Обновляем базу данных пользователя
        tariff_name = "Сладкий 🍬" if price == 99 else "Сахарная кома PRO 👑"
        new_key = f"AMAM-{price}X-{'PRO' if price == 299 else 'STD'}-88A2"
        
        users_db[user_id] = {
            "tariff": tariff_name,
            "key": new_key
        }
        
        try:
            await callback_query.message.edit_text(
                "✅ **Оплата прошла успешно!**\n\n"
                f"Ваш тариф изменен на: **{tariff_name}**\n\n"
                f"🔐 Ваш новый ключ доступа:\n`{new_key}`\n\n"
                "*(Нажмите на ключ, чтобы скопировать)*",
                parse_mode="Markdown"
            )
        except TelegramBadRequest:
            pass
        await callback_query.answer()
    else:
        await callback_query.answer("⏳ Оплата еще не поступила.\nПодождите минуту и нажмите снова.", show_alert=True)

async def main():
    print("VPN Бот запущен! Жду сообщений...")
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())
