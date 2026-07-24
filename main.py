import os
import random
import threading
import time
from flask import Flask
from telebot import TeleBot, types

# ================= FLASK SERVER (RENDER PORTI UCHUN) =================
app = Flask(__name__)

@app.route('/')
def home():
    return "Death Note Bot 24/7 ishlamoqda!", 200

def run_flask():
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)

# ================= BOT TOKENI VA MEDIA FILE_ID'LAR =================
TOKEN = os.environ.get('BOT_TOKEN', '8816866283:AAGJK1TXHj1b7LZQYQOG7e5w18fOfUH51PM')
bot = TeleBot(TOKEN)

# MEDIA FILE_ID'LAR
VID_KIRA_FIRST_KILL = "BAACAgIAAxkBAAOgamOkYUl93OnEJUrtZU_gomJwFlMAAoqgAAL2HBlLgTO60GPr0hI9BA"
VID_L_CHECK = "BAACAgIAAxkBAAOeamOj_BZ7ATgL5IYqkqp_c8ttBG4AAoOgAAL2HBlL1DxA2BLMmCo9BA"
VID_KIRA_WIN = "BAACAgIAAxkBAAOcamOjlGxvF-sQRjpGhOMss5BoRJAAAn6gAAL2HBlL9YoV8W6jmtU9BA"
VID_L_WIN = "BAACAgIAAxkBAAOiamOk543jPQXByEQZxEIcamNciz4AAoygAAL2HBlLHjkU3rpfDRY9BA"
VID_NIGHT_SHINIGAMI = "BAACAgIAAxkBAAOkamOlVOl26MJFVUhfNHNi9rlGklEAAo6gAAL2HBlLZkqb-a1mXQg9BA"
GIF_KIRA_DEATH = "CgACAgIAAxkBAAOmamOtjuILC7y_gntablguan3uETAAAtKgAAL2HBlLRYDNDMWd9So9BA"
GIF_DAY_START = "CgACAgIAAxkBAAOoamOutc6Wuf_8qZRR9P4Sa-Ma7-MAAuGgAAL2HBlLTIcoCecwxoY9BA"
GIF_L_DEATH = "CgACAgIAAxkBAAOqamOvVxow7dGO_DS5GKPmYcfbIRMAAuygAAL2HBlLfAQYGv77wJU9B"

# Baza
games = {}
user_data = {}

def get_user_profile(user_id):
    if user_id not in user_data:
        user_data[user_id] = {'coins': 100, 'inventory': []}
    return user_data[user_id]

# ================= ROLLARNI TAQSIMLASH =================
def assign_roles(players_dict):
    player_ids = list(players_dict.keys())
    random.shuffle(player_ids)
    
    roles = {}
    total = len(player_ids)
    
    roles[player_ids[0]] = "Kira"
    roles[player_ids[1]] = "L"
    
    if total >= 4:
        roles[player_ids[2]] = "Misa"
    if total >= 5:
        roles[player_ids[3]] = "Ryuk"
    if total >= 6:
        roles[player_ids[4]] = "Soichiro Yagami"
    if total >= 7:
        roles[player_ids[5]] = "Near"
    if total >= 8:
        roles[player_ids[6]] = "Mello"
        
    for p_id in player_ids:
        if p_id not in roles:
            roles[p_id] = "Matsuda (Politsiya)"
            
    return roles

# ================= TAYMER (45 SONIYA) =================
def auto_start_timer(chat_id):
    time.sleep(45)
    game = games.get(chat_id)
    if game and game.get('status') == 'waiting':
        if len(game.get('players', {})) >= 3:
            bot.send_message(chat_id, "⏰ Vaqt tugadi! O'yin avtomatik ravishda boshlanmoqda...")
            start_game_logic(chat_id)
        else:
            bot.send_message(chat_id, "❌ O'yinni boshlash uchun kamida 3 kishi kerak edi. O'yin bekor qilindi.")
            games.pop(chat_id, None)

