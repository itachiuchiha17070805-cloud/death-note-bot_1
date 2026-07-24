import os
import random
import threading
import time
from flask import Flask
from telebot import TeleBot, types

# ================= FLASK SERVER (RENDER UCHUN) =================
app = Flask(__name__)

@app.route('/')
def home():
    return "Death Note Bot 24/7 ishlamoqda!", 200

def run_flask():
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)

# ================= BOT TOKENI VA OWNER ID =================
TOKEN = os.environ.get('BOT_TOKEN', '8816866283:AAGJK1TXHj1b7LZQYQOG7e5w18fOfUH51PM')
bot = TeleBot(TOKEN)

OWNER_ID = 6090422473 

# MEDIA FILE_ID'LAR
VID_KIRA_FIRST_KILL = "BAACAgIAAxkBAAOgamOkYUl93OnEJUrtZU_gomJwFlMAAoqgAAL2HBlLgTO60GPr0hI9BA"
VID_L_CHECK = "BAACAgIAAxkBAAOeamOj_BZ7ATgL5IYqkqp_c8ttBG4AAoOgAAL2HBlL1DxA2BLMmCo9BA"
VID_NIGHT_SHINIGAMI = "BAACAgIAAxkBAAOkamOlVOl26MJFVUhfNHNi9rlGklEAAo6gAAL2HBlLZkqb-a1mXQg9BA"
GIF_DAY_START = "CgACAgIAAxkBAAOoamOutc6Wuf_8qZRR9P4Sa-Ma7-MAAuGgAAL2HBlLTIcoCecwxoY9BA"
GIF_L_DEATH = "CgACAgIAAxkBAAOqamOvVxow7dGO_DS5GKPmYcfbIRMAAuygAAL2HBlLfAQYGv77wJU9Bva"

# BAZA VA PROFIL TIZIMI
games = {}
user_data = {}

def get_user_profile(user_id, name="O'yinchi"):
    if user_id not in user_data:
        user_data[user_id] = {
            'name': name,
            'coins': 100,
            'wins': 0,
            'kills': 0,
            'inventory': [],
            'achievements': {'first_win': False, 'serial_killer': False}
        }
    user_data[user_id]['name'] = name
    return user_data[user_id]

# ================= ROLLARNI TAQSIMLASH =================
def assign_roles(players_dict):
    player_ids = list(players_dict.keys())
    random.shuffle(player_ids)
    
    roles = {}
    total = len(player_ids)
    
    roles[player_ids[0]] = "Kira"
    roles[player_ids[1]] = "L"
    if total >= 4: roles[player_ids[2]] = "Misa"
    if total >= 5: roles[player_ids[3]] = "Ryuk"
    if total >= 6: roles[player_ids[4]] = "Soichiro Yagami"
    if total >= 7: roles[player_ids[5]] = "Near"
    if total >= 8: roles[player_ids[6]] = "Mello"
        
    for p_id in player_ids:
        if p_id not in roles:
            roles[p_id] = "Matsuda (Politsiya)"
            
    return roles

# ================= KUN SIKLI (DAY) =================
def start_day(chat_id):
    game = games.get(chat_id)
    if not game or game.get('status') != 'night':
        return

    game['status'] = 'day'
    target_id = game.get('pending_kill')
    protected_id = game.get('protected_player')

    try:
        bot.send_animation(chat_id, GIF_DAY_START, caption="☀️ **Shahar ustiga quyosh chiqdi! Yangi kun boshlandi.**")
    except Exception:
        bot.send_message(chat_id, "☀️ Shahar ustiga quyosh chiqdi!")

    # Tundagi qurbonni aniqlash
    if target_id and target_id != protected_id:
        victim_name = game['players'].get(target_id, "Noma'lum")
        if target_id in game['alive']:
            game['alive'].remove(target_id)
        bot.send_message(chat_id, f"💀 **Aanchalik fojiali xabar!** Tunda {victim_name} halok bo'ldi...")
    else:
        bot.send_message(chat_id, "🛡 **Ajoyib xabar!** Bu kecha hech kim halok bo'lmadi.")

    # G'alaba shartlari
    kira_id = [p for p, r in game['roles'].items() if r == "Kira"]
    if kira_id and kira_id[0] not in game['alive']:
        bot.send_message(chat_id, "🎉 **G'ALABA!** Kira yo'q qilindi! Tinch aholi va L jamoasi yutdi!")
        games.pop(chat_id, None)
        return

    if len(game['alive']) <= 2:
        bot.send_message(chat_id, "📓 **G'ALABA!** Kira barcha raqiblarini yo'q qildi va yangi dunyo xudosiga aylandi!")
        games.pop(chat_id, None)
        return

    # Ovoz berish
    kb = types.InlineKeyboardMarkup(row_width=1)
    for p_id in game['alive']:
        p_name = game['players'][p_id]
        kb.add(types.InlineKeyboardButton(f"🗳 {p_name}ga ovoz berish", callback_data=f"vote_{chat_id}_{p_id}"))

    bot.send_message(chat_id, "🗣 **Muhokama va Ovoz berish vaqti!**\n\nSizningcha kim Kira? Ovoz bering:", reply_markup=kb)

