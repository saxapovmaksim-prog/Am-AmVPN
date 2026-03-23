import os
import zipfile
import shutil
from PIL import Image, ImageDraw
import math

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
        
        /* СЕРВЕР */
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
                    <span class="menu-title">Покупка тарифа</span>
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
        
        let currentLanguage = 'ru';
        let connected = false;
        let isLoggedIn = false;
        let currentUser = null;
        let allAccounts = [];
        
        // ЗАГРУЗКА АККАУНТОВ ИЗ ХРАНИЛИЩА
        function loadAccounts() {
            const stored = localStorage.getItem(STORAGE_KEY);
            if (stored) {
                allAccounts = JSON.parse(stored);
            }
        }
        
        // СОХРАНЕНИЕ АККАУНТОВ В ХРАНИЛИЩЕ
        function saveAccounts() {
            localStorage.setItem(STORAGE_KEY, JSON.stringify(allAccounts));
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
            
            // ПРОВЕРКА НА ДУБЛИРОВАНИЕ ID
            if (allAccounts.some(acc => acc.id === id)) {
                regError.textContent = 'ID уже зарегистрирован';
                regError.style.display = 'block';
                return;
            }
            
            // ПОКАЗЫВАЕМ ПОДТВЕРЖДЕНИЕ
            confirmNick.textContent = nick;
            confirmId.textContent = id;
            confirmBirthday.textContent = birthday;
            
            authModal.classList.remove('active');
            confirmModal.classList.add('active');
            
            confirmOkBtn.onclick = () => {
                const newAccount = { nick, id, birthday, password };
                allAccounts.push(newAccount);
                saveAccounts();
                
                currentUser = newAccount;
                confirmModal.classList.remove('active');
                isLoggedIn = true;
                profileLoggedOut.classList.remove('show');
                profileLoggedIn.classList.add('show');
                logoutBtn.classList.add('show');
                profileId.textContent = 'ID: ' + id;
                profileName.value = nick;
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
        
        // ВПН КНОПКА
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

print("✓ Приложение обновлено")

with open("am-am-vpn/images/background.txt", "w", encoding='utf-8') as f:
    f.write('Положи сюда свой файл background.jpg\n')

with zipfile.ZipFile("am-am-vpn.zip", 'w', zipfile.ZIP_DEFLATED) as z:
    for root, dirs, files_list in os.walk("am-am-vpn"):
        for f in files_list:
            file_path = os.path.join(root, f)
            arcname = os.path.relpath(file_path, ".")
            z.write(file_path, arcname)

print("✅ ГОТОВО!")
print("\n✨ Новое:")
print("   ✓ Выпадающее меню выбора сервера")
print("   ✓ Все серверы показывают 'Недоступно'")
print("   ✓ Выбранный сервер отображается в кнопке")
print("   ✓ LocalStorage сохраняет все аккаунты")
print("   ✓ Проверка на дублирование ID")
print("   ✓ Вход с существующими аккаунтами")

from google.colab import files
files.download("am-am-vpn.zip")
