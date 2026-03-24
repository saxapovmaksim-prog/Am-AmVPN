import json
import os
import hashlib
import threading
from datetime import datetime, timedelta

from aiogram import Bot, Dispatcher, types, F
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.enums import ParseMode

from flask import Flask, request, jsonify

# ================= НАСТРОЙКИ =================
BOT_TOKEN = "ТВОЙ_НОВЫЙ_ТОКЕН_СЮДА"
ADMIN_IDS = [123456789]  # вставь свой ID
DB_FILE = "users.json"

# ================= БАЗА =================
def load_db():
    if not os.path.exists(DB_FILE):
        return {}
    with open(DB_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_db(data):
    with open(DB_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# ================= API =================
app_api = Flask(__name__)

@app_api.route("/register", methods=["POST"])
def register():
    data = request.json
    db = load_db()

    user_id = data["id"]

    if user_id in db:
        return jsonify({"success": False, "message": "ID уже существует"})

    db[user_id] = {
        "nick": data["nick"],
        "password": hash_password(data["password"]),
        "telegram_id": None,
        "tariff": "free",
        "expires": None,
        "created": datetime.now().strftime("%Y-%m-%d")
    }

    save_db(db)
    return jsonify({"success": True})

@app_api.route("/login", methods=["POST"])
def login():
    data = request.json
    db = load_db()

    user = db.get(data["id"])
    if not user:
        return jsonify({"success": False})

    if user["password"] != hash_password(data["password"]):
        return jsonify({"success": False})

    return jsonify({"success": True, "user": user})

@app_api.route("/activate", methods=["POST"])
def activate():
    data = request.json
    db = load_db()

    user = db.get(data["id"])
    if not user:
        return jsonify({"success": False})

    days = data["days"]
    expires = datetime.now() + timedelta(days=days)

    user["tariff"] = "premium"
    user["expires"] = expires.strftime("%Y-%m-%d")

    save_db(db)
    return jsonify({"success": True})

# ================= БОТ =================
bot = Bot(BOT_TOKEN)
dp = Dispatcher()

def main_menu():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Личный кабинет", callback_data="cabinet")],
        [InlineKeyboardButton(text="Выбрать тариф", callback_data="tariffs")],
        [InlineKeyboardButton(text="Поддержка", callback_data="support")]
    ])

def tariffs_menu():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="1 месяц — 99₽ (~1$)", callback_data="buy_30")],
        [InlineKeyboardButton(text="3 месяца — 299₽ (~3$)", callback_data="buy_90")],
        [InlineKeyboardButton(text="1 год — 600₽ (~6$)", callback_data="buy_365")],
        [InlineKeyboardButton(text="Назад", callback_data="back")]
    ])

@dp.message(F.text == "/start")
async def start(msg: types.Message):
    await msg.answer("Добро пожаловать в VPN", reply_markup=main_menu())

@dp.callback_query(F.data == "back")
async def back(call: types.CallbackQuery):
    await call.message.edit_text("Главное меню", reply_markup=main_menu())

@dp.callback_query(F.data == "cabinet")
async def cabinet(call: types.CallbackQuery):
    db = load_db()

    user = None
    for uid, u in db.items():
        if u["telegram_id"] == call.from_user.id:
            user = (uid, u)
            break

    if not user:
        await call.message.edit_text("Вы не привязали аккаунт")
        return

    uid, u = user

    text = (
        f"ID: {uid}\n"
        f"Ник: {u['nick']}\n"
        f"Тариф: {u['tariff']}\n"
        f"До: {u['expires']}\n"
        f"Регистрация: {u['created']}"
    )

    await call.message.edit_text(text, reply_markup=main_menu())

@dp.callback_query(F.data == "tariffs")
async def tariffs(call: types.CallbackQuery):
    await call.message.edit_text("Выберите тариф", reply_markup=tariffs_menu())

@dp.callback_query(F.data.startswith("buy_"))
async def buy(call: types.CallbackQuery):
    days = int(call.data.split("_")[1])

    await call.message.edit_text(
        "Отправьте ID аккаунта для активации тарифа"
    )

    dp.message.register(wait_id, F.text)
    dp["buy_days"] = days

async def wait_id(msg: types.Message):
    db = load_db()
    user = db.get(msg.text)

    if not user:
        await msg.answer("ID не найден")
        return

    user["telegram_id"] = msg.from_user.id
    save_db(db)

    await msg.answer("Отправьте скрин оплаты")

    dp.message.register(wait_check)

async def wait_check(msg: types.Message):
    for admin in ADMIN_IDS:
        await bot.send_photo(
            admin,
            msg.photo[-1].file_id,
            caption=f"Проверить оплату от {msg.from_user.id}",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="Подтвердить", callback_data=f"ok_{msg.from_user.id}")]
            ])
        )

    await msg.answer("Ожидайте подтверждения")

@dp.callback_query(F.data.startswith("ok_"))
async def confirm(call: types.CallbackQuery):
    user_id = int(call.data.split("_")[1])
    db = load_db()

    for uid, u in db.items():
        if u["telegram_id"] == user_id:
            expires = datetime.now() + timedelta(days=30)
            u["tariff"] = "premium"
            u["expires"] = expires.strftime("%Y-%m-%d")
            save_db(db)

            await bot.send_message(user_id, "Оплата подтверждена! Тариф активирован")
            break

# ================= ЗАПУСК =================
def run_bot():
    import asyncio
    asyncio.run(dp.start_polling(bot))

def run_api():
    app_api.run(port=8000)

if __name__ == "__main__":
    threading.Thread(target=run_bot).start()
    run_api()
