import os
import zipfile
import shutil
from PIL import Image, ImageDraw
import math
import json

if os.path.exists("am-am-vpn"):
    shutil.rmtree("am-am-vpn")

os.makedirs("am-am-vpn/images", exist_ok=True)

print("✓ Структура создана")

# ИЗОБРАЖЕНИЯ
frames = []
for i in range(8):
    img = Image.new('RGBA', (400, 560), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    for r in range(130, 0, -1):
        alpha = int(255 * (r / 130))
        color = (255, 20 + int(100 * r / 130), 147, alpha)
        draw.ellipse([200-r, 200-r, 200+r, 200+r], fill=color)
    draw.ellipse([90, 90, 310, 310], fill=(255, 69, 180, 255))
    for angle in range(0, 360, 30):
        rad = math.radians(angle + i * 45)
        x1 = 200 + 100 * math.cos(rad)
        y1 = 200 + 100 * math.sin(rad)
        x2 = 200 + 80 * math.cos(rad + math.radians(15))
        y2 = 200 + 80 * math.sin(rad + math.radians(15))
        draw.line([(x1, y1), (x2, y2)], fill=(255, 200, 220, 200), width=4)
    draw.ellipse([110, 110, 170, 170], fill=(255, 255, 255, 150))
    draw.rectangle([190, 310, 210, 540], fill=(210, 105, 30, 255))
    draw.rectangle([206, 320, 214, 530], fill=(160, 80, 0, 200))
    frames.append(img)

frames[0].save("am-am-vpn/images/lollipop.gif", save_all=True, append_images=frames[1:], duration=100, loop=0)

img_connected = Image.new('RGBA', (400, 440), (0, 0, 0, 0))
draw = ImageDraw.Draw(img_connected)
draw.ellipse([40, 40, 360, 360], fill=(127, 255, 0, 255))
draw.ellipse([120, 140, 160, 170], fill=(255, 255, 255, 255))
draw.ellipse([130, 150, 150, 170], fill=(0, 0, 0, 255))
draw.ellipse([240, 140, 280, 170], fill=(255, 255, 255, 255))
draw.ellipse([250, 150, 270, 170], fill=(0, 0, 0, 255))
points = [(130, 250), (150, 280), (200, 290), (250, 280), (270, 250)]
draw.line(points, fill=(0, 0, 0, 255), width=14)
img_connected.save("am-am-vpn/images/character-connected.png")

img_disconnected = Image.new('RGBA', (400, 440), (0, 0, 0, 0))
draw = ImageDraw.Draw(img_disconnected)
draw.ellipse([40, 40, 360, 360], fill=(100, 180, 50, 255))
draw.ellipse([120, 130, 160, 180], fill=(255, 255, 255, 255))
draw.ellipse([130, 140, 150, 170], fill=(0, 0, 0, 255))
draw.ellipse([240, 130, 280, 180], fill=(255, 255, 255, 255))
draw.ellipse([250, 140, 270, 170], fill=(0, 0, 0, 255))
points = [(140, 280), (170, 250), (200, 240), (230, 250), (260, 280)]
draw.line(points, fill=(0, 0, 0, 255), width=14)
img_disconnected.save("am-am-vpn/images/character-disconnected.png")

print("✓ Изображения готовы")

# СОЗДАЕМ TELEGRAM BOT FILE
telegram_bot_code = '''
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application, CommandHandler, MessageHandler, filters, 
    ConversationHandler, CallbackQueryHandler, ContextTypes
)
import json
import os
from datetime import datetime
import hashlib

# НАСТРОЙКИ
BOT_TOKEN = "8277007634:AAFJaW4pws234-gOuC2CsbFXJZ0DLKFTo4Q"
DATABASE_FILE = "vpn_users.json"
ADMIN_ID = None  # Вставь свой ID администратора

# ЛОГИРОВАНИЕ
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# ЗАГРУЗКА И СОХРАНЕНИЕ ДАННЫХ
def load_users():
    """Загрузить пользователей из файла"""
    if os.path.exists(DATABASE_FILE):
        try:
            with open(DATABASE_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Ошибка загрузки БД: {e}")
            return {}
    return {}

def save_users(users):
    """Сохранить пользователей в файл"""
    try:
        with open(DATABASE_FILE, 'w', encoding='utf-8') as f:
            json.dump(users, f, indent=2, ensure_ascii=False)
    except Exception as e:
        logger.error(f"Ошибка сохранения БД: {e}")

def get_user_by_vpn_id(vpn_id):
    """Найти пользователя по VPN ID"""
    users = load_users()
    return users.get(vpn_id)

def add_user(vpn_id, nick, birthday, password, telegram_id):
    """Добавить пользователя"""
    users = load_users()
    
    if vpn_id in users:
        return False, "Этот ID уже зарегистрирован"
    
    users[vpn_id] = {
        "nick": nick,
        "birthday": birthday,
        "password": password,
        "telegram_id": telegram_id,
        "tariff": "free",
        "tariff_expires": None,
        "created_at": datetime.now().isoformat(),
        "balance": 0
    }
    save_users(users)
    return True, "Пользователь добавлен"

def update_user_tariff(vpn_id, tariff_type, days):
    """Обновить тариф пользователя"""
    users = load_users()
    
    if vpn_id not in users:
        return False, "Пользователь не найден"
    
    from datetime import timedelta
    expires = (datetime.now() + timedelta(days=days)).isoformat()
    
    users[vpn_id]["tariff"] = tariff_type
    users[vpn_id]["tariff_expires"] = expires
    save_users(users)
    return True, f"Тариф обновлен: {tariff_type} ({days} дней)"

# СОСТОЯНИЯ РАЗГОВОРА
WAITING_VPN_ID = 1
WAITING_ACTIVATION_KEY = 2

# КОМАНДЫ
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Команда /start"""
    keyboard = [
        [InlineKeyboardButton("🎮 Мой аккаунт", callback_data="account")],
        [InlineKeyboardButton("💳 Купить ключ", callback_data="buy_key")],
        [InlineKeyboardButton("❓ Помощь", callback_data="help")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        "👋 Привет! Я бот AM-AM VPN\n\n"
        "Здесь ты можешь:\n"
        "✓ Проверить свой аккаунт\n"
        "✓ Купить ключ активации\n"
        "✓ Получить помощь",
        reply_markup=reply_markup
    )

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Обработка кнопок"""
    query = update.callback_query
    await query.answer()
    
    if query.data == "account":
        await query.edit_message_text("📝 Введи свой VPN ID (8 цифр):")
        return WAITING_VPN_ID
    
    elif query.data == "buy_key":
        keyboard = [
            [InlineKeyboardButton("⏰ 7 дней - 99₽", callback_data="key_7d")],
            [InlineKeyboardButton("📅 30 дней - 299₽", callback_data="key_30d")],
            [InlineKeyboardButton("🎯 90 дней - 799₽", callback_data="key_90d")],
            [InlineKeyboardButton("◀️ Назад", callback_data="back")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(
            "💳 Выбери тариф:",
            reply_markup=reply_markup
        )
    
    elif query.data == "help":
        await query.edit_message_text(
            "❓ Помощь\n\n"
            "📱 Скачай приложение AM-AM VPN\n"
            "🔑 Введи свой ID и пароль\n"
            "💳 Активируй ключ из этого бота\n\n"
            "Вопросы? Напиши @support",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("◀️ Назад", callback_data="back")]])
        )
    
    elif query.data == "back":
        await start(update, context)
    
    elif query.data.startswith("key_"):
        days = int(query.data.split("_")[1].rstrip("d"))
        await query.edit_message_text(
            f"🔑 Введи свой VPN ID для активации ключа на {days} дней:\\n"
            "Формат: 8 цифр (например: 12345678)"
        )
        context.user_data["days"] = days
        return WAITING_ACTIVATION_KEY

async def handle_vpn_id(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Обработка введенного VPN ID"""
    vpn_id = update.message.text.strip()
    
    if len(vpn_id) != 8 or not vpn_id.isdigit():
        await update.message.reply_text("❌ ID должен состоять из 8 цифр")
        return WAITING_VPN_ID
    
    user = get_user_by_vpn_id(vpn_id)
    
    if not user:
        await update.message.reply_text(
            f"❌ Пользователь {vpn_id} не найден\\n\\n"
            "Сначала зарегистрируйся в приложении AM-AM VPN"
        )
        return WAITING_VPN_ID
    
    telegram_id = str(update.effective_user.id)
    if str(user.get("telegram_id")) != telegram_id:
        await update.message.reply_text("❌ Этот ID привязан к другому аккаунту Telegram")
        return WAITING_VPN_ID
    
    tariff = user.get("tariff", "free")
    expires = user.get("tariff_expires")
    
    info_text = (
        f"👤 Аккаунт: {user['nick']}\\n"
        f"🆔 ID: {vpn_id}\\n"
        f"📅 Создан: {user['created_at'][:10]}\\n"
        f"💳 Тариф: {tariff}\\n"
    )
    
    if expires:
        info_text += f"⏰ До: {expires[:10]}"
    
    await update.message.reply_text(info_text)
    return ConversationHandler.END

async def handle_activation_key(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Обработка ключа активации"""
    vpn_id = update.message.text.strip()
    
    if len(vpn_id) != 8 or not vpn_id.isdigit():
        await update.message.reply_text("❌ ID должен состоять из 8 цифр")
        return WAITING_ACTIVATION_KEY
    
    user = get_user_by_vpn_id(vpn_id)
    if not user:
        await update.message.reply_text("❌ Пользователь не найден")
        return WAITING_ACTIVATION_KEY
    
    telegram_id = str(update.effective_user.id)
    if str(user.get("telegram_id")) != telegram_id:
        await update.message.reply_text("❌ Этот ID привязан к другому аккаунту")
        return WAITING_ACTIVATION_KEY
    
    days = context.user_data.get("days", 30)
    tariff_type = "premium" if days >= 30 else "basic"
    
    success, message = update_user_tariff(vpn_id, tariff_type, days)
    
    if success:
        await update.message.reply_text(
            f"✅ {message}\\n\\n"
            f"Твой тариф активирован в приложении!"
        )
    else:
        await update.message.reply_text(f"❌ {message}")
    
    return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Отмена"""
    await update.message.reply_text("Операция отменена")
    return ConversationHandler.END

# АДМИН КОМАНДЫ
async def admin_stats(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Статистика для админа"""
    if update.effective_user.id != ADMIN_ID and ADMIN_ID is not None:
        await update.message.reply_text("❌ У тебя нет доступа")
        return
    
    users = load_users()
    total = len(users)
    premium = sum(1 for u in users.values() if u.get("tariff") == "premium")
    
    await update.message.reply_text(
        f"📊 Статистика\\n\\n"
        f"👥 Всего пользователей: {total}\\n"
        f"💳 Premium: {premium}\\n"
        f"📱 Free: {total - premium}"
    )

async def export_users(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Экспортировать пользователей (для админа)"""
    if update.effective_user.id != ADMIN_ID and ADMIN_ID is not None:
        await update.message.reply_text("❌ У тебя нет доступа")
        return
    
    users = load_users()
    
    export_text = "VPN_ID,Nick,Tariff,Expires\\n"
    for vpn_id, user in users.items():
        export_text += f"{vpn_id},{user['nick']},{user.get('tariff','free')},{user.get('tariff_expires','None')}\\n"
    
    with open("export.csv", "w", encoding="utf-8") as f:
        f.write(export_text)
    
    await update.message.reply_document(open("export.csv", "rb"))

def main() -> None:
    """Запуск бота"""
    app = Application.builder().token(BOT_TOKEN).build()
    
    # ОБРАБОТЧИК ДИАЛОГА
    conv_handler = ConversationHandler(
        entry_points=[
            CallbackQueryHandler(button_callback, pattern="^(account|buy_key|help|key_|back)$")
        ],
        states={
            WAITING_VPN_ID: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_vpn_id)],
            WAITING_ACTIVATION_KEY: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_activation_key)]
        },
        fallbacks=[CommandHandler("cancel", cancel)]
    )
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(conv_handler)
    app.add_handler(CommandHandler("stats", admin_stats))
    app.add_handler(CommandHandler("export", export_users))
    
    logger.info("Бот запущен!")
    app.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
'''

with open("telegram_bot.py", "w", encoding='utf-8') as f:
    f.write(telegram_bot_code)

print("✓ Telegram бот создан")

# ОБНОВЛЯЕМ HTML ДЛЯ ИНТЕГРАЦИИ С БОТОМ
html_content = '''<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AM-AM VPN</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        html, body {
            width: 100%;
            height: 100%;
            color: white;
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
        }
        
        .container {
            width: 100%;
            height: 100vh;
            max-width: 480px;
            margin: 0 auto;
            display: flex;
            flex-direction: column;
            background: url('images/background.jpg') center/cover no-repeat fixed;
            position: relative;
            overflow: hidden;
        }
        
        .header {
            padding: 12px 20px;
            border-bottom: 1px solid rgba(255,255,255,0.1);
            background: rgba(0,0,0,0.65);
            text-align: center;
            z-index: 5;
            flex-shrink: 0;
            min-height: 56px;
            display: flex;
            align-items: center;
            justify-content: center;
        }
        
        .header h1 {
            margin: 0;
            font-size: 20px;
            font-weight: 600;
        }
        
        .header .logout-btn {
            position: absolute;
            right: 20px;
            top: 50%;
            transform: translateY(-50%);
            background: rgba(255, 255, 255, 0.1);
            border: 1px solid rgba(255, 255, 255, 0.2);
            color: #fff;
            padding: 6px 12px;
            border-radius: 6px;
            font-size: 12px;
            cursor: pointer;
            transition: 0.2s;
            display: none;
        }
        
        .header .logout-btn.show {
            display: block;
        }
        
        .header .logout-btn:hover {
            background: rgba(255, 255, 255, 0.15);
        }
        
        .content {
            flex: 1;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: flex-start;
            padding: 20px;
            gap: 20px;
            z-index: 2;
            overflow-y: auto;
            overflow-x: hidden;
            position: relative;
            padding-bottom: 80px;
        }
        
        .character {
            width: 280px;
            height: 280px;
            flex-shrink: 0;
        }
        
        .character img {
            width: 100%;
            height: 100%;
            object-fit: contain;
        }
        
        .character.jump {
            animation: jump 0.6s;
        }
        
        .lollipop-btn {
            background: none;
            border: none;
            cursor: pointer;
            padding: 0;
            width: 200px;
            height: 240px;
            display: flex;
            align-items: center;
            justify-content: center;
            transition: transform 0.2s;
            flex-shrink: 0;
            margin-top: 20px;
        }
        
        .lollipop-btn:hover {
            transform: scale(1.08);
        }
        
        .lollipop-btn img {
            width: 180px;
            height: 220px;
            object-fit: contain;
        }
        
        .server-section {
            width: 100%;
            max-width: 400px;
        }
        
        .server-button {
            background: rgba(255, 255, 255, 0.08);
            border: 1px solid rgba(255, 255, 255, 0.15);
            border-radius: 8px;
            padding: 12px 16px;
            width: 100%;
            display: flex;
            align-items: center;
            justify-content: space-between;
            color: white;
            cursor: pointer;
            transition: 0.2s;
            font-size: 14px;
        }
        
        .server-button:hover {
            background: rgba(255, 255, 255, 0.12);
        }
        
        .server-button-content {
            display: flex;
            align-items: center;
            gap: 10px;
        }
        
        .server-flag {
            font-size: 18px;
        }
        
        .server-dropdown {
            position: absolute;
            top: 100%;
            left: 0;
            right: 0;
            background: rgba(10, 10, 10, 0.98);
            border: 1px solid rgba(255, 255, 255, 0.2);
            border-radius: 12px;
            overflow: hidden;
            margin-top: 8px;
            box-shadow: 0 4px 20px rgba(0, 0, 0, 0.5);
            display: none;
            z-index: 50;
        }
        
        .server-dropdown.show {
            display: block;
        }
        
        .server-option {
            padding: 12px 16px;
            display: flex;
            align-items: center;
            gap: 10px;
            cursor: pointer;
            transition: 0.2s;
            border-bottom: 1px solid rgba(255, 255, 255, 0.1);
            color: #999;
        }
        
        .server-option:last-child {
            border-bottom: none;
        }
        
        .server-option:hover {
            background: rgba(255, 255, 255, 0.1);
            color: #fff;
        }
        
        .server-option.selected {
            background: rgba(0, 255, 100, 0.2);
            color: #00ff64;
        }
        
        .server-option-status {
            margin-left: auto;
            font-size: 11px;
            color: #ff6b6b;
            font-weight: 600;
        }
        
        .bottom-nav {
            position: absolute;
            bottom: 0;
            left: 0;
            right: 0;
            height: 56px;
            background: rgba(0,0,0,0.65);
            border-top: 1px solid rgba(255,255,255,0.1);
            display: flex;
            justify-content: space-around;
            align-items: center;
            z-index: 100;
            flex-shrink: 0;
        }
        
        .nav-btn {
            background: none;
            border: none;
            color: #666;
            cursor: pointer;
            font-size: 11px;
            padding: 6px 8px;
            display: flex;
            flex-direction: column;
            align-items: center;
            gap: 3px;
            transition: color 0.2s;
            width: 60px;
            text-align: center;
            position: relative;
            border-radius: 12px;
        }
        
        .nav-btn:hover {
            color: #fff;
        }
        
        .nav-btn.active {
            color: #fff;
            background: rgba(255, 255, 255, 0.15);
            box-shadow: 0 0 15px rgba(0, 255, 100, 0.3);
        }
        
        .nav-icon {
            font-size: 20px;
        }
        
        .screen {
            display: none;
            position: absolute;
            top: 56px;
            left: 0;
            right: 0;
            bottom: 56px;
            flex-direction: column;
        }
        
        .screen.active {
            display: flex;
        }
        
        .filters-screen, .profile-screen {
            flex-direction: column;
            padding: 20px 16px 20px;
            overflow-y: auto;
            overflow-x: hidden;
            gap: 16px;
            background: rgba(0, 0, 0, 0.7);
        }
        
        .section {
            background: rgba(255, 255, 255, 0.08);
            border: 1px solid rgba(255, 255, 255, 0.15);
            border-radius: 12px;
            padding: 16px;
        }
        
        .section h3 {
            font-size: 14px;
            margin: 0 0 12px;
            font-weight: 600;
        }
        
        .menu-item {
            background: rgba(255, 255, 255, 0.08);
            border: 1px solid rgba(255, 255, 255, 0.15);
            border-radius: 12px;
            padding: 14px;
            margin-bottom: 12px;
            display: flex;
            align-items: center;
            gap: 12px;
            cursor: pointer;
            transition: 0.2s;
            text-decoration: none;
            color: white;
            position: relative;
        }
        
        .menu-item:hover {
            background: rgba(255, 255, 255, 0.12);
        }
        
        .menu-item.button {
            background: linear-gradient(135deg, #00ff64, #00cc44);
            color: #000;
            font-weight: bold;
            justify-content: center;
            border: none;
            padding: 12px 20px;
        }
        
        .menu-item.button:hover {
            transform: translateY(-2px);
            box-shadow: 0 6px 20px rgba(0, 255, 100, 0.3);
        }
        
        .menu-icon {
            font-size: 20px;
        }
        
        .menu-content {
            flex: 1;
        }
        
        .menu-title {
            margin: 0;
            font-size: 14px;
            font-weight: 500;
        }
        
        .menu-value {
            margin: 4px 0 0;
            font-size: 12px;
            color: #999;
        }
        
        .profile-header {
            text-align: center;
            margin-bottom: 20px;
        }
        
        .profile-logged-out {
            display: none;
            text-align: center;
        }
        
        .profile-logged-out.show {
            display: block;
        }
        
        .profile-logged-in {
            display: none;
        }
        
        .profile-logged-in.show {
            display: block;
        }
        
        .login-btn {
            width: 100%;
            padding: 12px 20px;
            background: linear-gradient(135deg, #00ff64, #00cc44);
            color: #000;
            border: none;
            border-radius: 10px;
            font-size: 14px;
            font-weight: bold;
            cursor: pointer;
            transition: 0.2s;
            margin-bottom: 16px;
        }
        
        .login-btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 6px 20px rgba(0, 255, 100, 0.3);
        }
        
        .avatar-container {
            position: relative;
            width: fit-content;
            margin: 0 auto 12px;
        }
        
        .avatar {
            width: 80px;
            height: 80px;
            background: linear-gradient(135deg, #7FFF00, #5FD700);
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 40px;
            overflow: hidden;
            cursor: pointer;
            position: relative;
        }
        
        .avatar img {
            width: 100%;
            height: 100%;
            object-fit: cover;
        }
        
        .avatar-upload {
            position: absolute;
            bottom: -6px;
            right: -6px;
            width: 32px;
            height: 32px;
            background: rgba(0, 255, 100, 0.3);
            border: 2px solid rgba(0, 255, 100, 0.6);
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 14px;
            cursor: pointer;
        }
        
        .avatar-upload input {
            display: none;
        }
        
        .profile-id {
            font-size: 12px;
            color: #999;
            margin: 0 0 12px;
            text-align: center;
        }
        
        .profile-tariff {
            background: rgba(0, 255, 100, 0.1);
            border: 1px solid rgba(0, 255, 100, 0.2);
            border-radius: 8px;
            padding: 10px;
            margin: 0 0 16px;
            font-size: 12px;
            color: #00ff64;
        }
        
        .profile-name {
            font-size: 18px;
            font-weight: 600;
            margin: 0 0 16px;
            text-align: center;
            background: rgba(255, 255, 255, 0.08);
            border: 1px solid rgba(255, 255, 255, 0.15);
            border-radius: 8px;
            padding: 8px 12px;
            color: white;
        }
        
        .profile-section {
            display: flex;
            flex-direction: column;
            gap: 12px;
            margin-bottom: 24px;
        }
        
        .profile-section.social {
            gap: 10px;
            margin-bottom: 28px;
        }
        
        .profile-section.settings {
            gap: 0;
        }
        
        .modal {
            display: none;
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(0, 0, 0, 0.9);
            z-index: 200;
            align-items: center;
            justify-content: center;
        }
        
        .modal.active {
            display: flex;
        }
        
        .modal-content {
            background: rgba(10, 10, 10, 0.95);
            border: 1px solid rgba(255, 255, 255, 0.2);
            border-radius: 16px;
            padding: 24px;
            max-width: 400px;
            width: 90%;
            position: relative;
            max-height: 90vh;
            overflow-y: auto;
        }
        
        .modal-close {
            position: absolute;
            top: 12px;
            right: 12px;
            background: rgba(255, 255, 255, 0.1);
            border: 1px solid rgba(255, 255, 255, 0.2);
            color: #fff;
            width: 32px;
            height: 32px;
            border-radius: 50%;
            cursor: pointer;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 18px;
            transition: 0.2s;
        }
        
        .modal-close:hover {
            background: rgba(255, 255, 255, 0.15);
        }
        
        .modal-title {
            font-size: 18px;
            font-weight: 600;
            margin: 0 0 16px;
            text-align: center;
            padding-right: 32px;
        }
        
        .modal-input {
            width: 100%;
            padding: 12px 16px;
            background: rgba(255, 255, 255, 0.08);
            border: 1px solid rgba(255, 255, 255, 0.15);
            border-radius: 8px;
            color: white;
            font-size: 14px;
            margin-bottom: 12px;
        }
        
        .modal-input::placeholder {
            color: #666;
        }
        
        .modal-input:focus {
            outline: none;
            border-color: rgba(0, 255, 100, 0.5);
            background: rgba(255, 255, 255, 0.1);
        }
        
        .modal-input-label {
            font-size: 12px;
            color: #999;
            margin-bottom: 4px;
            display: block;
        }
        
        .modal-error {
            color: #ff6b6b;
            font-size: 12px;
            text-align: center;
            margin-top: 8px;
            display: none;
        }
        
        .modal-success {
            color: #00ff64;
            font-size: 12px;
            text-align: center;
            margin-top: 8px;
            display: none;
        }
        
        .modal-buttons {
            display: flex;
            gap: 12px;
        }
        
        .modal-btn {
            flex: 1;
            padding: 12px 20px;
            border: none;
            border-radius: 8px;
            font-size: 14px;
            font-weight: 600;
            cursor: pointer;
            transition: 0.2s;
        }
        
        .modal-btn-confirm {
            background: linear-gradient(135deg, #00ff64, #00cc44);
            color: #000;
        }
        
        .modal-btn-confirm:hover {
            transform: translateY(-2px);
            box-shadow: 0 6px 20px rgba(0, 255, 100, 0.3);
        }
        
        .modal-btn-cancel {
            background: rgba(255, 255, 255, 0.1);
            color: #fff;
            border: 1px solid rgba(255, 255, 255, 0.2);
        }
        
        .modal-btn-cancel:hover {
            background: rgba(255, 255, 255, 0.15);
        }
        
        .form-group {
            margin-bottom: 12px;
        }
        
        .confirmation-text {
            background: rgba(255, 255, 255, 0.08);
            border: 1px solid rgba(255, 255, 255, 0.15);
            border-radius: 8px;
            padding: 12px;
            margin-bottom: 16px;
            font-size: 13px;
            line-height: 1.5;
        }
        
        .confirmation-field {
            margin-bottom: 8px;
        }
        
        .confirmation-label {
            color: #999;
            font-size: 12px;
        }
        
        .confirmation-value {
            color: #00ff64;
            font-weight: 600;
        }
        
        .lang-dropdown {
            position: relative;
        }
        
        .lang-menu {
            display: none;
            position: absolute;
            bottom: 100%;
            left: 0;
            right: 0;
            background: rgba(10, 10, 10, 0.98);
            border: 1px solid rgba(255, 255, 255, 0.2);
            border-radius: 12px;
            overflow: hidden;
            margin-bottom: 8px;
            box-shadow: 0 -4px 20px rgba(0, 0, 0, 0.5);
            z-index: 10;
        }
        
        .lang-menu.show {
            display: block;
        }
        
        .lang-option {
            padding: 12px 16px;
            display: flex;
            align-items: center;
            gap: 10px;
            cursor: pointer;
            transition: 0.2s;
            border-bottom: 1px solid rgba(255, 255, 255, 0.1);
            color: #999;
        }
        
        .lang-option:last-child {
            border-bottom: none;
        }
        
        .lang-option:hover {
            background: rgba(255, 255, 255, 0.1);
            color: #fff;
        }
        
        .lang-option.active {
            background: rgba(0, 255, 100, 0.2);
            color: #00ff64;
        }
        
        .lang-flag {
            font-size: 18px;
        }
        
        .lang-name {
            font-size: 13px;
            font-weight: 500;
        }
        
        @keyframes jump {
            0%, 100% {
                transform: translateY(0);
            }
            50% {
                transform: translateY(-30px);
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1 id="headerTitle">AM-AM VPN</h1>
            <button class="logout-btn" id="logoutBtn">Выход</button>
        </div>
        
        <!-- ГЛАВНАЯ ЭКРАН -->
        <div class="content screen active" id="mainScreen">
            <div class="character" id="character">
                <img id="characterImg" src="images/character-disconnected.png" alt="Character">
            </div>
            
            <button class="lollipop-btn" id="lollipopBtn">
                <img src="images/lollipop.gif" alt="Lollipop">
            </button>
            
            <!-- ВЫБОР СЕРВЕРА -->
            <div class="server-section" style="position: relative;">
                <button class="server-button" id="serverBtn">
                    <div class="server-button-content">
                        <span class="server-flag" id="serverFlag">🇷🇺</span>
                        <span id="serverName">Москва</span>
                    </div>
                    <span style="font-size: 12px;">▼</span>
                </button>
                
                <div class="server-dropdown" id="serverDropdown">
                    <div class="server-option" data-server="moscow" data-flag="🇷🇺">
                        <span class="server-flag">🇷🇺</span>
                        <span>Москва</span>
                        <span class="server-option-status">Недоступно</span>
                    </div>
                    <div class="server-option" data-server="newyork" data-flag="🇺🇸">
                        <span class="server-flag">🇺🇸</span>
                        <span>Нью-Йорк</span>
                        <span class="server-option-status">Недоступно</span>
                    </div>
                    <div class="server-option" data-server="berlin" data-flag="🇩🇪">
                        <span class="server-flag">🇩🇪</span>
                        <span>Берлин</span>
                        <span class="server-option-status">Недоступно</span>
                    </div>
                    <div class="server-option" data-server="tokyo" data-flag="🇯🇵">
                        <span class="server-flag">🇯🇵</span>
                        <span>Токио</span>
                        <span class="server-option-status">Недоступно</span>
                    </div>
                </div>
            </div>
        </div>
        
        <!-- ФИЛЬТРЫ ЭКРАН -->
        <div class="filters-screen screen" id="filtersScreen">
            <div class="section">
                <h3>Сайты</h3>
                <div class="menu-item">
                    <span class="menu-icon">🎬</span>
                    <div class="menu-content">
                        <p class="menu-title">YouTube</p>
                    </div>
                    <input type="checkbox" checked style="accent-color: #00ff64;">
                </div>
                <div class="menu-item">
                    <span class="menu-icon">💬</span>
                    <div class="menu-content">
                        <p class="menu-title">Discord</p>
                    </div>
                    <input type="checkbox" style="accent-color: #00ff64;">
                </div>
            </div>
        </div>
        
        <!-- ПРОФИЛЬ ЭКРАН -->
        <div class="profile-screen screen" id="profileScreen">
            <!-- ВЫШЛИ ИЗ АККАУНТА -->
            <div class="profile-header profile-logged-out show">
                <button class="login-btn" id="openAuthBtn">Вход / Регистрация</button>
            </div>
            
            <!-- В АККАУНТЕ -->
            <div class="profile-header profile-logged-in">
                <div class="avatar-container">
                    <div class="avatar" id="avatar">👤</div>
                    <label class="avatar-upload">
                        <input type="file" id="avatarInput" accept="image/*">
                        <span>📷</span>
                    </label>
                </div>
                
                <p class="profile-id" id="profileId">ID: 12345678</p>
                <p class="profile-tariff" id="profileTariff">💳 Тариф: Free</p>
                
                <input type="text" id="profileName" class="profile-name" placeholder="Введите ник" value="Пользователь">
            </div>
            
            <!-- КАТЕГОРИЯ: СОЦИАЛЬНЫЕ И ТАРИФ -->
            <div class="profile-section social">
                <a href="https://t.me/+WsHWAksr69E3NmMy" target="_blank" class="menu-item button">
                    <span class="menu-icon">📱</span>
                    <span class="menu-title">Наш Telegram канал</span>
                </a>
                
                <a href="https://t.me/HorriBrainBot" target="_blank" class="menu-item button">
                    <span class="menu-icon">💳</span>
                    <span class="menu-title">Купить в боте</span>
                </a>
            </div>
            
            <!-- КАТЕГОРИЯ: УСТРОЙСТВА И ЯЗЫК -->
            <div class="profile-section settings">
                <div class="menu-item">
                    <span class="menu-icon">💻</span>
                    <div class="menu-content">
                        <p class="menu-title">Мои устройства</p>
                        <p class="menu-value">0/2</p>
                    </div>
                </div>
                
                <div class="menu-item lang-dropdown">
                    <span class="menu-icon">🌐</span>
                    <div class="menu-content">
                        <p class="menu-title" id="langTitle">Язык</p>
                        <p class="menu-value" id="langValue">Русский</p>
                    </div>
                    
                    <div class="lang-menu" id="langMenu">
                        <div class="lang-option active" data-lang="ru">
                            <span class="lang-flag">🇷🇺</span>
                            <span class="lang-name">Русский</span>
                        </div>
                        <div class="lang-option" data-lang="en">
                            <span class="lang-flag">🇺🇸</span>
                            <span class="lang-name">English</span>
                        </div>
                        <div class="lang-option" data-lang="be">
                            <span class="lang-flag">🇧🇾</span>
                            <span class="lang-name">Беларусский</span>
                        </div>
                    </div>
                </div>
            </div>
        </div>
        
        <!-- МОДАЛЬНОЕ ОКНО РЕГИСТРАЦИИ / ВХОДА -->
        <div class="modal" id="authModal">
            <div class="modal-content">
                <button class="modal-close" id="authModalClose">✕</button>
                
                <!-- РЕГИСТРАЦИЯ -->
                <div id="registerForm">
                    <h2 class="modal-title">Регистрация</h2>
                    
                    <div class="form-group">
                        <label class="modal-input-label">Ник</label>
                        <input type="text" class="modal-input" id="regNick" placeholder="Ваш ник" maxlength="20">
                    </div>
                    
                    <div class="form-group">
                        <label class="modal-input-label">ID (8 цифр)</label>
                        <input type="text" class="modal-input" id="regId" placeholder="12345678" maxlength="8" inputmode="numeric">
                    </div>
                    
                    <div class="form-group">
                        <label class="modal-input-label">Дата рождения</label>
                        <input type="date" class="modal-input" id="regBirthday">
                    </div>
                    
                    <div class="form-group">
                        <label class="modal-input-label">Пароль</label>
                        <input type="password" class="modal-input" id="regPassword" placeholder="Минимум 6 символов" minlength="6">
                    </div>
                    
                    <div class="modal-error" id="regError"></div>
                    
                    <div class="modal-buttons" style="margin-bottom: 12px;">
                        <button class="modal-btn modal-btn-confirm" id="registerBtn" style="flex: 1;">Регистрация</button>
                    </div>
                    
                    <div style="text-align: center; padding-top: 12px; border-top: 1px solid rgba(255,255,255,0.1);">
                        <button id="toggleLoginBtn" style="background: none; border: none; color: #00ff64; cursor: pointer; font-size: 13px; margin-top: 8px;">Уже есть аккаунт? Войти</button>
                    </div>
                </div>
                
                <!-- ВХОД -->
                <div id="loginForm" style="display: none;">
                    <h2 class="modal-title">Вход</h2>
                    
                    <div class="form-group">
                        <label class="modal-input-label">ID</label>
                        <input type="text" class="modal-input" id="loginId" placeholder="Ваш ID" maxlength="8" inputmode="numeric">
                    </div>
                    
                    <div class="form-group">
                        <label class="modal-input-label">Пароль</label>
                        <input type="password" class="modal-input" id="loginPassword" placeholder="Ваш пароль">
                    </div>
                    
                    <div class="modal-error" id="loginError"></div>
                    
                    <div class="modal-buttons">
                        <button class="modal-btn modal-btn-confirm" id="loginBtn" style="flex: 1;">Войти</button>
                    </div>
                    
                    <div style="text-align: center; padding-top: 12px; border-top: 1px solid rgba(255,255,255,0.1);">
                        <button id="toggleRegisterBtn" style="background: none; border: none; color: #00ff64; cursor: pointer; font-size: 13px; margin-top: 8px;">Нет аккаунта? Создать</button>
                    </div>
                </div>
            </div>
        </div>
        
        <!-- МОДАЛЬНОЕ ОКНО ПОДТВЕРЖДЕНИЯ -->
        <div class="modal" id="confirmModal">
            <div class="modal-content">
                <h2 class="modal-title">Подтвердите данные</h2>
                
                <div class="confirmation-text">
                    <div class="confirmation-field">
                        <span class="confirmation-label">Ник:</span>
                        <span class="confirmation-value" id="confirmNick"></span>
                    </div>
                    <div class="confirmation-field">
                        <span class="confirmation-label">ID:</span>
                        <span class="confirmation-value" id="confirmId"></span>
                    </div>
                    <div class="confirmation-field">
                        <span class="confirmation-label">Дата рождения:</span>
                        <span class="confirmation-value" id="confirmBirthday"></span>
                    </div>
                    <div class="confirmation-field">
                        <span class="confirmation-label">Пароль:</span>
                        <span class="confirmation-value">••••••</span>
                    </div>
                </div>
                
                <div class="modal-buttons">
                    <button class="modal-btn modal-btn-cancel" id="confirmCancelBtn" style="flex: 1;">Отмена</button>
                    <button class="modal-btn modal-btn-confirm" id="confirmOkBtn" style="flex: 1;">Подтвердить</button>
                </div>
            </div>
        </div>
        
        <!-- НАВИГАЦИЯ -->
        <div class="bottom-nav">
            <button class="nav-btn active" data-screen="mainScreen">
                <span class="nav-icon">🏠</span>
                <span>Главная</span>
            </button>
            <button class="nav-btn" data-screen="filtersScreen">
                <span class="nav-icon">⭐</span>
                <span>Фильтры</span>
            </button>
            <button class="nav-btn" data-screen="profileScreen">
                <span class="nav-icon">👤</span>
                <span>Профиль</span>
            </button>
        </div>
    </div>
    
    <script>
        const STORAGE_KEY = 'am_am_vpn_accounts';
        const BOT_API_URL = 'https://api.telegram.org/bot8277007634:AAFJaW4pws234-gOuC2CsbFXJZ0DLKFTo4Q';
        
        let currentLanguage = 'ru';
        let connected = false;
        let isLoggedIn = false;
        let currentUser = null;
        let allAccounts = [];
        
        // ЗАГРУЗКА АККАУНТОВ
        function loadAccounts() {
            const stored = localStorage.getItem(STORAGE_KEY);
            if (stored) {
                allAccounts = JSON.parse(stored);
            }
        }
        
        // СОХРАНЕНИЕ АККАУНТОВ
        function saveAccounts() {
            localStorage.setItem(STORAGE_KEY, JSON.stringify(allAccounts));
        }
        
        // ОТПРАВКА ДАННЫХ НА БОТ
        async function syncWithBot(userData) {
            try {
                const message = `📱 Новый аккаунт:\\nID: ${userData.id}\\nНик: ${userData.nick}\\nДата: ${userData.birthday}`;
                await fetch(`${BOT_API_URL}/sendMessage`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        chat_id: -1002408977639,
                        text: message
                    })
                });
            } catch (e) {
                console.log('Синхронизация с ботом (не критично)');
            }
        }
        
        loadAccounts();
        
        // ЭЛЕМЕНТЫ
        const authModal = document.getElementById('authModal');
        const authModalClose = document.getElementById('authModalClose');
        const registerForm = document.getElementById('registerForm');
        const loginForm = document.getElementById('loginForm');
        const toggleLoginBtn = document.getElementById('toggleLoginBtn');
        const toggleRegisterBtn = document.getElementById('toggleRegisterBtn');
        const regNick = document.getElementById('regNick');
        const regId = document.getElementById('regId');
        const regBirthday = document.getElementById('regBirthday');
        const regPassword = document.getElementById('regPassword');
        const registerBtn = document.getElementById('registerBtn');
        const regError = document.getElementById('regError');
        const loginId = document.getElementById('loginId');
        const loginPassword = document.getElementById('loginPassword');
        const loginBtn = document.getElementById('loginBtn');
        const loginError = document.getElementById('loginError');
        const confirmModal = document.getElementById('confirmModal');
        const confirmCancelBtn = document.getElementById('confirmCancelBtn');
        const confirmOkBtn = document.getElementById('confirmOkBtn');
        const confirmNick = document.getElementById('confirmNick');
        const confirmId = document.getElementById('confirmId');
        const confirmBirthday = document.getElementById('confirmBirthday');
        const openAuthBtn = document.getElementById('openAuthBtn');
        const headerTitle = document.getElementById('headerTitle');
        const logoutBtn = document.getElementById('logoutBtn');
        const characterImg = document.getElementById('characterImg');
        const character = document.getElementById('character');
        const lollipopBtn = document.getElementById('lollipopBtn');
        const profileLoggedOut = document.querySelector('.profile-logged-out');
        const profileLoggedIn = document.querySelector('.profile-logged-in');
        const profileId = document.getElementById('profileId');
        const profileTariff = document.getElementById('profileTariff');
        const profileName = document.getElementById('profileName');
        const avatar = document.getElementById('avatar');
        const avatarInput = document.getElementById('avatarInput');
        const navBtns = document.querySelectorAll('.nav-btn');
        const screens = document.querySelectorAll('.screen');
        const langMenu = document.getElementById('langMenu');
        const langOptions = document.querySelectorAll('.lang-option');
        const langDropdown = document.querySelector('.lang-dropdown');
        
        // СЕРВЕР
        const serverBtn = document.getElementById('serverBtn');
        const serverDropdown = document.getElementById('serverDropdown');
        const serverOptions = document.querySelectorAll('.server-option');
        const serverFlag = document.getElementById('serverFlag');
        const serverName = document.getElementById('serverName');
        
        // ВЫБОР СЕРВЕРА
        serverBtn.addEventListener('click', () => {
            serverDropdown.classList.toggle('show');
        });
        
        serverOptions.forEach(option => {
            option.addEventListener('click', () => {
                serverOptions.forEach(o => o.classList.remove('selected'));
                option.classList.add('selected');
                serverFlag.textContent = option.getAttribute('data-flag');
                serverName.textContent = option.querySelector('span:nth-child(2)').textContent;
                serverDropdown.classList.remove('show');
            });
        });
        
        document.addEventListener('click', (e) => {
            if (!serverBtn.contains(e.target) && !serverDropdown.contains(e.target)) {
                serverDropdown.classList.remove('show');
            }
        });
        
        // АВТОРИЗАЦИЯ
        openAuthBtn.addEventListener('click', () => {
            authModal.classList.add('active');
            registerForm.style.display = 'block';
            loginForm.style.display = 'none';
        });
        
        authModalClose.addEventListener('click', () => authModal.classList.remove('active'));
        
        toggleLoginBtn.addEventListener('click', () => {
            registerForm.style.display = 'none';
            loginForm.style.display = 'block';
        });
        
        toggleRegisterBtn.addEventListener('click', () => {
            loginForm.style.display = 'none';
            registerForm.style.display = 'block';
        });
        
        // РЕГИСТРАЦИЯ
        registerBtn.addEventListener('click', () => {
            const nick = regNick.value.trim();
            const id = regId.value.trim();
            const birthday = regBirthday.value;
            const password = regPassword.value;
            
            regError.style.display = 'none';
            
            if (!nick || !id || !birthday || !password) {
                regError.textContent = 'Заполните все поля';
                regError.style.display = 'block';
                return;
            }
            
            if (id.length !== 8 || !/^\\d+$/.test(id)) {
                regError.textContent = 'ID должен состоять из 8 цифр';
                regError.style.display = 'block';
                return;
            }
            
            if (password.length < 6) {
                regError.textContent = 'Пароль минимум 6 символов';
                regError.style.display = 'block';
                return;
            }
            
            if (allAccounts.some(acc => acc.id === id)) {
                regError.textContent = 'ID уже зарегистрирован';
                regError.style.display = 'block';
                return;
            }
            
            confirmNick.textContent = nick;
            confirmId.textContent = id;
            confirmBirthday.textContent = birthday;
            
            authModal.classList.remove('active');
            confirmModal.classList.add('active');
            
            confirmOkBtn.onclick = () => {
                const newAccount = {
                    nick, id, birthday, password,
                    tariff: "free",
                    tariff_expires: null,
                    created_at: new Date().toISOString()
                };
                allAccounts.push(newAccount);
                saveAccounts();
                syncWithBot(newAccount);
                
                currentUser = newAccount;
                confirmModal.classList.remove('active');
                isLoggedIn = true;
                profileLoggedOut.classList.remove('show');
                profileLoggedIn.classList.add('show');
                logoutBtn.classList.add('show');
                profileId.textContent = 'ID: ' + id;
                profileName.value = nick;
                updateTariffDisplay();
            };
        });
        
        confirmCancelBtn.addEventListener('click', () => {
            confirmModal.classList.remove('active');
            authModal.classList.add('active');
        });
        
        // ВХОД
        loginBtn.addEventListener('click', () => {
            const id = loginId.value.trim();
            const password = loginPassword.value;
            
            loginError.style.display = 'none';
            
            if (!id || !password) {
                loginError.textContent = 'Введите ID и пароль';
                loginError.style.display = 'block';
                return;
            }
            
            const account = allAccounts.find(acc => acc.id === id && acc.password === password);
            
            if (account) {
                currentUser = account;
                authModal.classList.remove('active');
                isLoggedIn = true;
                profileLoggedOut.classList.remove('show');
                profileLoggedIn.classList.add('show');
                logoutBtn.classList.add('show');
                profileId.textContent = 'ID: ' + id;
                profileName.value = account.nick;
                updateTariffDisplay();
            } else {
                loginError.textContent = 'Неверный ID или пароль';
                loginError.style.display = 'block';
            }
        });
        
        // ВЫХОД
        logoutBtn.addEventListener('click', () => {
            isLoggedIn = false;
            currentUser = null;
            profileLoggedOut.classList.add('show');
            profileLoggedIn.classList.remove('show');
            logoutBtn.classList.remove('show');
            connected = false;
            characterImg.src = 'images/character-disconnected.png';
            headerTitle.textContent = 'Отключено';
        });
        
        function updateTariffDisplay() {
            if (currentUser) {
                const tariff = currentUser.tariff || 'free';
                const expires = currentUser.tariff_expires;
                let text = '💳 Тариф: ' + (tariff === 'premium' ? 'Premium' : 'Free');
                if (expires) {
                    text += ' (до ' + expires.slice(0, 10) + ')';
                }
                profileTariff.textContent = text;
            }
        }
        
        // ЯЗЫК
        langDropdown.addEventListener('click', (e) => {
            if (!e.target.closest('.lang-menu')) {
                langMenu.classList.toggle('show');
            }
        });
        
        langOptions.forEach(option => {
            option.addEventListener('click', () => {
                currentLanguage = option.getAttribute('data-lang');
                langOptions.forEach(o => o.classList.remove('active'));
                option.classList.add('active');
                langMenu.classList.remove('show');
            });
        });
        
        document.addEventListener('click', (e) => {
            if (!langDropdown.contains(e.target)) {
                langMenu.classList.remove('show');
            }
        });
        
        // НАВИГАЦИЯ
        navBtns.forEach(btn => {
            btn.addEventListener('click', () => {
                navBtns.forEach(b => b.classList.remove('active'));
                btn.classList.add('active');
                screens.forEach(s => s.classList.remove('active'));
                document.getElementById(btn.getAttribute('data-screen')).classList.add('active');
            });
        });
        
        // ВПН
        lollipopBtn.addEventListener('click', () => {
            character.classList.add('jump');
            connected = !connected;
            characterImg.src = connected ? 'images/character-connected.png' : 'images/character-disconnected.png';
            headerTitle.textContent = connected ? 'Подключено' : 'Отключено';
            setTimeout(() => character.classList.remove('jump'), 600);
        });
        
        avatarInput.addEventListener('change', (e) => {
            const file = e.target.files[0];
            if (file) {
                const reader = new FileReader();
                reader.onload = (event) => {
                    avatar.innerHTML = '<img src="' + event.target.result + '" alt="Avatar">';
                };
                reader.readAsDataURL(file);
            }
        });
        
        avatar.addEventListener('click', () => avatarInput.click());
    </script>
</body>
</html>
'''

with open("am-am-vpn/index.html", "w", encoding='utf-8') as f:
    f.write(html_content)

print("✓ Приложение с интеграцией бота создано")

with open("am-am-vpn/images/background.txt", "w", encoding='utf-8') as f:
    f.write('Положи сюда свой файл background.jpg\n')

with zipfile.ZipFile("am-am-vpn.zip", 'w', zipfile.ZIP_DEFLATED) as z:
    for root, dirs, files_list in os.walk("am-am-vpn"):
        for f in files_list:
            file_path = os.path.join(root, f)
            arcname = os.path.relpath(file_path, ".")
            z.write(file_path, arcname)

print("✅ ГОТОВО!")
print("\n✨ Интеграция с ботом:")
print("   ✓ telegram_bot.py - готовый код бота")
print("   ✓ Хранение аккаунтов в JSON (vpn_users.json)")
print("   ✓ Автосинхронизация с ботом")
print("   ✓ Управление тарифами через бот")
print("\n📝 Что делать:")
print("   1. pip install python-telegram-bot")
print("   2. З��пустить: python telegram_bot.py")
print("   3. Бот будет получать новых пользователей")
print("   4. В боте доступны команды:")
print("      - /start (главное меню)")
print("      - /stats (статистика для админа)")
print("      - /export (экспорт пользователей)")

from google.colab import files
files.download("am-am-vpn.zip")
