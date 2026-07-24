import os
import random
import threading
import time
from flask import Flask
from telebot import TeleBot, types

# ================= FLASK SERVER =================
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

VID_NIGHT_SHINIGAMI = "BAACAgIAAxkBAAOkamOlVOl26MJFVUhfNHNi9rlGklEAAo6gAAL2HBlLZkqb-a1mXQg9BA"
GIF_DAY_START = "CgACAgIAAxkBAAOoamOutc6Wuf_8qZRR9P4Sa-Ma7-MAAuGgAAL2HBlLTIcoCecwxoY9BA"

games = {}
user_data = {}

def get_user_profile(user_id, name="O'yinchi"):
    if user_id not in user_data:
        user_data[user_id] = {'name': name, 'coins': 100, 'wins': 0, 'inventory': []}
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
    roles[player_ids[2]] = "Tinch Aholi"
    
    if total >= 4: roles[player_ids[3]] = "Naomi Misora" # Blocker
    if total >= 5: roles[player_ids[4]] = "Soichiro Yagami" # Protect + 2x Vote
    if total >= 6: roles[player_ids[5]] = "Misa" # Eyes
    if total >= 7: roles[player_ids[6]] = "Near" # Succession
    if total >= 8: roles[player_ids[7]] = "Ryuk" # Neutral
        
    for p_id in player_ids:
        if p_id not in roles:
            roles[p_id] = "Tinch Aholi"
            
    return roles

# ================= KUN SIKLI (DAY) =================
def start_day(chat_id):
    game = games.get(chat_id)
    if not game or game.get('status') != 'night':
        return

    game['status'] = 'day'
    target_id = game.get('pending_kill')
    protected_id = game.get('protected_player')
    blocked_id = game.get('blocked_player')

    try:
        bot.send_animation(chat_id, GIF_DAY_START, caption="☀️ **Shahar ustiga quyosh chiqdi! Yangi kun boshlandi.**")
    except Exception:
        bot.send_message(chat_id, "☀️ **Shahar ustiga quyosh chiqdi!**")

    # Kira bloklangan bo'lsa
    kira_id = [p for p, r in game['roles'].items() if r == "Kira"]
    is_kira_blocked = (kira_id and kira_id[0] == blocked_id)

    # Qurbonni e'lon qilish (Mantiqiy sir saqlanadi - yolg'on gapirishga sharoit)
    if target_id and target_id != protected_id and not is_kira_blocked:
        victim_name = game['players'].get(target_id, "Noma'lum")
        if target_id in game['alive']:
            game['alive'].remove(target_id)
            
            if game['roles'].get(target_id) == "L":
                game['l_alive'] = False
                bot.send_message(chat_id, f"💀 **Fojia!** L ({victim_name}) halok bo'ldi... Endi Near uning ishini davom ettiradi!")
            else:
                bot.send_message(chat_id, f"💀 **Fojia!** Tunda {victim_name} halok bo'ldi...")
    else:
        bot.send_message(chat_id, "🛡 **Ajoyib xabar!** Bu kecha shahar tinch bo'ldi, hech kim halok bo'lmadi.")

    # G'alaba shartlari
    if kira_id and kira_id[0] not in game['alive']:
        bot.send_message(chat_id, "🎉 **G'ALABA!** Kira yo'q qilindi! Tinch aholi va Tergovchilar yutdi!")
        games.pop(chat_id, None)
        return

    if len(game['alive']) <= 2:
        bot.send_message(chat_id, "📓 **G'ALABA!** Kira barcha raqiblarini yo'q qildi va Yangi Dunyo Xudosiga aylandi!")
        games.pop(chat_id, None)
        return

    # Ovoz berish tugmalari
    kb = types.InlineKeyboardMarkup(row_width=1)
    for p_id in game['alive']:
        p_name = game['players'][p_id]
        kb.add(types.InlineKeyboardButton(f"🗳 {p_name}ga ovoz berish", callback_data=f"vote_{chat_id}_{p_id}"))

    bot.send_message(chat_id, "🗣 **Muhokama va Ovoz berish vaqti!**\n\nSizningcha kim Kira? Ovoz bering:", reply_markup=kb)

def night_timer(chat_id):
    time.sleep(30)
    start_day(chat_id)
    # ================= TUN SIKLI VA BALANSLANGAN QOBILIYATLAR =================
