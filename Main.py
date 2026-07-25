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

# Media fayllar va resurslar
VID_NIGHT_SHINIGAMI = "BAACAgIAAxkBAAOkamOlVOl26MJFVUhfNHNi9rlGklEAAo6gAAL2HBlLZkqb-a1mXQg9BA"
GIF_DAY_START = "CgACAgIAAxkBAAOoamOutc6Wuf_8qZRR9P4Sa-Ma7-MAAuGgAAL2HBlLTIcoCecwxoY9BA"
VID_KIRA_WIN = "BAACAgIAAxkBAAOcamOjlGxvF-sQRjpGhOMss5BoRJAAAn6gAAL2HBlL9YoV8W6jmtU9BA"
VID_L_INVESTIGATE = "BAACAgIAAxkBAAOeamOj_BZ7ATgL5IYqkqp_c8ttBG4AAoOgAAL2HBlL1DxA2BLMmCo9BA"
VID_KIRA_FIRST_KILL = "BAACAgIAAxkBAAOgamOkYUl93OnEJUrtZU_gomJwFlMAAoqgAAL2HBlLgTO60GPr0hI9BA"
VID_L_WIN = "BAACAgIAAxkBAAOiamOk543jPQXByEQZxEIcamNciz4AAoygAAL2HBlLHjkU3rpfDRY9BA"
GIF_KIRA_DIES = "CgACAgIAAxkBAAOmamOtjuILC7y_gntablguan3uETAAAtKgAAL2HBlLRYDNDMWd9So9BA"
GIF_L_DIES = "CgACAgIAAxkBAAOqamOvVxow7dGO_DS5GKPmYcfbIRMAAuygAAL2HBlLfAQYGv77wJU9BA"

IMG_GAME_START = "assets/game_start.jpg"

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

