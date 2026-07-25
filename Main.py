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

# ================= BOT TOKENI VA CONFIG =================
TOKEN = os.environ.get('BOT_TOKEN', '8816866283:AAGJK1TXHj1b7LZQYQOG7e5w18fOfUH51PM')
bot = TeleBot(TOKEN)
OWNER_ID = 6090422473 

VID_NIGHT_SHINIGAMI = "BAACAgIAAxkBAAOkamOlVOl26MJFVUhfNHNi9rlGklEAAo6gAAL2HBlLZkqb-a1mXQg9BA"
GIF_DAY_START = "CgACAgIAAxkBAAOoamOutc6Wuf_8qZRR9P4Sa-Ma7-MAAuGgAAL2HBlLTIcoCecwxoY9BA"

games = {}
user_data = {}

# ================= USER PROFILE & DATA =================
def get_user_profile(user_id, name="O'yinchi"):
    if user_id not in user_data:
        user_data[user_id] = {
            'name': name,
            'coins': 100,
            'wins': 0,
            'games_played': 0,
            'last_daily': 0,
            'inventory': [],
            'achievements': [],
            'rank': "🌱 Novice"
        }
    user_data[user_id]['name'] = name
    update_user_rank(user_id)
    return user_data[user_id]

def update_user_rank(user_id):
    prof = user_data[user_id]
    wins = prof['wins']
    if wins >= 50: prof['rank'] = "☠️ Death God"
    elif wins >= 30: prof['rank'] = "🧠 Mastermind"
    elif wins >= 15: prof['rank'] = "🕵️‍♂️ Master Detective"
    elif wins >= 5: prof['rank'] = "🔍 Investigator"
    else: prof['rank'] = "🌱 Novice"

# ================= 10 TA ROL TAQSIMOTI =================
def assign_roles(players_dict):
    player_ids = list(players_dict.keys())
    random.shuffle(player_ids)
    
    roles = {}
    total = len(player_ids)
    
    role_pool = [
        "Kira", "L", "Naomi Misora", "Soichiro Yagami", 
        "Aizawa", "Misa", "Near", "Ryuk", "Kiyomi Takada"
    ]
    
    for i, p_id in enumerate(player_ids):
        if i < len(role_pool):
            roles[p_id] = role_pool[i]
        else:
            roles[p_id] = "Tinch Aholi"
            
    return roles

