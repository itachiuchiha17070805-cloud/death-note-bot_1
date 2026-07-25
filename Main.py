import os
import random
import threading
import time
import sqlite3
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

# ================= BOT CONFIG =================
TOKEN = os.environ.get('BOT_TOKEN', '8816866283:AAGJK1TXHj1b7LZQYQOG7e5w18fOfUH51PM')
bot = TeleBot(TOKEN)
OWNER_ID = 6090422473

BOT_USERNAME = ""
try:
    BOT_USERNAME = bot.get_me().username
except Exception:
    pass

# Media resurslar
VID_NIGHT_SHINIGAMI = "BAACAgIAAxkBAAOkamOlVOl26MJFVUhfNHNi9rlGklEAAo6gAAL2HBlLZkqb-a1mXQg9BA"
GIF_DAY_START = "CgACAgIAAxkBAAOoamOutc6Wuf_8qZRR9P4Sa-Ma7-MAAuGgAAL2HBlLTIcoCecwxoY9BA"
VID_KIRA_WIN = "BAACAgIAAxkBAAOcamOjlGxvF-sQRjpGhOMss5BoRJAAAn6gAAL2HBlL9YoV8W6jmtU9BA"
VID_L_INVESTIGATE = "BAACAgIAAxkBAAOeamOj_BZ7ATgL5IYqkqp_c8ttBG4AAoOgAAL2HBlL1DxA2BLMmCo9BA"
VID_KIRA_FIRST_KILL = "BAACAgIAAxkBAAOgamOkYUl93OnEJUrtZU_gomJwFlMAAoqgAAL2HBlLgTO60GPr0hI9BA"
VID_L_WIN = "BAACAgIAAxkBAAOiamOk543jPQXByEQZxEIcamNciz4AAoygAAL2HBlLHjkU3rpfDRY9BA"
GIF_KIRA_DIES = "CgACAgIAAxkBAAOmamOtjuILC7y_gntablguan3uETAAAtKgAAL2HBlLRYDNDMWd9So9BA"
GIF_L_DIES = "CgACAgIAAxkBAAOqamOvVxow7dGO_DS5GKPmYcfbIRMAAuygAAL2HBlLfAQYGv77wJU9BA"

games = {}