# ================= O'YINNI BOSHLASH =================
def start_game_logic(chat_id):
    game = games.get(chat_id)
    if not game:
        return

    game['status'] = 'in_game'
    game['roles'] = assign_roles(game['players'])
    game['alive'] = list(game['players'].keys())
    game['notebook_holder'] = "Kira"
    game['l_alive'] = True
    game['first_kill_done'] = False

    bot.send_message(chat_id, "🎭 **Barcha personajlar va rollar taqsimlandi!**\n\nHar bir o'yinchiga shaxsiy chatda o'z roli va vazifasi yuborildi.")

    role_descriptions = {
        "Kira": "📓 Siz Kirasiz (Light Yagami)! Vazifangiz: Tunda O'lim Daftari orqali hammangizni yo'q qilish va L'ni topish.",
        "L": "🕵️‍♂️ Siz Lsiz! Vazifangiz: Tunda shubhalilarni tekshirish.",
        "Misa": "👁 Siz Misa Amanesiz! Vazifangiz: Kiraga yordam berish.",
        "Ryuk": "🍎 Siz Ryuksiz (Shinigami)! Siz neytralsiz, tunda kartalarga mo'ralaysiz.",
        "Soichiro Yagami": "👮‍♂️ Siz Soichiro Yagamisiz! Vazifangiz: Tunda bir o'yinchini himoya qilish.",
        "Near": "🧩 Siz Nearsiz! L halok bo'lsa uning ishini davom ettirasiz.",
        "Mello": "🍫 Siz Mellosiz! L halok bo'lsa aktivlashasiz.",
        "Matsuda (Politsiya)": "👮‍♂️ Siz Matsudasiz! Kunduzi muhokamada qatnashasiz."
    }

    for p_id, role in game['roles'].items():
        try:
            desc = role_descriptions.get(role, f"Sizning rolingiz: {role}")
            bot.send_message(p_id, desc)
        except Exception:
            pass

    time.sleep(2)
    start_night(chat_id)
  # ================= TUN SIKLI =================
def start_night(chat_id):
    game = games.get(chat_id)
    if not game:
        return

    game['status'] = 'night'
    game['protected_player'] = None
    game['pending_kill'] = None

    try:
        bot.send_video(chat_id, VID_NIGHT_SHINIGAMI, caption="🌙 **Shahar ustiga tun tushdi... Shinigami kulgisi yangramoqda!**")
    except Exception:
        bot.send_message(chat_id, "🌙 Shahar ustiga tun tushdi...")

    alive_players = game['alive']
    for player_id in alive_players:
        role = game['roles'].get(player_id)

        # KIRA
        if (role == "Kira" and game['notebook_holder'] == "Kira") or (role == "Misa" and game['notebook_holder'] == "Misa"):
            kb = types.InlineKeyboardMarkup(row_width=1)
            for target_id in alive_players:
                if target_id != player_id:
                    p_name = game['players'][target_id]
                    kb.add(types.InlineKeyboardButton(f"🗡 {p_name}ni nishonga olish", callback_data=f"target_{chat_id}_{target_id}"))
            
            try:
                bot.send_message(player_id, "📓 **Death Note:** Bugun tunda kimni nishonga olasiz?", reply_markup=kb)
            except Exception:
                pass

        # L
        elif role == "L" or (role == "Near" and not game['l_alive']):
            kb = types.InlineKeyboardMarkup(row_width=1)
            for target_id in alive_players:
                if target_id != player_id:
                    p_name = game['players'][target_id]
                    kb.add(types.InlineKeyboardButton(f"🔍 {p_name}ni tekshirish", callback_data=f"checkl_{chat_id}_{target_id}"))
            try:
                bot.send_message(player_id, "🕵️‍♂️ **L:** Kimni tekshirmoqchisiz?", reply_markup=kb)
            except Exception:
                pass

        # SOICHIRO
        elif role == "Soichiro Yagami":
            kb = types.InlineKeyboardMarkup(row_width=1)
            for target_id in alive_players:
                p_name = game['players'][target_id]
                kb.add(types.InlineKeyboardButton(f"🛡 {p_name}ni himoya qilish", callback_data=f"protect_{chat_id}_{target_id}"))
            try:
                bot.send_message(player_id, "👮‍♂️ **Soichiro Yagami:** Bugun tunda kimni himoya qilasiz?", reply_markup=kb)
            except Exception:
                pass

# ================= KUNDUZ SIKLI =================
def start_day(chat_id):
    game = games.get(chat_id)
    if not game:
        return

    game['status'] = 'day'

    try:
        bot.send_animation(chat_id, GIF_DAY_START, caption="☀️ **Quyosh chiqdi! Shaharda yangi kun boshlandi.**\n\nKechasi sodir bo me'siga o'tgan hodisalarni muhokama qiling!")
    except Exception:
        bot.send_message(chat_id, "☀️ **Quyosh chiqdi! Kun boshlandi.**")

# ================= COMMAND HANDLERLAR =================
@bot.message_handler(commands=['start'])
def start_cmd(message):
    bot.reply_to(message, "👋 Death Note Botiga xush kelibsiz!\n\n🎮 Guruhda `/create` buyrug'i orqali o'yin yarating.\n🛒 `/shop` — Do'kondan xaridlar qilish.")

@bot.message_handler(commands=['shop'])
def shop_cmd(message):
    profile = get_user_profile(message.from_user.id)
    kb = types.InlineKeyboardMarkup(row_width=1)
    kb.add(types.InlineKeyboardButton("🍎 Ryuk Olmasi (30 coin)", callback_data="buy_apple"))
    
    bot.reply_to(message, f"🛒 **Death Note Do'koni**\n\nBalansingiz: {profile['coins']} coin", reply_markup=kb)