# ================= TUN TAYMERI (30 SONIYA) =================
def night_timer(chat_id):
    time.sleep(30)
    start_day(chat_id)
        # ================= TUN SIKLI VA QOBILIYATLAR =================
def start_night(chat_id):
    game = games.get(chat_id)
    if not game:
        return

    game['status'] = 'night'
    game['protected_player'] = None
    game['pending_kill'] = None

    try:
        bot.send_video(chat_id, VID_NIGHT_SHINIGAMI, caption="🌙 **Shahar ustiga tun tushdi... Tun 30 soniya davom etadi!**")
    except Exception:
        bot.send_message(chat_id, "🌙 Shahar ustiga tun tushdi...")

    alive_players = game['alive']
    for player_id in alive_players:
        role = game['roles'].get(player_id)

        # 📓 KIRA QOBILIYATI (O'lim daftari)
        if role == "Kira":
            kb = types.InlineKeyboardMarkup(row_width=1)
            for t_id in alive_players:
                if t_id != player_id:
                    kb.add(types.InlineKeyboardButton(f"🗡 {game['players'][t_id]}ni o'ldirish", callback_data=f"target_{chat_id}_{t_id}"))
            try: bot.send_message(player_id, "📓 **Kira:** Qaysi o'yinchini O'lim Daftariga yozasiz?", reply_markup=kb)
            except Exception: pass

        # 🕵️‍♂️ L QOBILIYATI (Tergov qilish)
        elif role == "L" or (role == "Near" and not game.get('l_alive')):
            kb = types.InlineKeyboardMarkup(row_width=1)
            for t_id in alive_players:
                if t_id != player_id:
                    kb.add(types.InlineKeyboardButton(f"🔍 {game['players'][t_id]}ni shaxsiyatini tekshirish", callback_data=f"checkl_{chat_id}_{t_id}"))
            try: bot.send_message(player_id, "🕵️‍♂️ **L/Near:** Kimni Kira ekanligini tekshirmoqchisiz?", reply_markup=kb)
            except Exception: pass

        # 👁 MISA QOBILIYATI (Shinigami ko'zlari)
        elif role == "Misa":
            kb = types.InlineKeyboardMarkup(row_width=1)
            for t_id in alive_players:
                if t_id != player_id:
                    kb.add(types.InlineKeyboardButton(f"👁 {game['players'][t_id]}ning haqiqiy rolini ko'rish", callback_data=f"misaeyes_{chat_id}_{t_id}"))
            try: bot.send_message(player_id, "👁 **Misa Amane:** Umringiz yarmini berib kimning aniq rolini bilmoqchisiz?", reply_markup=kb)
            except Exception: pass

        # 👮‍♂️ SOICHIRO YAGAMI (Himoya)
        elif role == "Soichiro Yagami":
            kb = types.InlineKeyboardMarkup(row_width=1)
            for t_id in alive_players:
                kb.add(types.InlineKeyboardButton(f"🛡 {game['players'][t_id]}ni himoya qilish", callback_data=f"protect_{chat_id}_{t_id}"))
            try: bot.send_message(player_id, "👮‍♂️ **Soichiro:** Bugun kimni himoyaga olasiz?", reply_markup=kb)
            except Exception: pass

        # 🍎 RYUK QOBILIYATI (Kuzatish)
        elif role == "Ryuk":
            try: bot.send_message(player_id, "🍎 **Ryuk:** Siz neytral Shinigamisiz, shunchaki tunda o'yinni kuzatib rohatlaning!")
            except Exception: pass

    # Tun taymerini ishga tushirish (30s)
    threading.Thread(target=night_timer, args=(chat_id,), daemon=True).start()

