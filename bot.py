import json
import os
from datetime import datetime, timedelta
from aiogram import Bot, Dispatcher, types, F
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

# ===== НАСТРОЙКИ =====
BOT_TOKEN = "ВСТАВЬ_СЮДА_ТОКЕН"
ADMIN_ID = 123456789  # твой ID
DB_FILE = "users.json"

bot = Bot(BOT_TOKEN)
dp = Dispatcher()

# ===== БАЗА =====
def load_db():
    if not os.path.exists(DB_FILE):
        return {}
    with open(DB_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_db(db):
    with open(DB_FILE, "w", encoding="utf-8") as f:
        json.dump(db, f, indent=2)

# ===== КНОПКИ =====
def main_menu():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="👤 Личный кабинет", callback_data="cabinet")],
        [InlineKeyboardButton(text="💳 Выбрать тариф", callback_data="tariffs")],
        [InlineKeyboardButton(text="📥 Скачать VPN", url="https://your-site.com")],
        [InlineKeyboardButton(text="🛠 Поддержка", url="https://t.me/your_support")],
        [InlineKeyboardButton(text="⚙️ Админ панель", callback_data="admin")]
    ])

def tariffs_menu():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="30 дней — 99₽", callback_data="buy_30")],
        [InlineKeyboardButton(text="90 дней — 299₽", callback_data="buy_90")],
        [InlineKeyboardButton(text="365 дней — 600₽", callback_data="buy_365")],
        [InlineKeyboardButton(text="⬅️ Назад", callback_data="back")]
    ])

# ===== START (БЕЗ ФОТО) =====
@dp.message(F.text == "/start")
async def start(msg: types.Message):
    await msg.answer(
        "🚀 Добро пожаловать в AM-AM VPN\n\nГлавное меню:",
        reply_markup=main_menu()
    )

# ===== НАЗАД =====
@dp.callback_query(F.data == "back")
async def back(call: types.CallbackQuery):
    await call.message.edit_text("Главное меню:", reply_markup=main_menu())

# ===== ЛИЧНЫЙ КАБИНЕТ =====
@dp.callback_query(F.data == "cabinet")
async def cabinet(call: types.CallbackQuery):
    db = load_db()
    tg_id = str(call.from_user.id)

    user = None
    user_id = None

    for uid, data in db.items():
        if data.get("telegram_id") == tg_id:
            user = data
            user_id = uid
            break

    if not user:
        await call.message.edit_text(
            "❌ Вы не зарегистрированы\n\nНапишите ваш ID (8 цифр), чтобы привязать аккаунт:"
        )
        dp.message.register(bind_account)
        return

    text = (
        f"👤 Ник: {user.get('nick','-')}\n"
        f"🆔 ID: {user_id}\n"
        f"📅 Регистрация: {user.get('created','-')}\n"
        f"💳 Тариф: {user.get('tariff','free')}\n"
        f"⏳ До: {user.get('expires','нет')}"
    )

    await call.message.edit_text(text, reply_markup=main_menu())

# ===== ПРИВЯЗКА АККАУНТА =====
async def bind_account(msg: types.Message):
    db = load_db()
    uid = msg.text.strip()

    if uid not in db:
        await msg.answer("❌ ID не найден")
        return

    db[uid]["telegram_id"] = str(msg.from_user.id)
    save_db(db)

    await msg.answer("✅ Аккаунт привязан! Напиши /start")

# ===== ТАРИФЫ =====
@dp.callback_query(F.data == "tariffs")
async def tariffs(call: types.CallbackQuery):
    await call.message.edit_text("💳 Выберите тариф:", reply_markup=tariffs_menu())

# ===== ПОКУПКА =====
@dp.callback_query(F.data.startswith("buy_"))
async def buy(call: types.CallbackQuery):
    days = int(call.data.split("_")[1])

    dp["buy_days"] = days

    await call.message.edit_text(
        f"💳 Отправьте ID для активации тарифа ({days} дней):"
    )

    dp.message.register(process_buy)

async def process_buy(msg: types.Message):
    db = load_db()
    uid = msg.text.strip()

    if uid not in db:
        await msg.answer("❌ ID не найден")
        return

    db[uid]["telegram_id"] = str(msg.from_user.id)
    save_db(db)

    await msg.answer("📸 Отправьте скрин оплаты")

    dp["buy_user"] = uid
    dp.message.register(check_payment)

# ===== ПРОВЕРКА ОПЛАТЫ =====
async def check_payment(msg: types.Message):
    if not msg.photo:
        await msg.answer("❌ Отправьте фото")
        return

    user_id = msg.from_user.id

    await bot.send_photo(
        ADMIN_ID,
        msg.photo[-1].file_id,
        caption=f"Проверить оплату от {user_id}",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="✅ Подтвердить", callback_data=f"ok_{user_id}")]
        ])
    )

    await msg.answer("⏳ Ожидайте подтверждения")

# ===== ПОДТВЕРЖДЕНИЕ =====
@dp.callback_query(F.data.startswith("ok_"))
async def confirm(call: types.CallbackQuery):
    user_id = int(call.data.split("_")[1])
    db = load_db()

    for uid, user in db.items():
        if user.get("telegram_id") == str(user_id):
            days = dp.get("buy_days", 30)
            expires = datetime.now() + timedelta(days=days)

            user["tariff"] = "premium"
            user["expires"] = expires.strftime("%Y-%m-%d")

            save_db(db)

            await bot.send_message(user_id, "✅ Оплата подтверждена!")
            break

# ===== АДМИНКА =====
@dp.callback_query(F.data == "admin")
async def admin(call: types.CallbackQuery):
    if call.from_user.id != ADMIN_ID:
        await call.answer("Нет доступа", show_alert=True)
        return

    db = load_db()
    total = len(db)
    premium = sum(1 for u in db.values() if u.get("tariff") == "premium")

    await call.message.edit_text(
        f"📊 Статистика\n\n"
        f"👥 Пользователей: {total}\n"
        f"💎 Premium: {premium}\n"
        f"🆓 Free: {total - premium}",
        reply_markup=main_menu()
    )

# ===== ЗАПУСК =====
if __name__ == "__main__":
    import asyncio
    print("Бот запущен...")
    asyncio.run(dp.start_polling(bot))
