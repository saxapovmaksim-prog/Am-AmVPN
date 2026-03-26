import asyncio
import time
from aiogram import Bot, Dispatcher, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command
from aiogram.exceptions import TelegramBadRequest
from yoomoney import Quickpay, Client

# === ВАШИ ДАННЫЕ ===
BOT_TOKEN = "8637803848:AAHTK2zzOOtSUV2tsWJLckGYuNWV6tRCJRE" # Обязательно смените тот, что засветили на скриншоте!
YOOMONEY_TOKEN = "ВАШ_ACCESS_TOKEN_ИЗ_ПЕРВОГО_ШАГА"
RECEIVER_WALLET = "41001XXXXXXXXX" # Номер вашего кошелька ЮMoney (начинается на 4100)

PRICE = 99 # Цена тарифа в рублях

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# Обработка команды /start
@dp.message(Command("start"))
async def send_welcome(message: types.Message):
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🍬 Купить тариф Сладкий (99 ₽)", callback_data="buy_standard")]
    ])
    await message.answer(
        f"Привет, {message.from_user.first_name}! Я бот AmAm VPN 🍬\n\n"
        "Жми кнопку ниже, чтобы купить ключ и съесть все блокировки!",
        reply_markup=keyboard
    )

# Нажатие на кнопку "Купить"
@dp.callback_query(lambda c: c.data == 'buy_standard')
async def process_buy(callback_query: types.CallbackQuery):
    # Создаем уникальную метку для платежа (ID пользователя + время)
    payment_label = f"{callback_query.from_user.id}_{int(time.time())}"
    
    # Генерируем ссылку на оплату
    quickpay = Quickpay(
        receiver=RECEIVER_WALLET,
        quickpay_form="shop",
        targets="Оплата AmAm VPN",
        paymentType="SB", # SB = СБП (Быстрые платежи)
        sum=PRICE,
        label=payment_label
    )
    
    # Кнопка оплаты и проверки
    check_keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Оплатить 99 ₽", url=quickpay.base_url)],
        [InlineKeyboardButton(text="🔄 Я оплатил! (Проверить)", callback_data=f"check_{payment_label}")]
    ])
    
    await callback_query.message.answer(
        "Перейдите по ссылке ниже для оплаты.\nПосле успешного перевода нажмите кнопку 'Я оплатил!'",
        reply_markup=check_keyboard
    )
    await callback_query.answer()

# Проверка оплаты
@dp.callback_query(lambda c: c.data.startswith('check_'))
async def check_payment(callback_query: types.CallbackQuery):
    label = callback_query.data.split('_', 1)[1]
    
    # Идем в ЮMoney и ищем операцию по уникальной метке
    client = Client(YOOMONEY_TOKEN)
    history = client.operation_history(label=label)
    
    if history.operations:
        # ПЛАТЕЖ НАЙДЕН!
        try:
            await callback_query.message.edit_text(
                "✅ Оплата прошла успешно!\n\n"
                "🎉 Ваш ключ доступа:\n`AMAM-PRO-99X-TEST`\n\n"
                "Скачайте наш APK ниже и вставьте этот ключ в разделе Профиль."
            )
        except TelegramBadRequest:
            # Игнорируем ошибку (пользователь жмет кнопку, когда текст уже изменен)
            pass
            
        await callback_query.answer() # Убираем "часики" загрузки
    else:
        # ПЛАТЕЖ НЕ НАЙДЕН
        # Показываем всплывающее окошко (Alert), текст сообщения не трогаем
        await callback_query.answer(
            "⏳ Оплата еще не поступила.\nПодождите пару минут и нажмите снова.", 
            show_alert=True
        )

async def main():
    print("Бот AmAm VPN успешно запущен!")
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())