# ================= TAYMER VA O'YINNI BOSHLASH =================
def auto_start_timer(chat_id):
    time.sleep(45)
    game = games.get(chat_id)
    if game and game.get('status') == 'waiting':
        if len(game.get('players', {})) >= 3:
            bot.send_message(chat_id, "⏰ **Vaqt tugadi! O'yin boshlanmoqda...**")
            start_game_logic(chat_id)
        else:
            bot.send_message(chat_id, "❌ Kamida 3 kishi kerak edi. O'yin bekor qilindi.")
            games.pop(chat_id, None)

def start_game_logic(chat_id):
    game = games.get(chat_id)
    if not game: return

    game['status'] = 'in_game'
    game['roles'] = assign_roles(game['players'])
    game['alive'] = list(game['players'].keys())
    game['l_alive'] = True

    bot.send_message(chat_id, "🎭 **Rollar taqsimlandi!** Har bir o'yinchiga shaxsiy chatida vazifasi yuborildi.")

    role_desc = {
        "Kira": "📓 **Kira:** Tunda O'lim Daftari orqali hammangizni yo'q qiling!",
        "L": "🕵️‍♂️ **L:** Tunda shubhalilarni tekshirib Kirani toping!",
        "Misa": "👁 **Misa:** Shinigami ko'zlari bilan rollarni ko'ring va Kiraga yordam bering!",
        "Ryuk": "🍎 **Ryuk:** Neytralsiz, olmacha yeb tomosha qiling!",
        "Soichiro Yagami": "👮‍♂️ **Soichiro:** Tunda bir o'yinchini himoya qiling!",
        "Near": "🧩 **Near:** L halok bo'lsa uning o'rnini egallaysiz!",
        "Mello": "🍫 **Mello:** Kiraga qarshi mustaqil tergov olib borasiz!"
    }

    for p_id, role in game['roles'].items():
        try: bot.send_message(p_id, role_desc.get(role, f"Sizning rolingiz: {role}"))
        except Exception: pass

    time.sleep(2)
    start_night(chat_id)

# ================= BUYRUQLAR =================
@bot.message_handler(commands=['start'])
def start_cmd(message):
    bot.reply_to(message, "👋 **Death Note Botiga xush kelibsiz!**\n\n🎮 `/create` — Guruhda o'yin yaratish\n🛒 `/shop` — Buyumlar do'koni\n🏆 `/top` — Eng kuchli o'yinchilar\n🎯 `/achievements` — Yutuqlar")

@bot.message_handler(commands=['addcoins'])
def add_coins_cmd(message):
    if message.from_user.id != OWNER_ID:
        bot.reply_to(message, "⛔ Bu buyruq faqat bot egasi uchun!")
        return
    try:
        args = message.text.split()
        target_id = int(args[1])
        amount = int(args[2])
        profile = get_user_profile(target_id)
        profile['coins'] += amount
        bot.reply_to(message, f"✅ `{target_id}` hisobiga **{amount} coin** qo'shildi! Yangi balans: **{profile['coins']}**")
    except Exception:
        bot.reply_to(message, "⚠️ Qoida: `/addcoins <user_id> <miqdor>`")

@bot.message_handler(commands=['top'])
def top_cmd(message):
    if not user_data:
        bot.reply_to(message, "🏆 Hali hech kim reytingda yo'q!")
        return
    sorted_users = sorted(user_data.values(), key=lambda x: x['wins'], reverse=True)[:10]
    text = "🏆 **TOP-10 O'yinchilar:**\n\n"
    for idx, u in enumerate(sorted_users, 1):
        text += f"{idx}. **{u['name']}** — 🏆 {u['wins']} g'alaba | 💰 {u['coins']} coin\n"
    bot.reply_to(message, text)