def start_night(chat_id):
    game = games.get(chat_id)
    if not game: return

    game['status'] = 'night'
    game['night_count'] = game.get('night_count', 0) + 1
    game['pending_kill'] = None
    game['blocked_player'] = None
    game['last_protected'] = game.get('protected_player')
    game['protected_player'] = None

    try:
        bot.send_video(chat_id, VID_NIGHT_SHINIGAMI, caption=f"🌙 **Shahar ustiga {game['night_count']}-kecha tushdi... (30 soniya)**")
    except Exception:
        bot.send_message(chat_id, f"🌙 Shahar ustiga {game['night_count']}-kecha tushdi...")

    alive_players = game['alive']
    for player_id in alive_players:
        role = game['roles'].get(player_id)

        # 🛑 NAOMI MISORA (1-kecha taqiqi + max 2 marta limit)
        if role == "Naomi Misora":
            uses = game['naomi_uses'].get(player_id, 2)
            if game['night_count'] == 1:
                try: bot.send_message(player_id, "🛑 **Naomi Misora:** 1-kechada kuzatuv olib borilmaydi. Qobiliyatingiz 2-kechadan ochiladi!")
                except Exception: pass
            elif uses > 0:
                kb = types.InlineKeyboardMarkup(row_width=1)
                for t_id in alive_players:
                    if t_id != player_id:
                        kb.add(types.InlineKeyboardButton(f"🛑 {game['players'][t_id]}", callback_data=f"block_{chat_id}_{t_id}"))
                try: bot.send_message(player_id, f"🛑 **Naomi Misora:** Kimni bloklaysiz? (Qolgan limit: {uses})", reply_markup=kb)
                except Exception: pass
            else:
                try: bot.send_message(player_id, "🛑 Bloklash limitiz tugadi!")
                except Exception: pass

        # 📓 KIRA
        elif role == "Kira":
            kb = types.InlineKeyboardMarkup(row_width=1)
            for t_id in alive_players:
                if t_id != player_id:
                    kb.add(types.InlineKeyboardButton(f"🗡 {game['players'][t_id]}", callback_data=f"target_{chat_id}_{t_id}"))
            try: bot.send_message(player_id, "📓 **Kira:** Kimni O'lim Daftariga yozasiz?", reply_markup=kb)
            except Exception: pass

        # 🕵️‍♂️ L / NEAR
        elif role == "L" or (role == "Near" and not game.get('l_alive', True)):
            kb = types.InlineKeyboardMarkup(row_width=1)
            for t_id in alive_players:
                if t_id != player_id:
                    kb.add(types.InlineKeyboardButton(f"🔍 {game['players'][t_id]}", callback_data=f"checkl_{chat_id}_{t_id}"))
            r_name = "L" if role == "L" else "Near"
            try: bot.send_message(player_id, f"🕵️‍♂️ **{r_name}:** Kimni tekshirasiz?", reply_markup=kb)
            except Exception: pass

        # 👁 MISA (Limit: 2 marta)
        elif role == "Misa":
            uses = game['misa_uses'].get(player_id, 2)
            if uses > 0:
                kb = types.InlineKeyboardMarkup(row_width=1)
                for t_id in alive_players:
                    if t_id != player_id:
                        kb.add(types.InlineKeyboardButton(f"👁 {game['players'][t_id]}", callback_data=f"misaeyes_{chat_id}_{t_id}"))
                try: bot.send_message(player_id, f"👁 **Misa:** Kimning rolini ko'rasiz? (Qolgan limit: {uses})", reply_markup=kb)
                except Exception: pass

        # 👮‍♂️ SOICHIRO YAGAMI (Ketma-ket 1 kishini saqlamaydi)
        elif role == "Soichiro Yagami":
            kb = types.InlineKeyboardMarkup(row_width=1)
            for t_id in alive_players:
                if t_id != game.get('last_protected'):
                    kb.add(types.InlineKeyboardButton(f"🛡 {game['players'][t_id]}", callback_data=f"protect_{chat_id}_{t_id}"))
            try: bot.send_message(player_id, "👮‍♂️ **Soichiro:** Bugun kimni himoya qilasiz? (Kunduzi 2x Ovoz)", reply_markup=kb)
            except Exception: pass

        # 👤 TINCH AHOLI
        elif role == "Tinch Aholi":
            try: bot.send_message(player_id, "👤 **Tinch Aholi:** Tunda dam oling, kunduzi muhokamada Kirani toping!")
            except Exception: pass

    threading.Thread(target=night_timer, args=(chat_id,), daemon=True).start()

# ================= O'YINNI BOSHLASH =================
def auto_start_timer(chat_id):
    time.sleep(45)
    game = games.get(chat_id)
    if game and game.get('status') == 'waiting':
        if len(game.get('players', {})) >= 3:
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
    game['misa_uses'] = {}
    game['naomi_uses'] = {}
    game['l_alive'] = True
    game['night_count'] = 0

    bot.send_message(chat_id, "🎭 **Rollar taqsimlandi!** Har bir o'yinchiga shaxsiy chatida vazifasi yuborildi.")

    for p_id, role in game['roles'].items():
        if role == "Misa": game['misa_uses'][p_id] = 2
        if role == "Naomi Misora": game['naomi_uses'][p_id] = 2
        try: bot.send_message(p_id, f"🎭 Sizning rolingiz: **{role}**")
        except Exception: pass

    time.sleep(2)
    start_night(chat_id)