# ================= SQLITE DATABASE BAZASI =================
def init_db():
    conn = sqlite3.connect('deathnote.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            name TEXT,
            coins INTEGER DEFAULT 100,
            wins INTEGER DEFAULT 0,
            games_played INTEGER DEFAULT 0,
            last_daily REAL DEFAULT 0,
            inventory TEXT DEFAULT '',
            achievements TEXT DEFAULT '',
            rank TEXT DEFAULT '🌱 Novice',
            tasks_done TEXT DEFAULT ''
        )
    ''')
    conn.commit()
    conn.close()

init_db()

def db_get_user(user_id, name="O'yinchi"):
    conn = sqlite3.connect('deathnote.db')
    cursor = conn.cursor()
    cursor.execute("SELECT user_id, name, coins, wins, games_played, last_daily, inventory, achievements, rank, tasks_done FROM users WHERE user_id=?", (user_id,))
    row = cursor.fetchone()

    if not row:
        cursor.execute("INSERT INTO users (user_id, name) VALUES (?, ?)", (user_id, name))
        conn.commit()
        cursor.execute("SELECT user_id, name, coins, wins, games_played, last_daily, inventory, achievements, rank, tasks_done FROM users WHERE user_id=?", (user_id,))
        row = cursor.fetchone()

    conn.close()

    user = {
        'user_id': row[0],
        'name': row[1],
        'coins': row[2],
        'wins': row[3],
        'games_played': row[4],
        'last_daily': row[5],
        'inventory': [i for i in row[6].split(',') if i],
        'achievements': [a for a in row[7].split(',') if a],
        'rank': row[8],
        'tasks_done': [t for t in row[9].split(',') if t]
    }
    return user

def db_update_user(user):
    # Unvonni yangilash
    wins = user['wins']
    if wins >= 50: user['rank'] = "☠️ Death God"
    elif wins >= 30: user['rank'] = "🧠 Mastermind"
    elif wins >= 15: user['rank'] = "🕵️‍♂️ Master Detective"
    elif wins >= 5: user['rank'] = "🔍 Investigator"
    else: user['rank'] = "🌱 Novice"

    conn = sqlite3.connect('deathnote.db')
    cursor = conn.cursor()
    cursor.execute('''
        UPDATE users SET 
            name=?, coins=?, wins=?, games_played=?, last_daily=?, 
            inventory=?, achievements=?, rank=?, tasks_done=?
        WHERE user_id=?
    ''', (
        user['name'], user['coins'], user['wins'], user['games_played'], user['last_daily'],
        ','.join(user['inventory']), ','.join(user['achievements']), user['rank'], ','.join(user['tasks_done']),
        user['user_id']
    ))
    conn.commit()
    conn.close()

def award_achievement(user_id, ach_key, title, reward_coins, chat_id=None):
    user = db_get_user(user_id)
    if ach_key not in user['achievements']:
        user['achievements'].append(ach_key)
        user['coins'] += reward_coins
        db_update_user(user)
        msg = f"🏆 **YANGI YUTUQ OCHILDI!**\n\n🎯 **{title}**\n💰 Mukofot: **+{reward_coins} Coin**!"
        try:
            bot.send_message(user_id, msg)
        except Exception:
            if chat_id:
                bot.send_message(chat_id, f"🎉 **{user['name']}** yutuqqa erishdi: **{title}** (+{reward_coins} Coin)!")

# ================= PERSONAJLAR HAQIDA BAZA =================
ROLES_INFO = {
    "Kira": "📓 **Kira (Light Yagami):** Tunda O'lim Daftariga o'yinchi nomini yozib yo'q qiladi. Barcha g'animlarni mahv etish uning maqsadi!",
    "L": "🕵️‍♂️ **L (Lawliet):** Dunyoning eng kuchli detektivi. Tunda shubhali shaxsni tekshirib, Kira ekanligini fosh etadi.",
    "Naomi Misora": "🛑 **Naomi Misora:** Sobiq FBR agenti. Tunda o'yinchini bloklab, uning qobiliyatini to'xtatadi. Limit: 2 marta.",
    "Soichiro Yagami": "👮‍♂️ **Soichiro Yagami:** Politsiya boshlig'i. Tunda biror kishini (o'zini ham) himoya qiladi. Limit: 2 marta.",
    "Aizawa": "💥 **Aizawa:** Kunduzi shubhali kishiga o'q uzadi. Kira bo'lsa u o'ladi, begunoh bo'lsa ikkalasi ham halok bo'ladi!",
    "Misa": "👁 **Misa Amane:** Shinigami ko'zlari bilan rollarni aniq ko'radi. Kira bilan maxfiy yozisha oladi. Limit: 3 marta.",
    "Near": "🧠 **Near (N):** L halok bo'lsa, L'ning barcha tergov qobiliyati va vazifasi Near'ga o'tadi.",
    "Ryuk": "🍎 **Ryuk:** Neytral Shinigami. Tunda tasodifiy o'yinchiga Coin beradi yoki o'g'irlaydi!",
    "Kiyomi Takada": "🎭 **Kiyomi Takada:** Kiraning suxandani. Tunda OAV orqali chalg'ituvchi xabarlar tarqatadi.",
    "Mello": "🔥 **Mello:** Tunda tavakkal qilib hujum qiladi. Kira bo'lsa Kira o'ladi, bo'lmasa Mello 2 kechaga blokka tushadi.",
    "Teru Mikami": "📜 **Teru Mikami (X-Kira):** Asl Kira o'lsa, O'lim Daftari unga o'tadi va u Yangi Kira bo'ladi!",
    "Matsuda": "🗣 **Matsuda:** Soddadil politsiyachi. Kunduzgi ovoz berishda uning ovozi 2x kuchga ega!"
}

def assign_roles(players_dict):
    player_ids = list(players_dict.keys())
    random.shuffle(player_ids)
    roles = {}
    role_pool = ["Kira", "L", "Naomi Misora", "Soichiro Yagami", "Aizawa", "Misa", "Near", "Ryuk", "Kiyomi Takada", "Mello", "Teru Mikami", "Matsuda"]
    for i, p_id in enumerate(player_ids):
        roles[p_id] = role_pool[i] if i < len(role_pool) else "Tinch Aholi"
    return roles

def send_private_safe(user_id, text, reply_markup=None, group_chat_id=None):
    try:
        bot.send_message(user_id, text, reply_markup=reply_markup, parse_mode="Markdown")
        return True
    except Exception:
        if group_chat_id:
            user = db_get_user(user_id)
            kb = types.InlineKeyboardMarkup()
            if BOT_USERNAME:
                kb.add(types.InlineKeyboardButton("🤖 Botda /start bosish", url=f"https://t.me/{BOT_USERNAME}?start=game"))
            bot.send_message(group_chat_id, f"⚠️ **{user['name']}**, sizga shaxsiy xabar yuborib bo'lmadi! Pastdagi tugma orqali botga kirib `/start` bosing:", reply_markup=kb)
        return False
def check_kira_death_and_transfer(chat_id, dead_kira_name="Kira"):
    game = games.get(chat_id)
    if not game: return

    try: bot.send_animation(chat_id, GIF_KIRA_DIES, caption=f"💥 **KIRA QULADI!** {dead_kira_name} halok bo'ldi!")
    except Exception: bot.send_message(chat_id, f"💥 **KIRA QULADI!** {dead_kira_name} halok bo'ldi!")

    time.sleep(1.5)
    mikami_id = [p for p, r in game['roles'].items() if r == "Teru Mikami" and p in game['alive']]

    if mikami_id and not game.get('mikami_used', False):
        game['mikami_used'] = True
        game['roles'][mikami_id[0]] = "Kira"
        bot.send_message(chat_id, "📜 **ANIME BURILISHI!**\n\n'Adolat to'xtamaydi!' O'lim Daftari **Teru Mikami**ning qo'liga o'tdi! U yangi Kira!")
        send_private_safe(mikami_id[0], "⚡️ **SIZ YANGI KIRASIZ!** O'lim Daftari sizga o'tdi!", None, chat_id)
    else:
        try: bot.send_video(chat_id, VID_L_WIN, caption="🎉 **BUYUK G'ALABA!** Kira butunlay yo'q qilindi!\n💰 Tiriklarga **+50 Coin**!")
        except Exception: bot.send_message(chat_id, "🎉 **BUYUK G'ALABA!** Kira yo'q qilindi!\n💰 Tiriklarga +50 Coin!")

        for p_id in game['alive']:
            user = db_get_user(p_id)
            user['coins'] += 50
            user['wins'] += 1
            db_update_user(user)
            award_achievement(p_id, "first_win", "🏆 Birinchi G'alaba", 100, chat_id)
            if user['wins'] >= 10:
                award_achievement(p_id, "win_10", "👑 Tajribali Detektiv", 300, chat_id)

        games.pop(chat_id, None)

def get_lobby_text(chat_id):
    game = games.get(chat_id)
    if not game: return ""
    players_list = game.get('players', {})
    count = len(players_list)
    names_str = "\n".join([f"{i+1}. {name}" for i, name in enumerate(players_list.values())])
    return (
        f"🎮 **DEATH NOTE: ADOLAT URUSHI**\n\n"
        f"👥 **Sahnadagi o'yinchilar ({count} kishi):**\n"
        f"{names_str}\n\n"
        f"⚠️ **MUHIM:** Rol va tugmalarni olish uchun bot shaxsiyida `/start` bosgan bo'ling!\n"
        f"⏱ O'yin tez orada boshlanadi!"
    )

def start_day(chat_id):
    game = games.get(chat_id)
    if not game or game.get('status') != 'night': return

    game['status'] = 'day'
    game['votes'] = {}
    targets = game.get('pending_kills', [])
    protected_id = game.get('protected_player')

    try: bot.send_animation(chat_id, GIF_DAY_START, caption="☀️ **Yangi kun boshlandi!**")
    except Exception: bot.send_message(chat_id, "☀️ **Yangi kun boshlandi!**")

    if game.get('ryuk_event'):
        bot.send_message(chat_id, game['ryuk_event'])
        game['ryuk_event'] = None

    dead_this_night = []
    if targets:
        for target_id in targets:
            user = db_get_user(target_id)
            if "🍎 Shinigami Olmasi" in user['inventory'] and target_id != protected_id:
                user['inventory'].remove("🍎 Shinigami Olmasi")
                db_update_user(user)
                bot.send_message(chat_id, f"🍎 **{game['players'].get(target_id)}** Shinigami Olmasi evaziga tirik qoldi!")
                continue

            if target_id != protected_id and target_id in game['alive']:
                game['alive'].remove(target_id)
                dead_this_night.append(target_id)
                v_name = game['players'].get(target_id, "Noma'lum")
                v_role = game['roles'].get(target_id, "Noma'lum")

                if v_role == "L":
                    game['l_alive'] = False
                    try: bot.send_animation(chat_id, GIF_L_DIES, caption=f"💀 **L ({v_name}) tunda halok bo'ldi!** Near ishni o'z zimmasiga oladi!")
                    except Exception: bot.send_message(chat_id, f"💀 **L ({v_name}) tunda halok bo'ldi!** Near ishni o'z zimmasiga oladi!")
                else:
                    bot.send_message(chat_id, f"💀 **FOJIA!** Tunda **{v_name}** ({v_role}) halok bo'ldi...")

        if dead_this_night and not game.get('kira_first_kill_shown'):
            game['kira_first_kill_shown'] = True
            try: bot.send_video(chat_id, VID_KIRA_FIRST_KILL, caption="📓 **Kira birinchi qurbonini O'lim Daftariga yozdi...**")
            except Exception: pass

    if not dead_this_night:
        bot.send_message(chat_id, "🛡 **XUSHXABAR!** Bu kecha hech kim halok bo'lmadi.")

    kira_id = [p for p, r in game['roles'].items() if r == "Kira"]

    if kira_id and kira_id[0] not in game['alive']:
        check_kira_death_and_transfer(chat_id, game['players'].get(kira_id[0], "Kira"))
        return

    if kira_id and kira_id[0] in game['alive'] and len(game['alive']) <= 2:
        try: bot.send_video(chat_id, VID_KIRA_WIN, caption="📓 **KIRA G'ALABA QOZONDI!**\n🏆 **MVP Kira** ga **+250 Coin** berildi!")
        except Exception: bot.send_message(chat_id, "📓 **KIRA G'ALABA QOZONDI!**\n🏆 **MVP Kira** ga **+250 Coin**!")

        u = db_get_user(kira_id[0])
        u['coins'] += 250
        u['wins'] += 1
        db_update_user(u)
        award_achievement(kira_id[0], "god_world", "📓 Yangi Dunyo Xudosi", 500, chat_id)
        games.pop(chat_id, None)
        return

    kb = types.InlineKeyboardMarkup(row_width=1)
    aizawa_id = [p for p, r in game['roles'].items() if r == "Aizawa"]
    if aizawa_id and aizawa_id[0] in game['alive'] and game['aizawa_shots'].get(aizawa_id[0], 0) < 2:
        kb.add(types.InlineKeyboardButton("💥 Aizawa: Otish (Limit 2x)", callback_data=f"aizawashot_menu_{chat_id}"))

    for p_id in game['alive']:
        kb.add(types.InlineKeyboardButton(f"🗳 {game['players'][p_id]}ga ovoz berish", callback_data=f"vote_{chat_id}_{p_id}"))

    bot.send_message(chat_id, "🗣 **MUHOKAMA VA OVOZ BERISH (30s):**", reply_markup=kb)
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
                bot.send_message(chat_id, f"⚖️ **OMMAVIY HUKM!** {v_name} ({v_role}) qatl qilindi!")

                if v_role == "Kira":
                    check_kira_death_and_transfer(chat_id, v_name)
                    return
        else:
            bot.send_message(chat_id, "🗣 Ovozlar yetarli bo'lmadi.")

        time.sleep(2)
        start_night(chat_id)

def start_night(chat_id):
    game = games.get(chat_id)
    if not game: return

    game['status'] = 'night'
    game['night_count'] = game.get('night_count', 0) + 1
    game['pending_kills'] = []
    game['blocked_player'] = None
    game['protected_player'] = None

    try: bot.send_video(chat_id, VID_NIGHT_SHINIGAMI, caption=f"🌙 **{game['night_count']}-KECHA BOSHLA NDI (30s)**\nShaxsiyingizni tekshiring!")
    except Exception: bot.send_message(chat_id, f"🌙 {game['night_count']}-kecha boshlandi.")

    alive_players = game['alive']
    for player_id in alive_players:
        role = game['roles'].get(player_id)
        u = db_get_user(player_id)

        if role == "Kira":
            max_k = 2 if "📓 Kira Daftari" in u['inventory'] else 1
            kb = types.InlineKeyboardMarkup(row_width=1)
            for t_id in alive_players:
                if t_id != player_id: kb.add(types.InlineKeyboardButton(f"🗡 {game['players'][t_id]}", callback_data=f"target_{chat_id}_{t_id}"))
            send_private_safe(player_id, f"📓 **Kira:** Qaysi ismni daftarga yozasiz? (Limit: {max_k})", kb, chat_id)

        elif role == "Kiyomi Takada":
            uses = game['takada_uses'].get(player_id, 3)
            if uses > 0:
                kb = types.InlineKeyboardMarkup(row_width=1)
                kb.add(types.InlineKeyboardButton("📢 OAV xabarini tarqatish", callback_data=f"fakefact_{chat_id}_random"))
                send_private_safe(player_id, f"🎭 **Takada:** OAV xabari chiqarish (Qolgan limit: {uses})", kb, chat_id)

        elif role == "Naomi Misora":
            uses = game['naomi_uses'].get(player_id, 2)
            if uses > 0:
                kb = types.InlineKeyboardMarkup(row_width=1)
                for t_id in alive_players:
                    if t_id != player_id: kb.add(types.InlineKeyboardButton(f"🛑 {game['players'][t_id]}", callback_data=f"block_{chat_id}_{t_id}"))
                send_private_safe(player_id, f"🛑 **Naomi:** Kimni bloklaysiz? (Qolgan limit: {uses})", kb, chat_id)

        elif role == "L" or (role == "Near" and not game.get('l_alive', True)):
            kb = types.InlineKeyboardMarkup(row_width=1)
            for t_id in alive_players:
                if t_id != player_id: kb.add(types.InlineKeyboardButton(f"🔍 {game['players'][t_id]}", callback_data=f"checkl_{chat_id}_{t_id}"))
            send_private_safe(player_id, "🕵️‍♂️ **Tergovchi:** Kimning shaxsiyatini tekshirasiz?", kb, chat_id)

        elif role == "Soichiro Yagami":
            uses = game['soichiro_uses'].get(player_id, 2)
            if uses > 0:
                kb = types.InlineKeyboardMarkup(row_width=1)
                for t_id in alive_players: kb.add(types.InlineKeyboardButton(f"🛡 {game['players'][t_id]}", callback_data=f"protect_{chat_id}_{t_id}"))
                send_private_safe(player_id, f"👮‍♂️ **Soichiro:** Kimni himoya qilasiz? (Limit: {uses})", kb, chat_id)

        elif role == "Misa":
            uses = game['misa_uses'].get(player_id, 0)
            if uses > 0 or "👁 Shinigami Ko'zlari" in u['inventory']:
                kb = types.InlineKeyboardMarkup(row_width=1)
                for t_id in alive_players:
                    if t_id != player_id: kb.add(types.InlineKeyboardButton(f"👁 {game['players'][t_id]}", callback_data=f"misaeyes_{chat_id}_{t_id}"))
                send_private_safe(player_id, "👁 **Misa:** Kimning rolini ko'rasiz?", kb, chat_id)

        elif role == "Mello":
            cd = game['mello_cd'].get(player_id, 0)
            if cd > 0:
                game['mello_cd'][player_id] -= 1
                send_private_safe(player_id, f"⏳ **Mello:** Xato hujum tufayli harakatsizsiz! (Qolgan CD: {game['mello_cd'][player_id]})", None, chat_id)
            else:
                kb = types.InlineKeyboardMarkup(row_width=1)
                for t_id in alive_players:
                    if t_id != player_id: kb.add(types.InlineKeyboardButton(f"🔥 {game['players'][t_id]}", callback_data=f"melloattack_{chat_id}_{t_id}"))
                send_private_safe(player_id, "🔥 **Mello:** Kimga hujum qilasiz?", kb, chat_id)

        elif role == "Ryuk":
            lucky_id = random.choice(alive_players)
            delta = random.choice([25, -25])
            l_u = db_get_user(lucky_id)
            l_u['coins'] = max(0, l_u['coins'] + delta)
            db_update_user(l_u)
            game['ryuk_event'] = f"🍎 **Ryuk:** {game['players'][lucky_id]} bilan o'ynab, **{delta} Coin** o'zgartirdi!"

    threading.Thread(target=night_timer, args=(chat_id,), daemon=True).start()

def night_timer(chat_id):
    time.sleep(30)
    start_day(chat_id)

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
    game['mello_cd'] = {}
    game['soichiro_uses'] = {}
    game['mikami_used'] = False
    game['l_alive'] = True
    game['night_count'] = 0

    bot.send_message(chat_id, "🎭 **O'YIN BOSH LANDI!** Rollar shaxsiy chatga yuborildi.")

    for p_id, role in game['roles'].items():
        u = db_get_user(p_id)
        u['games_played'] += 1
        u['coins'] += 15
        db_update_user(u)

        if u['games_played'] >= 5: award_achievement(p_id, "games_5", "🎮 Faol O'yinchi", 150, chat_id)

        if role == "Naomi Misora": game['naomi_uses'][p_id] = 2
        if role == "Kiyomi Takada": game['takada_uses'][p_id] = 3
        if role == "Soichiro Yagami": game['soichiro_uses'][p_id] = 2
        if role == "Aizawa": game['aizawa_shots'][p_id] = 0
        if role == "Misa": game['misa_uses'][p_id] = 3
        if role == "Mello": game['mello_cd'][p_id] = 0

        send_private_safe(p_id, f"🎭 Sizning rolingiz: **{role}**\nUnvoningiz: {u['rank']}", None, chat_id)

    time.sleep(2)
    start_night(chat_id)
# ================= BUYRUQLAR (COMMANDS) =================
@bot.message_handler(commands=['start'])
def start_cmd(message):
    db_get_user(message.from_user.id, message.from_user.first_name)
    kb = types.InlineKeyboardMarkup(row_width=2)
    kb.add(
        types.InlineKeyboardButton("📜 Rollar va Info", callback_data="info_roles"),
        types.InlineKeyboardButton("🛒 Do'kon", callback_data="open_shop")
    )
    kb.add(
        types.InlineKeyboardButton("🎯 Missiyalar", callback_data="show_tasks"),
        types.InlineKeyboardButton("🏆 Top O'yinchilar", callback_data="show_top")
    )

    welcome_text = (
        "📓 **DEATH NOTE BOTIGA XUSH KELIBSIZ!** 🖤\n\n"
        "⚡️ Siz bu intellektual psixologik o'yinda **Kira**, **L** yoki boshqa dinamik personajlar safida o'ynashingiz mumkin!\n\n"
        "🎮 **Buyruqlar:**\n"
        "• `/create` — Guruhda yangi o'yin yaratish\n"
        "• `/roles` — Personajlar haqida ma'lumot\n"
        "• `/profile` — Profil, yutuq va unvoningiz\n"
        "• `/tasks` — Kunlik missiyalar\n"
        "• `/shop` — Artefaktlar do'koni\n"
        "• `/daily` — Kunlik bonus (+100 Coin)"
    )
    bot.reply_to(message, welcome_text, reply_markup=kb)

@bot.message_handler(commands=['roles', 'info'])
def roles_info_cmd(message):
    kb = types.InlineKeyboardMarkup(row_width=2)
    for role_name in ROLES_INFO.keys():
        kb.add(types.InlineKeyboardButton(f"🎭 {role_name}", callback_data=f"viewrole_{role_name}"))
    bot.reply_to(message, "🎭 **PERSONAJLAR HAQIDA MA'LUMOT:**", reply_markup=kb)

@bot.message_handler(commands=['daily'])
def daily_cmd(message):
    u = db_get_user(message.from_user.id, message.from_user.first_name)
    now = time.time()
    if now - u['last_daily'] >= 86400:
        u['coins'] += 100
        u['last_daily'] = now
        db_update_user(u)
        bot.reply_to(message, "🎁 **KUNLIK BONUS!** +100 Coin olindi!")
    else:
        rem = int((86400 - (now - u['last_daily'])) // 3600)
        bot.reply_to(message, f"⏱ Keyingi bonus **{rem} soatdan** keyin.")

@bot.message_handler(commands=['tasks'])
def tasks_cmd(message):
    u = db_get_user(message.from_user.id, message.from_user.first_name)
    txt = "🎯 **KUNLIK MISSIYALAR VA TOPSHIRIQ LAR:**\n\n"

    # Task 1: 3 ta o'yin
    t1 = "✅ Bajarildi (+100 Coin)" if "t_games_3" in u['tasks_done'] else ("🎁 Olish (/claim_t1)" if u['games_played'] >= 3 else f"⏳ Jarayon: {u['games_played']}/3 o'yin")
    txt += f"1. 3 ta o'yin o'ynash — {t1}\n"

    # Task 2: 1 g'alaba
    t2 = "✅ Bajarildi (+150 Coin)" if "t_win_1" in u['tasks_done'] else ("🎁 Olish (/claim_t2)" if u['wins'] >= 1 else f"⏳ Jarayon: {u['wins']}/1 g'alaba")
    txt += f"2. 1 marta g'alaba qozonish — {t2}\n"

    bot.reply_to(message, txt)

@bot.message_handler(commands=['claim_t1'])
def claim_t1(message):
    u = db_get_user(message.from_user.id)
    if "t_games_3" not in u['tasks_done'] and u['games_played'] >= 3:
        u['tasks_done'].append("t_games_3")
        u['coins'] += 100
        db_update_user(u)
        bot.reply_to(message, "🎉 **MISSIYA BAJARILDI!** +100 Coin berildi!")
    else: bot.reply_to(message, "❌ Topshiriq bajarilmagan yoki mukofot olingan.")

@bot.message_handler(commands=['claim_t2'])
def claim_t2(message):
    u = db_get_user(message.from_user.id)
    if "t_win_1" not in u['tasks_done'] and u['wins'] >= 1:
        u['tasks_done'].append("t_win_1")
        u['coins'] += 150
        db_update_user(u)
        bot.reply_to(message, "🎉 **MISSIYA BAJARILDI!** +150 Coin berildi!")
    else: bot.reply_to(message, "❌ Topshiriq bajarilmagan yoki mukofot olingan.")

@bot.message_handler(commands=['profile'])
def profile_cmd(message):
    u = db_get_user(message.from_user.id, message.from_user.first_name)
    inv = ", ".join(u['inventory']) if u['inventory'] else "Bo'sh"
    achs = ", ".join(u['achievements']) if u['achievements'] else "Yo'q"

    text = (
        f"👤 **PROFIL: {u['rank']} {u['name']}**\n\n"
        f"💰 **Coinlar:** {u['coins']} coin\n"
        f"🏆 **G'alabalar:** {u['wins']}\n"
        f"🎮 **O'yinlar:** {u['games_played']}\n"
        f"🎒 **Inventar:** {inv}\n"
        f"🎖 **Yutuqlar (Achievements):** {achs}"
    )
    bot.reply_to(message, text)

@bot.message_handler(commands=['top'])
def top_cmd(message):
    conn = sqlite3.connect('deathnote.db')
    cursor = conn.cursor()
    cursor.execute("SELECT rank, name, wins FROM users ORDER BY wins DESC LIMIT 10")
    rows = cursor.fetchall()
    conn.close()

    text = "🏆 **TOP-10 O'YINCHILAR**\n\n"
    for i, row in enumerate(rows, 1):
        text += f"{i}. {row[0]} **{row[1]}** — {row[2]} g'alaba\n"
    bot.reply_to(message, text)

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
        'alive': [],
        'msg_id': None
    }

    kb = types.InlineKeyboardMarkup(row_width=1)
    kb.add(types.InlineKeyboardButton("✋ Qo'shilish", callback_data=f"join_{chat_id}"))
    if BOT_USERNAME:
        kb.add(types.InlineKeyboardButton("🤖 Botni faollashtirish (PM)", url=f"https://t.me/{BOT_USERNAME}?start=game"))
    kb.add(types.InlineKeyboardButton("🚀 Boshlash", callback_data=f"start_{chat_id}"))

    msg = bot.send_message(chat_id, get_lobby_text(chat_id), reply_markup=kb)
    games[chat_id]['msg_id'] = msg.message_id

# ================= CALLBACK HANDLERLAR =================
@bot.callback_query_handler(func=lambda call: True)
def callback_inline(call):
    data = call.data.split("_")
    action = data[0]

    if action == "viewrole":
        bot.answer_callback_query(call.id)
        bot.send_message(call.message.chat.id, ROLES_INFO.get(data[1], "Topilmadi."))
        return

    if action == "show":
        if data[1] == "tasks": tasks_cmd(call.message)
        elif data[1] == "top": top_cmd(call.message)
        return

    if action in ["target", "checkl", "protect", "misaeyes", "melloattack", "block"]:
        c_id = int(data[1])
        game = games.get(c_id)
        if game and game.get('blocked_player') == call.from_user.id:
            bot.answer_callback_query(call.id, "🛑 Naomi Misora sizni blokladi!", show_alert=True)
            return

    if action == "vote":
        c_id, target_id = int(data[1]), int(data[2])
        game = games.get(c_id)
        if game and game['status'] == 'day':
            game['votes'][call.from_user.id] = target_id
            bot.answer_callback_query(call.id, "Ovozingiz muhrlandi!")

    elif action == "target":
        c_id, target_id = int(data[1]), int(data[2])
        game = games.get(c_id)
        if game:
            game['pending_kills'].append(target_id)
            bot.answer_callback_query(call.id, "Ism O'lim Daftariga yozildi!", show_alert=True)

    elif action == "checkl":
        c_id, target_id = int(data[1]), int(data[2])
        game = games.get(c_id)
        if game:
            res = "KIRA!" if game['roles'].get(target_id) == "Kira" else "Kira EMAS."
            bot.answer_callback_query(call.id, f"Tergov natijasi: {res}", show_alert=True)

    elif action == "protect":
        c_id, target_id = int(data[1]), int(data[2])
        game = games.get(c_id)
        if game:
            uses = game['soichiro_uses'].get(call.from_user.id, 0)
            if uses > 0:
                game['soichiro_uses'][call.from_user.id] -= 1
                game['protected_player'] = target_id
                bot.answer_callback_query(call.id, "✅ Himoyalandi!", show_alert=True)
            else:
                bot.answer_callback_query(call.id, "❌ Limit tugagan!", show_alert=True)

    elif action == "block":
        c_id, target_id = int(data[1]), int(data[2])
        game = games.get(c_id)
        if game:
            uses = game['naomi_uses'].get(call.from_user.id, 0)
            if uses > 0:
                game['naomi_uses'][call.from_user.id] -= 1
                game['blocked_player'] = target_id
                bot.answer_callback_query(call.id, "🛑 O'yinchi bloklandi!", show_alert=True)

    elif action == "join":
        c_id = int(data[1])
        game = games.get(c_id)
        if game and game['status'] == 'waiting':
            if call.from_user.id not in game['players']:
                game['players'][call.from_user.id] = call.from_user.first_name
                db_get_user(call.from_user.id, call.from_user.first_name)
                bot.answer_callback_query(call.id, "Qo'shildingiz!")

                kb = types.InlineKeyboardMarkup(row_width=1)
                kb.add(types.InlineKeyboardButton("✋ Qo'shilish", callback_data=f"join_{c_id}"))
                if BOT_USERNAME: kb.add(types.InlineKeyboardButton("🤖 Botni faollashtirish (PM)", url=f"https://t.me/{BOT_USERNAME}?start=game"))
                kb.add(types.InlineKeyboardButton("🚀 Boshlash", callback_data=f"start_{c_id}"))

                try: bot.edit_message_text(chat_id=c_id, message_id=game['msg_id'], text=get_lobby_text(c_id), reply_markup=kb)
                except Exception: pass

    elif action == "start":
        c_id = int(data[1])
        game = games.get(c_id)
        if game and game['status'] == 'waiting':
            if len(game['players']) >= 3:
                start_game_logic(c_id)
            else:
                bot.answer_callback_query(call.id, "Kamida 3 kishi kerak!", show_alert=True)

if __name__ == "__main__":
    threading.Thread(target=run_flask, daemon=True).start()
    bot.polling(none_stop=True)
    
    
    
    