# ================= KUN SIKLI =================
def start_day(chat_id):
    game = games.get(chat_id)
    if not game or game.get('status') != 'night':
        return

    game['status'] = 'day'
    targets = game.get('pending_kills', [])
    protected_id = game.get('protected_player')
    blocked_id = game.get('blocked_player')

    try:
        bot.send_animation(chat_id, GIF_DAY_START, caption="☀️ **Shahar ustiga quyosh chiqdi! Yangi kun boshlandi.**")
    except Exception:
        bot.send_message(chat_id, "☀️ **Shahar ustiga quyosh chiqdi!**")

    kira_id = [p for p, r in game['roles'].items() if r == "Kira"]
    is_kira_blocked = (kira_id and kira_id[0] == blocked_id)

    dead_this_night = []
    if not is_kira_blocked and targets:
        for target_id in targets:
            if target_id != protected_id and target_id in game['alive']:
                game['alive'].remove(target_id)
                dead_this_night.append(target_id)
                victim_name = game['players'].get(target_id, "Noma'lum")
                victim_role = game['roles'].get(target_id, "Noma'lum")
                
                if victim_role == "L":
                    game['l_alive'] = False
                    bot.send_message(chat_id, f"💀 **FOJIA!** L ({victim_name}) tunda halok bo'ldi! Near endi uning ishini davom ettiradi!")
                else:
                    bot.send_message(chat_id, f"💀 **FOJIA!** Tunda {victim_name} ({victim_role}) halok bo'ldi...")

    if not dead_this_night:
        bot.send_message(chat_id, "🛡 **Ajoyib xabar!** Bu kecha shahar tinch bo'ldi, hech kim halok bo'lmadi.")

    # G'alaba tekshiruvi
    if kira_id and kira_id[0] not in game['alive']:
        bot.send_message(chat_id, "🎉 **G'ALABA!** Kira yo'q qilindi! Tergovchilar va Tinch aholi yutdi!\n💰 Tiriklarga +100 Coin berildi!")
        for p_id in game['alive']:
            prof = get_user_profile(p_id)
            prof['coins'] += 100
            prof['wins'] += 1
            if "🔍 Topuvchi" not in prof['achievements']:
                prof['achievements'].append("🔍 Topuvchi")
        games.pop(chat_id, None)
        return

    if len(game['alive']) <= 2:
        bot.send_message(chat_id, "📓 **G'ALABA VA MVP!** Kira barcha raqiblarini yo'q qildi!\n🏆 **MVP Kira** ga **+200 Coin** taqdim etildi!")
        if kira_id:
            prof = get_user_profile(kira_id[0])
            prof['coins'] += 200
            prof['wins'] += 1
            if "📓 Haqiqiy Kira" not in prof['achievements']:
                prof['achievements'].append("📓 Haqiqiy Kira")
        games.pop(chat_id, None)
        return

    # Ovoz berish tugmalari
    kb = types.InlineKeyboardMarkup(row_width=1)
    
    aizawa_id = [p for p, r in game['roles'].items() if r == "Aizawa"]
    if aizawa_id and aizawa_id[0] in game['alive'] and game['aizawa_shots'].get(aizawa_id[0], 0) < 2:
        kb.add(types.InlineKeyboardButton("💥 Aizawa: Otish (Limit 2x)", callback_data=f"aizawashot_menu_{chat_id}"))

    for p_id in game['alive']:
        p_name = game['players'][p_id]
        kb.add(types.InlineKeyboardButton(f"🗳 {p_name}ga ovoz berish", callback_data=f"vote_{chat_id}_{p_id}"))

    bot.send_message(chat_id, "🗣 **Muhokama va Ovoz berish vaqti! (30 soniya)**\n\nOvoz bering:", reply_markup=kb)
    threading.Thread(target=day_timer, args=(chat_id,), daemon=True).start()

def day_timer(chat_id):
    time.sleep(30)
    game = games.get(chat_id)
    if game and game.get('status') == 'day':
        start_night(chat_id)
            # ================= TUN SIKLI =================