@bot.message_handler(commands=['shop'])
def shop_cmd(message):
    profile = get_user_profile(message.from_user.id, message.from_user.first_name)
    kb = types.InlineKeyboardMarkup(row_width=1)
    kb.add(
        types.InlineKeyboardButton("🍎 Ryuk Olmasi (30 coin)", callback_data="buy_apple"),
        types.InlineKeyboardButton("👁 Shinigami Ko'zlari (50 coin)", callback_data="buy_eyes")
    )
    inv = ', '.join(profile['inventory']) if profile['inventory'] else 'Bo\'sh'
    bot.reply_to(message, f"🛒 **Death Note Do'koni**\n\n💰 Balansingiz: **{profile['coins']} coin**\n🎒 Sumkangiz: {inv}", reply_markup=kb)

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
        'alive': []
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

    if action == "buy":
        item = data[1]
        profile = get_user_profile(call.from_user.id, call.from_user.first_name)
        if item == "apple" and profile['coins'] >= 30:
            profile['coins'] -= 30
            profile['inventory'].append("Ryuk Olmasi")
            bot.answer_callback_query(call.id, "🍎 Ryuk Olmasi xarid qilindi!", show_alert=True)
        elif item == "eyes" and profile['coins'] >= 50:
            profile['coins'] -= 50
            profile['inventory'].append("Shinigami Ko'zlari")
            bot.answer_callback_query(call.id, "👁 Shinigami Ko'zlari xarid qilindi!", show_alert=True)
        else:
            bot.answer_callback_query(call.id, "❌ Coin yetarli emas!", show_alert=True)

    elif action == "join":
        c_id = int(data[1])
        game = games.get(c_id)
        if game and game['status'] == 'waiting':
            if call.from_user.id not in game['players']:
                game['players'][call.from_user.id] = call.from_user.first_name
                get_user_profile(call.from_user.id, call.from_user.first_name)
                bot.answer_callback_query(call.id, "Qo'shildingiz!")

    elif action == "start":
        c_id = int(data[1])
        game = games.get(c_id)
        if game and game['status'] == 'waiting':
            if len(game['players']) >= 3:
                start_game_logic(c_id)
            else:
                bot.answer_callback_query(call.id, "Kamida 3 kishi kerak!", show_alert=True)

    elif action == "target":
        c_id, target_id = int(data[1]), int(data[2])
        game = games.get(c_id)
        if game:
            game['pending_kill'] = target_id
            if game['roles'].get(target_id) == "L":
                game['l_alive'] = False
            bot.answer_callback_query(call.id, "Ism O'lim daftariga yozildi!")
            bot.edit_message_text("📓 Qurbon ismi daftarga yozildi.", call.message.chat.id, call.message.message_id)

    elif action == "checkl":
        c_id, target_id = int(data[1]), int(data[2])
        game = games.get(c_id)
        if game:
            res = "HA (Kira!)" if game['roles'].get(target_id) == "Kira" else "YO'Q (Begunoh)"
            bot.answer_callback_query(call.id, f"Tergov natijasi: {res}", show_alert=True)

    elif action == "misaeyes":
        c_id, target_id = int(data[1]), int(data[2])
        game = games.get(c_id)
        if game:
            role = game['roles'].get(target_id, "Noma'lum")
            bot.answer_callback_query(call.id, f"👁 Ko'zlar natijasi: Uning roli — {role}", show_alert=True)

    elif action == "protect":
        c_id, target_id = int(data[1]), int(data[2])
        game = games.get(c_id)
        if game:
            game['protected_player'] = target_id
            bot.answer_callback_query(call.id, "Himoyaga olindi!")
            bot.edit_message_text("🛡 Tanlangan o'yinchi himoyalandi.", call.message.chat.id, call.message.message_id)

if __name__ == "__main__":
    threading.Thread(target=run_flask, daemon=True).start()
    bot.polling(none_stop=True)
                           