@bot.message_handler(commands=['create'])
def create_game_command(message):
    chat_id = message.chat.id
    if chat_id in games:
        bot.reply_to(message, "⚠️ Bu guruhda allaqachon o'yin ketmoqda!")
        return

    games[chat_id] = {
        'status': 'waiting',
        'players': {message.from_user.id: message.from_user.first_name},
        'roles': {},
        'alive': [],
        'first_kill_done': False
    }

    kb = types.InlineKeyboardMarkup()
    kb.add(types.InlineKeyboardButton("✋ O'yinga Qo'shilish", callback_data=f"join_{chat_id}"))
    kb.add(types.InlineKeyboardButton("🚀 O'yinni Boshlash", callback_data=f"start_{chat_id}"))

    bot.send_message(chat_id, f"🎮 **Death Note O'yini Yaratildi!**\n\nYaratuvchi: {message.from_user.first_name}\n\n45 soniya ichida qo'shiling!", reply_markup=kb)
    
    threading.Thread(target=auto_start_timer, args=(chat_id,), daemon=True).start()

# ================= CALLBACK HANDLERLAR =================
@bot.callback_query_handler(func=lambda call: True)
def callback_inline(call):
    data = call.data.split("_")
    action = data[0]

    if action == "join":
        c_id = int(data[1])
        game = games.get(c_id)
        if game and game['status'] == 'waiting':
            if call.from_user.id not in game['players']:
                game['players'][call.from_user.id] = call.from_user.first_name
                bot.answer_callback_query(call.id, "Qo'shildingiz!")
            else:
                bot.answer_callback_query(call.id, "Siz allaqachon o'yindasiz!")

    elif action == "start":
        c_id = int(data[1])
        game = games.get(c_id)
        if game and game['status'] == 'waiting':
            if len(game['players']) >= 3:
                start_game_logic(c_id)
            else:
                bot.answer_callback_query(call.id, "Kamida 3 kishi kerak!", show_alert=True)

    elif action == "target":
        c_id = int(data[1])
        target_id = int(data[2])
        game = games.get(c_id)
        if game:
            game['pending_kill'] = target_id
            kb = types.InlineKeyboardMarkup(row_width=1)
            kb.add(types.InlineKeyboardButton("💔 Yurak xuruji", callback_data=f"cause_{c_id}_Yurak xuruji"))
            kb.add(types.InlineKeyboardButton("🚗 Yo'l transport hodisasi", callback_data=f"cause_{c_id}_Yo'l transport hodisasi"))
            bot.edit_message_text("📓 **O'lim sababini tanlang:**", call.message.chat.id, call.message.message_id, reply_markup=kb)

    elif action == "cause":
        c_id = int(data[1])
        cause_text = data[2]
        game = games.get(c_id)
        if game:
            if not game.get('first_kill_done'):
                try:
                    bot.send_video(c_id, VID_KIRA_FIRST_KILL, caption="📓 **Kira birinchi qurbonining ismini daftarga ishtiyoq bilan yozmoqda...**")
                    game['first_kill_done'] = True
                except Exception:
                    pass
            
            target_id = game.get('pending_kill')
            if target_id and game['roles'].get(target_id) == "L":
                game['l_alive'] = False
                try:
                    bot.send_animation(c_id, GIF_L_DEATH, caption="😱 **L halok bo'ldi!** Endi tergovni Near va Mello o'z qo'liga oladi...")
                except Exception:
                    pass

            bot.answer_callback_query(call.id, "Sabab yozildi!")
            bot.edit_message_text(f"✅ Niyat qabul qilindi. O'lim sababi: *{cause_text}*", call.message.chat.id, call.message.message_id)

    elif action == "checkl":
        c_id = int(data[1])
        target_id = int(data[2])
        game = games.get(c_id)
        if game:
            try:
                bot.send_video(call.message.chat.id, VID_L_CHECK, caption="🔍 **L shubhalini diqqat bilan tergov qilmoqda...**")
            except Exception:
                pass
            
            target_role = game['roles'].get(target_id)
            res = "HA (Kira!)" if target_role == "Kira" else "YO'Q (Begunoh)"
            bot.answer_callback_query(call.id, f"Natija: {res}", show_alert=True)

    elif action == "protect":
        c_id = int(data[1])
        target_id = int(data[2])
        game = games.get(c_id)
        if game:
            game['protected_player'] = target_id
            bot.answer_callback_query(call.id, "Himoya o'rnatildi!")
            bot.edit_message_text("🛡 Tanlangan o'yinchi bu kecha himoyaga olindi.", call.message.chat.id, call.message.message_id)

if __name__ == "__main__":
    threading.Thread(target=run_flask, daemon=True).start()
    bot.polling(none_stop=True)
  