def start_night(chat_id):
    game = games.get(chat_id)
    if not game: return

    game['status'] = 'night'
    game['night_count'] = game.get('night_count', 0) + 1
    game['pending_kills'] = []
    game['blocked_player'] = None
    game['protected_player'] = None

    try:
        bot.send_video(chat_id, VID_NIGHT_SHINIGAMI, caption=f"🌙 **Shahar ustiga {game['night_count']}-kecha tushdi... (30 soniya)**")
    except Exception:
        bot.send_message(chat_id, f"🌙 Shahar ustiga {game['night_count']}-kecha tushdi...")

    alive_players = game['alive']
    for player_id in alive_players:
        role = game['roles'].get(player_id)
        prof = get_user_profile(player_id)

        if role == "Kira":
            max_kills = 2 if "📓 Kira Daftari" in prof['inventory'] else 1
            kb = types.InlineKeyboardMarkup(row_width=1)
            for t_id in alive_players:
                if t_id != player_id:
                    kb.add(types.InlineKeyboardButton(f"🗡 {game['players'][t_id]}", callback_data=f"target_{chat_id}_{t_id}"))
            try: bot.send_message(player_id, f"📓 **Kira:** Kimni O'lim Daftariga yozasiz? (Maks: {max_kills} kishi)", reply_markup=kb)
            except Exception: pass

        elif role == "Kiyomi Takada":
            uses = game['takada_uses'].get(player_id, 3)
            if uses > 0:
                kb = types.InlineKeyboardMarkup(row_width=1)
                for t_id in alive_players:
                    if t_id != player_id:
                        kb.add(types.InlineKeyboardButton(f"🎭 {game['players'][t_id]} haqida soxta fakt", callback_data=f"fakefact_{chat_id}_{t_id}"))
                try: bot.send_message(player_id, f"🎭 **Kiyomi Takada:** Guruhni chalg'itish uchun kimga tuxmat qilasiz? (Qolgan limit: {uses})", reply_markup=kb)
                except Exception: pass

        elif role == "Naomi Misora":
            uses = game['naomi_uses'].get(player_id, 2)
            if game['night_count'] > 1 and uses > 0:
                kb = types.InlineKeyboardMarkup(row_width=1)
                for t_id in alive_players:
                    if t_id != player_id:
                        kb.add(types.InlineKeyboardButton(f"🛑 {game['players'][t_id]}", callback_data=f"block_{chat_id}_{t_id}"))
                try: bot.send_message(player_id, "🛑 **Naomi:** Kimni bloklaysiz?", reply_markup=kb)
                except Exception: pass

        elif role == "L" or (role == "Near" and not game.get('l_alive', True)):
            kb = types.InlineKeyboardMarkup(row_width=1)
            for t_id in alive_players:
                if t_id != player_id:
                    kb.add(types.InlineKeyboardButton(f"🔍 {game['players'][t_id]}", callback_data=f"checkl_{chat_id}_{t_id}"))
            try: bot.send_message(player_id, "🕵️‍♂️ **Tergovchi:** Kimni tekshirasiz?", reply_markup=kb)
            except Exception: pass

        elif role == "Soichiro Yagami":
            kb = types.InlineKeyboardMarkup(row_width=1)
            for t_id in alive_players:
                kb.add(types.InlineKeyboardButton(f"🛡 {game['players'][t_id]}", callback_data=f"protect_{chat_id}_{t_id}"))
            try: bot.send_message(player_id, "👮‍♂️ **Soichiro:** Kimni himoya qilasiz?", reply_markup=kb)
            except Exception: pass

    threading.Thread(target=night_timer, args=(chat_id,), daemon=True).start()

def night_timer(chat_id):
    time.sleep(30)
    start_day(chat_id)

# ================= O'YINNI BOSHLASH & TAYMER =================
def auto_start_timer(chat_id, wait_time=45):
    time.sleep(wait_time)
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
    game['naomi_uses'] = {}
    game['takada_uses'] = {}
    game['aizawa_shots'] = {}
    game['l_alive'] = True
    game['night_count'] = 0

    bot.send_message(chat_id, "🎭 **Rollar taqsimlandi!** Har bir o'yinchiga shaxsiy chatida roli yuborildi.")

    for p_id, role in game['roles'].items():
        prof = get_user_profile(p_id)
        prof['games_played'] += 1
        prof['coins'] += 10 # Har 1 raund o'ynagani uchun
        
        if role == "Naomi Misora": game['naomi_uses'][p_id] = 2
        if role == "Kiyomi Takada": game['takada_uses'][p_id] = 3
        if role == "Aizawa": game['aizawa_shots'][p_id] = 0
        try: bot.send_message(p_id, f"🎭 Sizning rolingiz: **{role}**\nSizning Unvoningiz: {prof['rank']}")
        except Exception: pass

    time.sleep(2)
    start_night(chat_id)

# ================= BUYRUQLAR (COMMANDS) =================
@bot.message_handler(commands=['start'])
def start_cmd(message):
    bot.reply_to(message, "👋 **Death Note Botiga xush kelibsiz!**\n\n🎮 `/create` — O'yin Yaratish\n🛑 `/stop` — O'yinni Bekor Qilish\n⏳ `/extend` — Kutish Vaqtini Uzaytirish\n👤 `/profile` — Profil va Unvon\n🛒 `/shop` — Do'kon (1000 Coin)\n🏆 `/top` — Top-10 Reyting\n🎁 `/daily` — Kunlik Bonus")