# ================= BUYRUQLAR =================
@bot.message_handler(commands=['start'])
def start_cmd(message):
    bot.reply_to(message, "👋 **Death Note Botiga xush kelibsiz!**\n\n🎮 `/create` — O'yin yaratish\n📖 `/info` — Rollar va Qoidalar\n🛒 `/shop` — Do'kon")

@bot.message_handler(commands=['info', 'help'])
def info_cmd(message):
    text = (
        "📖 **DEATH NOTE — BARCHA ROLLAR VA BALANS**\n\n"
        "• 📓 **Kira:** Tunda 1 kishini o'ldiradi.\n"
        "• 🕵️‍♂️ **L:** Tunda o'yinchini tekshiradi.\n"
        "• 🛑 **Naomi Misora:** Tunda 1 kishini bloklaydi (2-kechadan, limit 2 marta).\n"
        "• 👮‍♂️ **Soichiro:** Himoya qiladi (Kunduzi **2x Ovoz**).\n"
        "• 👁 **Misa:** 2 marta Shinigami ko'zlari bilan rolni ko'radi.\n"
        "• 🧩 **Near:** L o'lsa uning o'rnini egallaydi.\n"
        "• 👤 **Tinch Aholi:** Muhokamada Kirani ushlovchi fuqaro."
    )
    bot.reply_to(message, text)

@bot.message_handler(commands=['addcoins'])
def add_coins_cmd(message):
    if message.from_user.id != OWNER_ID: return
    try:
        args = message.text.split()
        profile = get_user_profile(int(args[1]))
        profile['coins'] += int(args[2])
        bot.reply_to(message, f"✅ `{args[1]}` hisobiga **{args[2]} coin** qo'shildi!")
    except Exception: pass

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

    if action == "join":
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

    elif action == "block":
        c_id, target_id = int(data[1]), int(data[2])
        game = games.get(c_id)
        if game:
            game['naomi_uses'][call.from_user.id] -= 1
            game['blocked_player'] = target_id
            bot.answer_callback_query(call.id, "Harakati bloklandi!")
            bot.edit_message_text("🛑 Tanlangan o'yinchi kuzatuvga olindi va bloklandi.", call.message.chat.id, call.message.message_id)

    elif action == "target":
        c_id, target_id = int(data[1]), int(data[2])
        game = games.get(c_id)
        if game:
            if game.get('blocked_player') == call.from_user.id:
                bot.answer_callback_query(call.id, "❌ Siz tunda kuzatuvdasiz, harakat qilolmayotganingizni sezdingiz!", show_alert=True)
            else:
                game['pending_kill'] = target_id
                bot.answer_callback_query(call.id, "Ism yozildi!")
                bot.edit_message_text("📓 Qurbon ismi daftarga yozildi.", call.message.chat.id, call.message.message_id)

    elif action == "checkl":
        c_id, target_id = int(data[1]), int(data[2])
        game = games.get(c_id)
        if game:
            if game.get('blocked_player') == call.from_user.id:
                bot.answer_callback_query(call.id, "❌ Siz tunda bloklangansiz, tekshira olmaysiz!", show_alert=True)
            else:
                res = "HA (Kira!)" if game['roles'].get(target_id) == "Kira" else "YO'Q (Begunoh)"
                bot.answer_callback_query(call.id, f"Natija: {res}", show_alert=True)

    elif action == "misaeyes":
        c_id, target_id = int(data[1]), int(data[2])
        game = games.get(c_id)
        if game:
            if game.get('blocked_player') == call.from_user.id:
                bot.answer_callback_query(call.id, "❌ Siz tunda bloklangansiz!", show_alert=True)
            else:
                game['misa_uses'][call.from_user.id] -= 1
                role = game['roles'].get(target_id, "Noma'lum")
                bot.answer_callback_query(call.id, f"👁 Uning roli: {role}", show_alert=True)
                bot.edit_message_text("👁 Ko'zlar ishlatildi.", call.message.chat.id, call.message.message_id)

    elif action == "protect":
        c_id, target_id = int(data[1]), int(data[2])
        game = games.get(c_id)
        if game:
            if game.get('blocked_player') == call.from_user.id:
                bot.answer_callback_query(call.id, "❌ Siz tunda bloklangansiz!", show_alert=True)
            else:
                game['protected_player'] = target_id
                bot.answer_callback_query(call.id, "Himoyalandi!")
                bot.edit_message_text("🛡 Tanlangan o'yinchi himoyalandi.", call.message.chat.id, call.message.message_id)

if __name__ == "__main__":
    threading.Thread(target=run_flask, daemon=True).start()
    bot.polling(none_stop=True)
                                                          
                           