# ================= ROLLAR TAQSIMOTI =================
def assign_roles(players_dict):
    player_ids = list(players_dict.keys())
    random.shuffle(player_ids)

    roles = {}
    role_pool = [
        "Kira", "L", "Naomi Misora", "Soichiro Yagami",
        "Aizawa", "Misa", "Near", "Ryuk", "Kiyomi Takada", "Mello", "Teru Mikami", "Matsuda"
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
    game['votes'] = {}
    targets = game.get('pending_kills', [])
    protected_id = game.get('protected_player')
    blocked_id = game.get('blocked_player')

    try:
        bot.send_animation(chat_id, GIF_DAY_START, caption="☀️ **Shahar ustiga quyosh chiqdi! Yangi kun boshlandi.**")
    except Exception:
        bot.send_message(chat_id, "☀️ **Shahar ustiga quyosh chiqdi! Yangi kun boshlandi.**")

    if game.get('ryuk_event'):
        bot.send_message(chat_id, game['ryuk_event'])
        game['ryuk_event'] = None

    kira_id = [p for p, r in game['roles'].items() if r == "Kira"]
    is_kira_blocked = (kira_id and kira_id[0] == blocked_id)

    dead_this_night = []
    if not is_kira_blocked and targets:
        for target_id in targets:
            # SHINIGAMI OLMASI TEKSHIRUVI (1 martalik himoya)
            target_prof = get_user_profile(target_id)
            if "🍎 Shinigami Olmasi" in target_prof['inventory'] and target_id != protected_id:
                target_prof['inventory'].remove("🍎 Shinigami Olmasi")
                bot.send_message(chat_id, f"🍎 **{game['players'].get(target_id)}** do'kondagi Shinigami Olmasi tufayli bu kecha o'limdan eson-omon qutulib qoldi!")
                continue

            if target_id != protected_id and target_id in game['alive']:
                game['alive'].remove(target_id)
                dead_this_night.append(target_id)
                victim_name = game['players'].get(target_id, "Noma'lum")
                victim_role = game['roles'].get(target_id, "Noma'lum")

                if victim_role == "L":
                    game['l_alive'] = False
                    try:
                        bot.send_animation(chat_id, GIF_L_DIES, caption=f"💀 **FOJIA!** L ({victim_name}) tunda halok bo'ldi! Near endi uning ishini davom ettiradi!")
                    except Exception:
                        bot.send_message(chat_id, f"💀 **FOJIA!** L ({victim_name}) tunda halok bo'ldi! Near endi uning ishini davom ettiradi!")
                else:
                    bot.send_message(chat_id, f"💀 **FOJIA!** Tunda {victim_name} ({victim_role}) halok bo'ldi...")

        if dead_this_night and not game.get('kira_first_kill_shown'):
            game['kira_first_kill_shown'] = True
            try:
                bot.send_video(chat_id, VID_KIRA_FIRST_KILL, caption="📓 **Kira birinchi qurbonini O'lim Daftariga yozdi...**")
            except Exception:
                pass

    if not dead_this_night:
        bot.send_message(chat_id, "🛡 **Ajoyib xabar!** Bu kecha shahar tinch bo'ldi, hech kim halok bo'lmadi.")

    if kira_id and kira_id[0] not in game['alive']:
        mikami_id = [p for p, r in game['roles'].items() if r == "Teru Mikami" and p in game['alive']]
        if mikami_id and not game.get('mikami_used', False):
            game['mikami_used'] = True
            game['roles'][mikami_id[0]] = "Kira"
            kira_id = mikami_id
            try:
                bot.send_message(chat_id, "📜 **KUTILMAGAN BURILISH!** Asl Kira yo'q qilindi... ammo O'lim Daftari maxfiy davomchisiga o'tdi! Kira ruhi shahar ustida hali ham yashaydi...")
            except Exception:
                pass
            try:
                bot.send_message(mikami_id[0], "📜 **Siz — Teru Mikami edingiz.** Asl Kira yo'q qilindi, endi O'lim Daftari sizga o'tdi. Siz endigi **yangi Kira**siz — tungi hujum imkoniyatingiz keyingi kechadan boshlanadi!")
            except Exception:
                pass
        else:
            try:
                bot.send_animation(chat_id, GIF_KIRA_DIES, caption="📓 **Kira daftari yondirildi...**")
            except Exception:
                pass
            try:
                bot.send_video(chat_id, VID_L_WIN, caption="🎉 **G'ALABA!** Kira yo'q qilindi! Tergovchilar va Tinch aholi yutdi!\n💰 Tiriklarga +25 Coin berildi!")
            except Exception:
                bot.send_message(chat_id, "🎉 **G'ALABA!** Kira yo'q qilindi! Tergovchilar va Tinch aholi yutdi!\n💰 Tiriklarga +25 Coin berildi!")
            for p_id in game['alive']:
                prof = get_user_profile(p_id)
                prof['coins'] += 25
                prof['wins'] += 1
                if "🔍 Topuvchi" not in prof['achievements']:
                    prof['achievements'].append("🔍 Topuvchi")
            games.pop(chat_id, None)
            return

    if len(game['alive']) <= 2:
        try:
            bot.send_video(chat_id, VID_KIRA_WIN, caption="📓 **G'ALABA VA MVP!** Kira barcha raqiblarini yo'q qildi!\n🏆 **MVP Kira** ga **+200 Coin** taqdim etildi!")
        except Exception:
            bot.send_message(chat_id, "📓 **G'ALABA VA MVP!** Kira barcha raqiblarini yo'q qildi!\n🏆 **MVP Kira** ga **+200 Coin** taqdim etildi!")
        if kira_id:
            prof = get_user_profile(kira_id[0])
            prof['coins'] += 200
            prof['wins'] += 1
            if "📓 Haqiqiy Kira" not in prof['achievements']:
                prof['achievements'].append("📓 Haqiqiy Kira")
        games.pop(chat_id, None)
        return

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
        votes = game.get('votes', {})
        if votes:
            weighted_votes = []
            for voter_id, t_id in votes.items():
                weight = 2 if game['roles'].get(voter_id) == "Matsuda" else 1
                weighted_votes.extend([t_id] * weight)
            voted_target = max(set(weighted_votes), key=weighted_votes.count)
            if voted_target in game['alive']:
                game['alive'].remove(voted_target)
                v_name = game['players'][voted_target]
                v_role = game['roles'][voted_target]
                bot.send_message(chat_id, f"⚖️ **Ovoz berish natijasida** {v_name} ({v_role}) qatl etildi!")
        else:
            bot.send_message(chat_id, "🗣 Bu safar hech kimga etarli ovoz berilmadi.")

        time.sleep(2)
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
        bot.send_message(chat_id, f"🌙 Shahar ustiga {game['night_count']}-kecha tushdi... (30 soniya)")

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
            try: bot.send_message(player_id, f"📓 **Kira:** Kimni O'lim Daftariga yozasiz? (Qolgan o'ldirish limiti: {max_kills})", reply_markup=kb)
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
            if uses > 0:
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

        elif role == "Misa":
            uses = game['misa_uses'].get(player_id, 0)
            has_eyes = "👁 Shinigami Ko'zlari" in prof['inventory']
            if uses > 0 or has_eyes:
                kb = types.InlineKeyboardMarkup(row_width=1)
                for t_id in alive_players:
                    if t_id != player_id:
                        kb.add(types.InlineKeyboardButton(f"👁 {game['players'][t_id]}", callback_data=f"misaeyes_{chat_id}_{t_id}"))
                try: bot.send_message(player_id, f"👁 **Misa (Shinigami Ko'zi):** Kimning aniq rolini ko'rmoqchisiz?", reply_markup=kb)
                except Exception: pass

        elif role == "Mello":
            if not game['mello_used'].get(player_id, False):
                kb = types.InlineKeyboardMarkup(row_width=1)
                for t_id in alive_players:
                    if t_id != player_id:
                        kb.add(types.InlineKeyboardButton(f"🔥 {game['players'][t_id]}", callback_data=f"melloattack_{chat_id}_{t_id}"))
                try: bot.send_message(player_id, "🔥 **Mello:** Tavakkal qilib kimga xujum qilasiz? (Faqat 1 marta, butun o'yin davomida)", reply_markup=kb)
                except Exception: pass

        elif role == "Ryuk":
            lucky_id = random.choice(alive_players)
            delta = random.choice([20, -20])
            l_prof = get_user_profile(lucky_id)
            l_prof['coins'] = max(0, l_prof['coins'] + delta)
            l_name = game['players'][lucky_id]
            if delta > 0:
                game['ryuk_event'] = f"🍎 **Ryuk zerikib olma bilan qimor o'ynadi...** {l_name} kutilmaganda **+{delta} Coin** yutib oldi!"
            else:
                game['ryuk_event'] = f"🍎 **Ryuk zerikib olma bilan qimor o'ynadi...** {l_name} omadsizlikka uchrab **{delta} Coin** yutqazdi!"

    threading.Thread(target=night_timer, args=(chat_id,), daemon=True).start()

def night_timer(chat_id):
    time.sleep(30)
    start_day(chat_id)

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
    game['misa_uses'] = {}
    game['mello_used'] = {}
    game['mikami_used'] = False
    game['secret_msgs_used'] = 0
    game['l_alive'] = True
    game['night_count'] = 0

    bot.send_message(chat_id, "🎭 **Rollar taqsimlandi!** Har bir o'yinchiga shaxsiy chatida roli yuborildi.")

    for p_id, role in game['roles'].items():
        prof = get_user_profile(p_id)
        prof['games_played'] += 1
        prof['coins'] += 15
        if prof['games_played'] % 5 == 0:
            prof['coins'] += 50
            try: bot.send_message(p_id, "🎯 **Bonus!** 5-raundda ishtirok etganingiz uchun **+50 Coin**!")
            except Exception: pass

        if role == "Naomi Misora": game['naomi_uses'][p_id] = 2
        if role == "Kiyomi Takada": game['takada_uses'][p_id] = 3
        if role == "Aizawa": game['aizawa_shots'][p_id] = 0
        if role == "Misa": game['misa_uses'][p_id] = 3
        if role == "Mello": game['mello_used'][p_id] = False
        try: bot.send_message(p_id, f"🎭 Sizning rolingiz: **{role}**\nSizning Unvoningiz: {prof['rank']}")
        except Exception: pass

    time.sleep(2)
    start_night(chat_id)
            # ================= BUYRUQLAR (COMMANDS) =================
@bot.message_handler(commands=['start'])
def start_cmd(message):
    bot.reply_to(message, "👋 **Death Note Botiga xush kelibsiz!**\n\n🎮 `/create` — O'yin Yaratish\n🛑 `/stop` — O'yinni Bekor Qilish\n⏳ `/extend` — Kutish Vaqtini Uzaytirish\n👤 `/profile` — Profil va Unvon\n🛒 `/shop` — Do'kon (1000 Coin)\n🏆 `/top` — Top-10 Reyting\n🎁 `/daily` — Kunlik Bonus\n🔒 `/maxfiy` — (Faqat Kira/Misa, shaxsiy chatda) Maxfiy xabar")

@bot.message_handler(commands=['addcoin'])
def addcoin_cmd(message):
    if message.from_user.id != OWNER_ID:
        bot.reply_to(message, "❌ Bu buyruq faqat bot egasiga tegishli!")
        return

    try:
        parts = message.text.split()
        if len(parts) == 2:
            amount = int(parts[1])
            u_id = message.from_user.id
        elif len(parts) >= 3:
            u_id = int(parts[1])
            amount = int(parts[2])
        else:
            bot.reply_to(message, "⚠️ Format: `/addcoin USER_ID AMOUNT` yoki `/addcoin AMOUNT`")
            return

        prof = get_user_profile(u_id)
        prof['coins'] += amount
        bot.reply_to(message, f"✅ **{u_id}** ga **+{amount} Coin** qo'shildi!\nHozirgi balansi: {prof['coins']} coin.")
    except Exception:
        bot.reply_to(message, "⚠️ Format: `/addcoin USER_ID AMOUNT`")

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
    kb.add(types.InlineKeyboardButton("👁 Shinigami Ko'zlari (1000 coin) - 1x", callback_data="buy_eyes"))
    kb.add(types.InlineKeyboardButton("🍎 Shinigami Olmasi / Himoya (1000 coin) - 1x", callback_data="buy_apple"))
    kb.add(types.InlineKeyboardButton("📓 Kira Daftari / 2x Kill (1000 coin) - 1x", callback_data="buy_notebook"))
    bot.reply_to(message, "🛒 **DEATH NOTE DO'KONI (Barchasi 1000 Coin, 1-martalik):**", reply_markup=kb)

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
        f"🎒 **Inventar (1-martalik):** {inv}\n\n"
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

@bot.message_handler(commands=['maxfiy'])
def secret_cmd(message):
    if message.chat.type != 'private':
        return
    sender_id = message.from_user.id
    text = message.text.replace('/maxfiy', '', 1).strip()
    if not text:
        bot.reply_to(message, "⚠️ Format: `/maxfiy xabar matni`")
        return

    for g in games.values():
        if sender_id in g.get('alive', []) and g['roles'].get(sender_id) in ("Kira", "Misa"):
            if g.get('secret_msgs_used', 0) >= 6:
                bot.reply_to(message, "❌ Maxfiy aloqa limiti tugadi (jami 6 marta).")
                return
            other_role = "Misa" if g['roles'].get(sender_id) == "Kira" else "Kira"
            other_id = next((p for p, r in g['roles'].items() if r == other_role and p in g['alive']), None)
            if other_id:
                try:
                    bot.send_message(other_id, f"🔒 **Maxfiy xabar:** {text}")
                    g['secret_msgs_used'] = g.get('secret_msgs_used', 0) + 1
                    bot.reply_to(message, f"✅ Xabar maxfiy yuborildi. (Qolgan limit: {6 - g['secret_msgs_used']})")
                except Exception:
                    bot.reply_to(message, "⚠️ Xabar yetkazilmadi.")
            else:
                bot.reply_to(message, "⚠️ Hamkoringiz topilmadi (o'lgan yoki mavjud emas).")
            return

    bot.reply_to(message, "⚠️ Siz hozir Kira yoki Misa rolida faol o'yinda emassiz.")

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

    try:
        with open(IMG_GAME_START, 'rb') as photo:
            bot.send_photo(chat_id, photo, caption="🎮 **Death Note O'yini Yaratildi!**\n\n45 soniya ichida qo'shiling!", reply_markup=kb)
    except Exception:
        bot.send_message(chat_id, "🎮 **Death Note O'yini Yaratildi!**\n\n45 soniya ichida qo'shiling!", reply_markup=kb)
    threading.Thread(target=auto_start_timer, args=(chat_id, 45), daemon=True).start()

# ================= CALLBACK HANDLERLAR =================
@bot.callback_query_handler(func=lambda call: True)
def callback_inline(call):
    data = call.data.split("_")
    action = data[0]

    if action == "vote":
        c_id, target_id = int(data[1]), int(data[2])
        game = games.get(c_id)
        if game and game['status'] == 'day':
            game['votes'][call.from_user.id] = target_id
            bot.answer_callback_query(call.id, "Ovozingiz qabul qilindi!")

    elif action == "checkl":
        c_id, target_id = int(data[1]), int(data[2])
        game = games.get(c_id)
        if game:
            t_role = game['roles'].get(target_id, "Tinch Aholi")
            res = "KIRA!" if t_role == "Kira" else "Kira EMAS."
            bot.answer_callback_query(call.id, f"Natija: Bu o'yinchi {res}", show_alert=True)
            try:
                bot.send_video(call.from_user.id, VID_L_INVESTIGATE, caption=f"🕵️‍♂️ **Tergov natijasi:** {res}")
            except Exception:
                pass

    elif action == "protect":
        c_id, target_id = int(data[1]), int(data[2])
        game = games.get(c_id)
        if game:
            game['protected_player'] = target_id
            bot.answer_callback_query(call.id, "Himoyalandi!")

    elif action == "misaeyes":
        c_id, target_id = int(data[1]), int(data[2])
        game = games.get(c_id)
        if game:
            prof = get_user_profile(call.from_user.id)
            if game['misa_uses'].get(call.from_user.id, 0) > 0:
                game['misa_uses'][call.from_user.id] -= 1
            elif "👁 Shinigami Ko'zlari" in prof['inventory']:
                prof['inventory'].remove("👁 Shinigami Ko'zlari") # 1 MARTALIK BUYUM ISHLATILDI
            t_role = game['roles'].get(target_id, "Noma'lum")
            t_name = game['players'].get(target_id, "Noma'lum")
            bot.answer_callback_query(call.id, f"👁 {t_name} — roli: {t_role}", show_alert=True)

    elif action == "melloattack":
        c_id, target_id = int(data[1]), int(data[2])
        game = games.get(c_id)
        if game and not game['mello_used'].get(call.from_user.id, False):
            game['mello_used'][call.from_user.id] = True
            if target_id in game['alive']:
                game['alive'].remove(target_id)
                t_name = game['players'].get(target_id, "Noma'lum")
                t_role = game['roles'].get(target_id, "Noma'lum")
                if t_role == "Kira":
                    bot.send_message(c_id, f"🔥 **Mello** tavakkal qildi va {t_name}ga xujum qildi — u aynan **KIRA** edi! 🎯")
                    prof = get_user_profile(call.from_user.id)
                    prof['coins'] += 150
                    if "🔥 Xavfli O'yinchi" not in prof['achievements']:
                        prof['achievements'].append("🔥 Xavfli O'yinchi")
                else:
                    bot.send_message(c_id, f"🔥 **Mello** tavakkal qildi va begunoh {t_name} ({t_role})ga xujum qildi...")
            bot.answer_callback_query(call.id, "Hujum amalga oshirildi!")

    elif action == "block":
        c_id, target_id = int(data[1]), int(data[2])
        game = games.get(c_id)
        if game:
            game['blocked_player'] = target_id
            bot.answer_callback_query(call.id, "Bloklandi!")

    elif action == "buy":
        item = data[1]
        prof = get_user_profile(call.from_user.id, call.from_user.first_name)
        if prof['coins'] >= 1000:
            if item == "eyes": prof['inventory'].append("👁 Shinigami Ko'zlari")
            elif item == "apple": prof['inventory'].append("🍎 Shinigami Olmasi")
            elif item == "notebook": prof['inventory'].append("📓 Kira Daftari")
            prof['coins'] -= 1000
            bot.answer_callback_query(call.id, "✅ 1 martalik buyum xarid qilindi!", show_alert=True)
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
            prof = get_user_profile(call.from_user.id)
            # KIRA DAFTARI 2X KILL ISHLATILSA INVENTARDAN O'CHADI
            if len(game['pending_kills']) >= 2 and "📓 Kira Daftari" in prof['inventory']:
                prof['inventory'].remove("📓 Kira Daftari")
            bot.answer_callback_query(call.id, "Ism yozildi!")

if __name__ == "__main__":
    threading.Thread(target=run_flask, daemon=True).start()
    bot.polling(none_stop=True)
        
    
            
        