@bot.message_handler(commands=['daily'])
def daily_cmd(message):
    prof = get_user_profile(message.from_user.id, message.from_user.first_name)
    now = time.time()
    if now - prof['last_daily'] >= 86400:
        prof['coins'] += 100
        prof['last_daily'] = now
        bot.reply_to(message, "🎁 **Kunlik bonus!** Hisobingizga **+100 Coin** qo'shildi!")
    else:
        rem = int((86400 - (now - prof['last_daily'])) // 3600)
        bot.reply_to(message, f"⏱ Keyingi bonusni **{rem} soatdan** keyin olishingiz mumkin.")

@bot.message_handler(commands=['top'])
def top_cmd(message):
    sorted_users = sorted(user_data.items(), key=lambda x: x[1]['wins'], reverse=True)[:10]
    text = "🏆 **DEATH NOTE TOP-10 O'YINCHILAR**\n\n"
    for i, (u_id, u_info) in enumerate(sorted_users, 1):
        text += f"{i}. {u_info['rank']} **{u_info['name']}** — {u_info['wins']} g'alaba\n"
    bot.reply_to(message, text)

@bot.message_handler(commands=['shop'])
def shop_cmd(message):
    kb = types.InlineKeyboardMarkup()
    kb.add(types.InlineKeyboardButton("👁 Shinigami Ko'zlari (1000 coin)", callback_data="buy_eyes"))
    kb.add(types.InlineKeyboardButton("🍎 Shinigami Olmasi / Himoya (1000 coin)", callback_data="buy_apple"))
    kb.add(types.InlineKeyboardButton("📓 Kira Daftari / 2x Kill (1000 coin)", callback_data="buy_notebook"))
    bot.reply_to(message, "🛒 **DEATH NOTE DO'KONI (Barchasi 1000 Coin):**", reply_markup=kb)

@bot.message_handler(commands=['profile', 'achievements'])
def profile_cmd(message):
    prof = get_user_profile(message.from_user.id, message.from_user.first_name)
    achs = "\n• ".join(prof['achievements']) if prof['achievements'] else "Yo'q"
    inv = ", ".join(prof['inventory']) if prof['inventory'] else "Bo'sh"
    
    text = (
        f"👤 **PROFIL: {prof['rank']} {prof['name']}**\n\n"
        f"💰 **Coinlar:** {prof['coins']} coin\n"
        f"🏆 **G'alabalar:** {prof['wins']}\n"
        f"🎮 **O'yinlar:** {prof['games_played']}\n"
        f"🎒 **Inventar:** {inv}\n\n"
        f"🎖 **YUTUQLAR (ACHIEVEMENTS):**\n• {achs}"
    )
    bot.reply_to(message, text)

@bot.message_handler(commands=['stop'])
def stop_cmd(message):
    chat_id = message.chat.id
    if chat_id in games:
        games.pop(chat_id, None)
        bot.reply_to(message, "🛑 **O'yin to'xtatildi va bekor qilindi.**")
    else:
        bot.reply_to(message, "⚠️ Faol o'yin yo'q.")

@bot.message_handler(commands=['extend'])
def extend_cmd(message):
    chat_id = message.chat.id
    game = games.get(chat_id)
    if game and game['status'] == 'waiting':
        threading.Thread(target=auto_start_timer, args=(chat_id, 30), daemon=True).start()
        bot.reply_to(message, "⏳ **Kutish vaqti yana +30 soniyaga uzaytirildi!**")

@bot.message_handler(commands=['create'])
def create_game_command(message):
    chat_id = message.chat.id
    if chat_id in games:
        bot.reply_to(message, "⚠️ Guruhda allaqachon o'yin ketmoqda!")
        return
    games[chat_id] = {
        'status': 'waiting',
        'players': {message.from_user.id: message.from_user.first_name},
        'roles': {},
        'alive': []
    }
    kb = types.InlineKeyboardMarkup()
    kb.add(types.InlineKeyboardButton("✋ Qo'shilish", callback_data=f"join_{chat_id}"))
    kb.add(types.InlineKeyboardButton("🚀 Boshlash", callback_data=f"start_{chat_id}"))

    bot.send_message(chat_id, f"🎮 **Death Note O'yini Yaratildi!**\n\n45 soniya ichida qo'shiling!", reply_markup=kb)
    threading.Thread(target=auto_start_timer, args=(chat_id, 45), daemon=True).start()

# ================= CALLBACK HANDLERLAR =================
@bot.callback_query_handler(func=lambda call: True)
def callback_inline(call):
    data = call.data.split("_")
    action = data[0]

    if action == "buy":
        item = data[1]
        prof = get_user_profile(call.from_user.id, call.from_user.first_name)
        if prof['coins'] >= 1000:
            if item == "eyes": prof['inventory'].append("👁 Shinigami Ko'zlari")
            elif item == "apple": prof['inventory'].append("🍎 Shinigami Olmasi")
            elif item == "notebook": prof['inventory'].append("📓 Kira Daftari")
            prof['coins'] -= 1000
            bot.answer_callback_query(call.id, "✅ Xarid qilindi!", show_alert=True)
        else:
            bot.answer_callback_query(call.id, "❌ 1000 Coin yetarli emas!", show_alert=True)

    elif action == "fakefact":
        c_id, target_id = int(data[1]), int(data[2])
        game = games.get(c_id)
        if game:
            game['takada_uses'][call.from_user.id] -= 1
            t_name = game['players'][target_id]
            facts = [
                f"🚨 **SHUBHALI FAKT:** Men {t_name} tunda O'lim Daftari ushlab turgganini ko'rdim!",
                f"🚨 **SHUBHALI FAKT:** {t_name} kecha Soichiro bilan yashirincha gaplashayotgan edi, u L bo'lishi mumkin!",
                f"🚨 **SHUBHALI FAKT:** {t_name}ning harakatlari mutlaqo Kiraga o'xshaydi, uni darhol otish kerak!"
            ]
            bot.send_message(c_id, random.choice(facts))
            bot.answer_callback_query(call.id, "Tuxmat guruhga tashlandi!")

    elif action == "aizawashot":
        if data[1] == "menu":
            c_id = int(data[2])
            game = games.get(c_id)
            if game and game['roles'].get(call.from_user.id) == "Aizawa":
                kb = types.InlineKeyboardMarkup(row_width=1)
                for t_id in game['alive']:
                    if t_id != call.from_user.id:
                        kb.add(types.InlineKeyboardButton(f"💥 {game['players'][t_id]}ni otish", callback_data=f"aizawashot_exec_{c_id}_{t_id}"))
                bot.send_message(call.from_user.id, "💥 **Aizawa:** Kimni otib tashlaysiz?", reply_markup=kb)

        elif data[1] == "exec":
            c_id, target_id = int(data[2]), int(data[3])
            game = games.get(c_id)
            if game and game['roles'].get(call.from_user.id) == "Aizawa":
                game['aizawa_shots'][call.from_user.id] += 1
                shooter = game['players'][call.from_user.id]
                victim = game['players'][target_id]
                
                if game['roles'].get(target_id) == "Kira":
                    game['alive'].remove(target_id)
                    bot.send_message(c_id, f"💥 **Aizawa ({shooter})** {victim}ni otdi va u **KIRA** edi!")
                else:
                    game['alive'].remove(target_id)
                    game['alive'].remove(call.from_user.id)
                    bot.send_message(c_id, f"💥 **Aizawa ({shooter})** begunoh {victim}ni otib qo'ydi va **o'zi ham halok bo'ldi!**")

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

    elif action == "target":
        c_id, target_id = int(data[1]), int(data[2])
        game = games.get(c_id)
        if game:
            game['pending_kills'].append(target_id)
            bot.answer_callback_query(call.id, "Ism yozildi!")

if __name__ == "__main__":
    threading.Thread(target=run_flask, daemon=True).start()
    bot.polling(none_stop=True)
        
