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

# ================= PERSONAJLAR HAQIDA MA'LUMOT BAZASI =================
ROLES_INFO = {
    "Kira": "📓 **Kira (Light Yagami):** Yangi dunyo Xudosi bo'lishni xohlaydi. Tunda O'lim Daftariga istalgan odam nomini yozib yo'q qila oladi. Maqsadi — barcha raqiblarni va L'ni yo'q qilish!",
    "L": "🕵️‍♂️ **L (Lawliet):** Dunyoning eng kuchli detektivi. Tunda shubhali shaxsning rolini tekshirib, u Kira ekanligini bilib oladi. L o'lsa, uning ishini Near davom ettiradi.",
    "Naomi Misora": "🛑 **Naomi Misora:** Sobiq FBR agenti. Tunda biror o'yinchining izidan tushib, uning qobiliyatini block qiladi (u bu kecha hech narsa qila olmaydi). Limit: 2 marta.",
    "Soichiro Yagami": "👮‍♂️ **Soichiro Yagami:** Politsiya boshlig'i va fidoyi ota. Tunda biror o'yinchini (shu jumladan O'ZINI HAM) Kira hujumidan va o'limdan himoya qila oladi. Limit: 2 marta.",
    "Aizawa": "💥 **Aizawa:** Jasur politsiyachi. Kunduzi muhokama paytida shubhali deb bilgan odamiga o'q uzishi mumkin. Agar u Kiraga tegsa — Kira o'ladi, aks holda ikkalasi ham halok bo'ladi! Limit: 2 marta.",
    "Misa": "👁 **Misa Amane:** Kiraning sodiq oshig'i. Shinigami ko'zlari yordamida o'yinchilarning aniq rolini ko'ra oladi. Limit: 3 marta. Shuningdek, Kira bilan maxfiy yazisha oladi.",
    "Near": "🧠 **Near (N):** L'ning munosib vorisi. L halok bo'lganidan so'ng, L'ning barcha tergov qobiliyatlari va vakolatlari Near'ga o'tadi va u Kirani fosh qilishni davom ettiradi.",
    "Ryuk": "🍎 **Ryuk:** Zerikkan Shinigami (O'lim Xudosi). U neytral, tunda shunchaki erkin kezib, omadingizga qarab Coin sovg'a qiladi yoki cho'ntagingizdan coin o'g'irlaydi!",
    "Kiyomi Takada": "🎭 **Kiyomi Takada:** Kiraning OAVdagi rasmiy suxandani. Tunda guruhga yolg'on, chalg'ituvchi yoki qisman rost OAV xabarlarini tarqatib, tergovni chalkashtiradi. Limit: 3 marta.",
    "Mello": "🔥 **Mello:** Qat'iyatli va xavfli taktik. Tunda tavakkal qilib biror kishiga hujum qiladi. Agar u Kira bo'lsa, Kira yo'q qilinadi! Agar begunoh bo'lsa, Mello 2 kechaga qobiliyatini yo'qotadi.",
    "Teru Mikami": "📜 **Teru Mikami (X-Kira):** Kiraning eng ashaddiy izdoshi va adolat xodimi. Asl Kira halok bo'lsa, O'lim Daftari unga o'tadi va u Yangi Kira bo'lib o'yinni davom ettiradi!",
    "Matsuda": "🗣 **Matsuda:** Soddadil politsiya xodimi. Uning ovozi kunduzgi ovoz berish jarayonida 2 karra kuchga (2x weight) ega bo'ladi!"
}

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

def check_kira_death_and_transfer(chat_id, dead_kira_name="Kira"):
    """Kira halok bo'lganda o'lim animatsiyasini chiqarish va Teru Mikamiga rolni o'tkazish"""
    game = games.get(chat_id)
    if not game: return

    try:
        bot.send_animation(chat_id, GIF_KIRA_DIES, caption=f"💥 **KIRA QULADI!** {dead_kira_name} o'zining dahshatli taqdiriga duch keldi... O'lim Daftari qo'lidan tushib ketdi!")
    except Exception:
        bot.send_message(chat_id, f"💥 **KIRA QULADI!** {dead_kira_name} o'zining dahshatli taqdiriga duch keldi!")

    time.sleep(1.5)

    mikami_id = [p for p, r in game['roles'].items() if r == "Teru Mikami" and p in game['alive']]
    if mikami_id and not game.get('mikami_used', False):
        game['mikami_used'] = True
        game['roles'][mikami_id[0]] = "Kira"

        try:
            bot.send_message(chat_id, "📜 **KUTILMAGAN BURILISH (ANIME TWIST)!**\n\n'Adolat hech qachon to'xtamaydi!' — Qorong'ulik qoplami ostida O'lim Daftari yangi voris **Teru Mikami**ning qo'liga o'tdi! Kira ruhi va qasosi hali ham yashamoqda! ⚡️")
        except Exception:
            pass

        try:
            bot.send_message(mikami_id[0], "⚡️ **SIZ YANGI KIRASIZ!**\n\nAsl Kira yo'q qilindi. Lekin muqaddas missiya tugamadi! O'lim Daftari va Kiraning barcha vakolatlari sizga o'tdi! Shaharni adolat bilan tozalang!")
        except Exception:
            pass
    else:
        try:
            bot.send_video(chat_id, VID_L_WIN, caption="🎉 **BUYUK G'ALABA!**\n\nKira va uning barcha davomchilari tamomila yo'q qilindi! Dunyo qorong'ulikdan xalos bo'ldi!\n💰 Barcha tiriklarga **+25 Coin** berildi!")
        except Exception:
            bot.send_message(chat_id, "🎉 **BUYUK G'ALABA!** Kira yo'q qilindi! Tergovchilar va Tinch aholi yutdi!\n💰 Tiriklarga +25 Coin!")

        for p_id in game['alive']:
            prof = get_user_profile(p_id)
            prof['coins'] += 25
            prof['wins'] += 1
            if "🔍 Topuvchi" not in prof['achievements']:
                prof['achievements'].append("🔍 Topuvchi")

        games.pop(chat_id, None)

# ================= LOBBY MATNI =================
def get_lobby_text(chat_id):
    game = games.get(chat_id)
    if not game: return ""
    players_list = game.get('players', {})
    count = len(players_list)
    names_str = "\n".join([f"{i+1}. {name}" for i, name in enumerate(players_list.values())])
    return (
        f"🎮 **DEATH NOTE: SHAKKASIZ ADOLAT URUSHI**\n\n"
        f"👥 **Sahnaga chiqqanlar ({count} kishi):**\n"
        f"{names_str}\n\n"
        f"⏱ **O'yin 1 daqiqa ichida boshlanadi!** Qo'shilish uchun tugmani bosing!"
    )

# ================= KUN SIKLI =================
def start_day(chat_id):
    game = games.get(chat_id)
    if not game or game.get('status') != 'night': return

    game['status'] = 'day'
    game['votes'] = {}
    targets = game.get('pending_kills', [])
    protected_id = game.get('protected_player')

    try:
        bot.send_animation(chat_id, GIF_DAY_START, caption="☀️ **Quyosh nur sochdi... Ammo zulmat shamoli hali so'ngani yo'q. Yangi kun boshlandi!**")
    except Exception:
        bot.send_message(chat_id, "☀️ **Quyosh nur sochdi... Yangi kun boshlandi!**")

    if game.get('ryuk_event'):
        bot.send_message(chat_id, game['ryuk_event'])
        game['ryuk_event'] = None

    dead_this_night = []
    if targets:
        for target_id in targets:
            target_prof = get_user_profile(target_id)
            if "🍎 Shinigami Olmasi" in target_prof['inventory'] and target_id != protected_id:
                target_prof['inventory'].remove("🍎 Shinigami Olmasi")
                bot.send_message(chat_id, f"🍎 **{game['players'].get(target_id)}** xarid qilingan Shinigami Olmasi sharofati bilan tunni eson-omon o'tkazdi!")
                continue

            if target_id != protected_id and target_id in game['alive']:
                game['alive'].remove(target_id)
                dead_this_night.append(target_id)
                victim_name = game['players'].get(target_id, "Noma'lum")
                victim_role = game['roles'].get(target_id, "Noma'lum")

                if victim_role == "L":
                    game['l_alive'] = False
                    try:
                        bot.send_animation(chat_id, GIF_L_DIES, caption=f"💀 **DAHSHAT! L ({victim_name}) tunda halok bo'ldi!** Dunyo eng buyuk detektivini yo'qotdi... Near endi uning bayrog'ini ko'taradi!")
                    except Exception:
                        bot.send_message(chat_id, f"💀 **DAHSHAT! L ({victim_name}) tunda halok bo'ldi!** Near endi uning ishini davom ettiradi!")
                else:
                    bot.send_message(chat_id, f"💀 **FOJIA!** Tunda **{victim_name}** ({victim_role}) fojiali tarzda halok bo'ldi...")

        if dead_this_night and not game.get('kira_first_kill_shown'):
            game['kira_first_kill_shown'] = True
            try:
                bot.send_video(chat_id, VID_KIRA_FIRST_KILL, caption="📓 **Kira birinchi qurbonining ismini O'lim Daftariga qon bilan yozdi...**")
            except Exception:
                pass

    if not dead_this_night:
        bot.send_message(chat_id, "🛡 **XUSHXABAR!** Bu kecha shahar tinch bo'ldi, qorong'ulik hech kimni olib ketmadi.")

    kira_id = [p for p, r in game['roles'].items() if r == "Kira"]

    if kira_id and kira_id[0] not in game['alive']:
        check_kira_death_and_transfer(chat_id, game['players'].get(kira_id[0], "Kira"))
        return

    if kira_id and kira_id[0] in game['alive'] and len(game['alive']) <= 2:
        try:
            bot.send_video(chat_id, VID_KIRA_WIN, caption="📓 **DUNYO YANGI TIZIMGA BO'YSUNDI!**\n\nKira barcha g'animlarini yer bilan bitta qildi va Yangi Dunyo Xudosiga aylandi!\n🏆 **MVP Kira** ga **+200 Coin** taqdim etildi!")
        except Exception:
            bot.send_message(chat_id, "📓 **G'ALABA VA MVP!** Kira barcha raqiblarini yo'q qildi!\n🏆 **MVP Kira** ga **+200 Coin**!")

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

    bot.send_message(chat_id, "🗣 **XINSO VA MUHOKAMA VAQTI! (30 soniya)**\n\nKim shubhali? Ovoz bering:", reply_markup=kb)
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
                bot.send_message(chat_id, f"⚖️ **OMMAVIY HUKM!** {v_name} ({v_role}) ko'pchilik ovozi bilan dorga tortildi!")

                if v_role == "Kira":
                    check_kira_death_and_transfer(chat_id, v_name)
                    return
        else:
            bot.send_message(chat_id, "🗣 Shubhali shaxslar uchun yetarlicha ovoz yig'ilmadi.")

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
        bot.send_video(chat_id, VID_NIGHT_SHINIGAMI, caption=f"🌙 **{game['night_count']}-KECHA: Shahar uzra sukunat va Shinigamilar soyasi tushdi... (30 soniya)**")
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
            try: bot.send_message(player_id, f"📓 **Kira:** Qaysi ismni daftarga yozasiz? (Limit: {max_kills})", reply_markup=kb)
            except Exception: pass

        elif role == "Kiyomi Takada":
            uses = game['takada_uses'].get(player_id, 3)
            if uses > 0:
                kb = types.InlineKeyboardMarkup(row_width=1)
                kb.add(types.InlineKeyboardButton("📢 Tasodifiy o'yinchi haqida OAV xabari chiqarish", callback_data=f"fakefact_{chat_id}_random"))
                try: bot.send_message(player_id, f"🎭 **Kiyomi Takada:** OAV orqali xabar tarqatasizmi? (Qolgan limit: {uses})", reply_markup=kb)
                except Exception: pass

        elif role == "Naomi Misora":
            uses = game['naomi_uses'].get(player_id, 2)
            if uses > 0:
                kb = types.InlineKeyboardMarkup(row_width=1)
                for t_id in alive_players:
                    if t_id != player_id:
                        kb.add(types.InlineKeyboardButton(f"🛑 {game['players'][t_id]}", callback_data=f"block_{chat_id}_{t_id}"))
                try: bot.send_message(player_id, "🛑 **Naomi:** Kimning izidan tushib bloklaysiz?", reply_markup=kb)
                except Exception: pass

        elif role == "L" or (role == "Near" and not game.get('l_alive', True)):
            kb = types.InlineKeyboardMarkup(row_width=1)
            for t_id in alive_players:
                if t_id != player_id:
                    kb.add(types.InlineKeyboardButton(f"🔍 {game['players'][t_id]}", callback_data=f"checkl_{chat_id}_{t_id}"))
            try: bot.send_message(player_id, "🕵️‍♂️ **Tergovchi:** Kimning shaxsiyatini tekshirasiz?", reply_markup=kb)
            except Exception: pass

        elif role == "Soichiro Yagami":
            uses = game['soichiro_uses'].get(player_id, 2)
            if uses > 0:
                kb = types.InlineKeyboardMarkup(row_width=1)
                for t_id in alive_players:
                    kb.add(types.InlineKeyboardButton(f"🛡 {game['players'][t_id]}", callback_data=f"protect_{chat_id}_{t_id}"))
                try: bot.send_message(player_id, f"👮‍♂️ **Soichiro:** Kimni qalqoningiz bilan himoya qilasiz? (O'zingizni ham mumkin. Limit: {uses})", reply_markup=kb)
                except Exception: pass
            else:
                try: bot.send_message(player_id, "👮‍♂️ **Soichiro:** Himoya limit xagingiz (2 marta) tugadi!")
                except Exception: pass

        elif role == "Misa":
            uses = game['misa_uses'].get(player_id, 0)
            has_eyes = "👁 Shinigami Ko'zlari" in prof['inventory']
            if uses > 0 or has_eyes:
                kb = types.InlineKeyboardMarkup(row_width=1)
                for t_id in alive_players:
                    if t_id != player_id:
                        kb.add(types.InlineKeyboardButton(f"👁 {game['players'][t_id]}", callback_data=f"misaeyes_{chat_id}_{t_id}"))
                try: bot.send_message(player_id, "👁 **Misa (Shinigami Ko'zi):** Kimning rolingizni ko'rmoqchisiz?", reply_markup=kb)
                except Exception: pass

        elif role == "Mello":
            cd = game['mello_cd'].get(player_id, 0)
            if cd > 0:
                game['mello_cd'][player_id] -= 1
                try: bot.send_message(player_id, f"⏳ **Mello:** Xato hujum sababli bu kecha tinchsiz! (Qolgan CD: {game['mello_cd'][player_id]} kecha)")
                except Exception: pass
            else:
                kb = types.InlineKeyboardMarkup(row_width=1)
                for t_id in alive_players:
                    if t_id != player_id:
                        kb.add(types.InlineKeyboardButton(f"🔥 {game['players'][t_id]}", callback_data=f"melloattack_{chat_id}_{t_id}"))
                try: bot.send_message(player_id, "🔥 **Mello:** Tavakkal qilib kimga xujum qilasiz?", reply_markup=kb)
                except Exception: pass

        elif role == "Ryuk":
            lucky_id = random.choice(alive_players)
            delta = random.choice([20, -20])
            l_prof = get_user_profile(lucky_id)
            l_prof['coins'] = max(0, l_prof['coins'] + delta)
            l_name = game['players'][lucky_id]
            if delta > 0:
                game['ryuk_event'] = f"🍎 **Ryuk:** Zerikib, {l_name} bilan qimor o'ynadi va unga **+{delta} Coin** sovg'a qildi!"
            else:
                game['ryuk_event'] = f"🍎 **Ryuk:** {l_name}ning cho'ntagidan **{delta} Coin** o'g'irlab olma sotib oldi!"

    threading.Thread(target=night_timer, args=(chat_id,), daemon=True).start()

def night_timer(chat_id):
    time.sleep(30)
    start_day(chat_id)

def auto_start_timer(chat_id, wait_time=60):
    time.sleep(wait_time)
    game = games.get(chat_id)
    if game and game.get('status') == 'waiting':
        if len(game.get('players', {})) >= 3:
            start_game_logic(chat_id)
        else:
            bot.send_message(chat_id, "❌ Kamida 3 kishi yig'ilmadi. O'yin bekor qilindi.")
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
    game['mello_cd'] = {}
    game['soichiro_uses'] = {}
    game['mikami_used'] = False
    game['secret_msgs_used'] = 0
    game['l_alive'] = True
    game['night_count'] = 0

    bot.send_message(chat_id, "🎭 **SAHNA OCHILDI!** Rollar maxfiy ravishda tarqatildi. Shaxsiy chatingizni tekshiring!")
# ================= BUYRUQLAR (COMMANDS) =================
@bot.message_handler(commands=['start'])
def start_cmd(message):
    kb = types.InlineKeyboardMarkup(row_width=2)
    kb.add(
        types.InlineKeyboardButton("📜 Personajlar va Rollar", callback_data="info_roles"),
        types.InlineKeyboardButton("🛒 Do'kon", callback_data="open_shop")
    )
    kb.add(types.InlineKeyboardButton("🏆 Top O'yinchilar", callback_data="show_top"))

    welcome_text = (
        "📓 **DEATH NOTE: SHAKKASIZ ADOLAT DUNYOSIGA XUSH KELIBSIZ!** 🖤\n\n"
        "⚡️ *'O'lim Daftari yerga tushgan kundan boshlab, dunyo ikki qutbga bo'lindi...'* \n\n"
        "Siz bu intellektual va psixologik o'yinda **Kira** bo'lib yangi dunyo tartibini o'rnatishingiz, "
        "yoki **L** va uning maxfiy tergovchilar guruhiga qo'shilib, qorong'ulik hukmdorini fosh qilishingiz kerak!\n\n"
        "🎮 **O'yin buyruqlari:**\n"
        "• `/create` — Guruhda yangi o'yin yaratish\n"
        "• `/roles` yoki `/info` — Barcha personajlar va ularning qobiliyatlari\n"
        "• `/profile` — Sizning balansingiz, unvoningiz va buyumlaringiz\n"
        "• `/shop` — Do'kondan maxsus artefaktlar xarid qilish\n"
        "• `/daily` — Kunlik **+100 Coin** bonusini olish\n"
        "• `/maxfiy` — (Kira va Misa uchun) Shifrlangan aloqa\n"
        "• `/stop` — O'yinni to'xtatish"
    )
    bot.reply_to(message, welcome_text, reply_markup=kb)

@bot.message_handler(commands=['roles', 'info'])
def roles_info_cmd(message):
    kb = types.InlineKeyboardMarkup(row_width=2)
    for role_name in ROLES_INFO.keys():
        kb.add(types.InlineKeyboardButton(f"🎭 {role_name}", callback_data=f"viewrole_{role_name}"))

    bot.reply_to(
        message,
        "🎭 **DEATH NOTE PERSONAJLARI VA QOBILIYATLARI**\n\nBarcha personajlar va ularning o'yindagi vazifalari haqida ma'lumot olish uchun quyidagi tugmalardan birini bosing:",
        reply_markup=kb
    )

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
        bot.reply_to(message, "🎁 **KUNLIK BONUS!** Hisobingizga **+100 Coin** berildi!")
    else:
        rem = int((86400 - (now - prof['last_daily'])) // 3600)
        bot.reply_to(message, f"⏱ Keyingi bonusni **{rem} soatdan** keyin olasiz.")

@bot.message_handler(commands=['top'])
def top_cmd(message):
    sorted_users = sorted(user_data.items(), key=lambda x: x[1]['wins'], reverse=True)[:10]
    text = "🏆 **DEATH NOTE: SHAN-SHARAF ZALI (TOP-10)**\n\n"
    for i, (u_id, u_info) in enumerate(sorted_users, 1):
        text += f"{i}. {u_info['rank']} **{u_info['name']}** — {u_info['wins']} g'alaba\n"
    bot.reply_to(message, text)

@bot.message_handler(commands=['shop'])
def shop_cmd(message):
    kb = types.InlineKeyboardMarkup()
    kb.add(types.InlineKeyboardButton("👁 Shinigami Ko'zlari (1000 coin) - 1x", callback_data="buy_eyes"))
    kb.add(types.InlineKeyboardButton("🍎 Shinigami Olmasi / Himoya (1000 coin) - 1x", callback_data="buy_apple"))
    kb.add(types.InlineKeyboardButton("📓 Kira Daftari / 2x Kill (1000 coin) - 1x", callback_data="buy_notebook"))
    bot.reply_to(message, "🛒 **DEATH NOTE ARSENALI (1000 Coin, 1-martalik):**", reply_markup=kb)

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
        f"🎖 **YUTUQLAR:**\n• {achs}"
    )
    bot.reply_to(message, text)

@bot.message_handler(commands=['stop'])
def stop_cmd(message):
    chat_id = message.chat.id
    if chat_id in games:
        games.pop(chat_id, None)
        bot.reply_to(message, "🛑 **O'yin to'xtatildi.**")
    else:
        bot.reply_to(message, "⚠️ Faol o'yin yo'q.")

@bot.message_handler(commands=['extend'])
def extend_cmd(message):
    chat_id = message.chat.id
    game = games.get(chat_id)
    if game and game['status'] == 'waiting':
        threading.Thread(target=auto_start_timer, args=(chat_id, 120), daemon=True).start()
        bot.reply_to(message, "⏳ **Kutish vaqti +2 daqiqaga uzaytirildi!**")

@bot.message_handler(commands=['maxfiy'])
def secret_cmd(message):
    if message.chat.type != 'private': return
    sender_id = message.from_user.id
    text = message.text.replace('/maxfiy', '', 1).strip()
    if not text:
        bot.reply_to(message, "⚠️ Format: `/maxfiy xabar matni`")
        return

    for g in games.values():
        if sender_id in g.get('alive', []) and g['roles'].get(sender_id) in ("Kira", "Misa"):
            if g.get('secret_msgs_used', 0) >= 6:
                bot.reply_to(message, "❌ Maxfiy shifrlangan aloqa limiti tugadi (6 marta).")
                return
            other_role = "Misa" if g['roles'].get(sender_id) == "Kira" else "Kira"
            other_id = next((p for p, r in g['roles'].items() if r == other_role and p in g['alive']), None)
            if other_id:
                try:
                    bot.send_message(other_id, f"🔒 **SHIFRLANGAN MAXFIY XABAR:** {text}")
                    g['secret_msgs_used'] = g.get('secret_msgs_used', 0) + 1
                    bot.reply_to(message, f"✅ Xabar sherigingizga yetkazildi. (Qolgan limit: {6 - g['secret_msgs_used']})")
                except Exception:
                    bot.reply_to(message, "⚠️ Xabar yetkazilmadi.")
            else:
                bot.reply_to(message, "⚠️ Sherigingiz topilmadi yoki o'lgan.")
            return

    bot.reply_to(message, "⚠️ Siz faol o'yinda Kira yoki Misa rolida emassiz.")

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

    kb = types.InlineKeyboardMarkup()
    kb.add(types.InlineKeyboardButton("✋ Qo'shilish", callback_data=f"join_{chat_id}"))
    kb.add(types.InlineKeyboardButton("🚀 Boshlash", callback_data=f"start_{chat_id}"))

    txt = get_lobby_text(chat_id)

    try:
        with open(IMG_GAME_START, 'rb') as photo:
            msg = bot.send_photo(chat_id, photo, caption=txt, reply_markup=kb)
            games[chat_id]['msg_id'] = msg.message_id
    except Exception:
        msg = bot.send_message(chat_id, txt, reply_markup=kb)
        games[chat_id]['msg_id'] = msg.message_id

    threading.Thread(target=auto_start_timer, args=(chat_id, 60), daemon=True).start()
# ================= CALLBACK HANDLERLAR =================
@bot.callback_query_handler(func=lambda call: True)
def callback_inline(call):
    data = call.data.split("_")
    action = data[0]

    # PERSONAJLAR INFO TUGMASI BOSILGANDA
    if action == "viewrole":
        role_key = data[1]
        info_text = ROLES_INFO.get(role_key, "Ma'lumot topilmadi.")
        bot.answer_callback_query(call.id)
        bot.send_message(call.message.chat.id, info_text)
        return

    elif action == "info":
        if data[1] == "roles":
            roles_info_cmd(call.message)
            return

    elif action == "open":
        if data[1] == "shop":
            shop_cmd(call.message)
            return

    elif action == "show":
        if data[1] == "top":
            top_cmd(call.message)
            return

    # NAOMI BLOKLANGAN O'YINCHILAR TEKSHIRUVI
    if action in ["target", "checkl", "protect", "misaeyes", "melloattack", "block", "fakefact"]:
        c_id = int(data[1])
        game = games.get(c_id)
        if game and game.get('blocked_player') == call.from_user.id:
            bot.answer_callback_query(call.id, "🛑 Naomi Misora yo'lingizni tosdi! Harakatingiz izsiz ketdi.", show_alert=True)
            return

    if action == "vote":
        c_id, target_id = int(data[1]), int(data[2])
        game = games.get(c_id)
        if game and game['status'] == 'day':
            game['votes'][call.from_user.id] = target_id
            bot.answer_callback_query(call.id, "Ovozingiz muhrlandi!")

    elif action == "checkl":
        c_id, target_id = int(data[1]), int(data[2])
        game = games.get(c_id)
        if game:
            t_role = game['roles'].get(target_id, "Tinch Aholi")
            res = "KIRA!" if t_role == "Kira" else "Kira EMAS."
            bot.answer_callback_query(call.id, f"Tergov natijasi: {res}", show_alert=True)
            try:
                bot.send_video(call.from_user.id, VID_L_INVESTIGATE, caption=f"🕵️‍♂️ **L / Near Tergov Tahlili:** Bu shaxs **{res}**")
            except Exception:
                pass

    # SOICHIRO YAGAMI HIMOYA (2 marta, o'zini ham himoya qila oladi)
    elif action == "protect":
        c_id, target_id = int(data[1]), int(data[2])
        game = games.get(c_id)
        if game:
            uses = game['soichiro_uses'].get(call.from_user.id, 0)
            if uses > 0:
                game['soichiro_uses'][call.from_user.id] -= 1
                game['protected_player'] = target_id
                target_name = game['players'].get(target_id, "O'zingiz")
                bot.answer_callback_query(call.id, f"✅ {target_name} tuni bilan himoya ostida! (Qolgan limit: {uses - 1})")
            else:
                bot.answer_callback_query(call.id, "❌ Himoya qilish limiti (2 marta) tugagan!", show_alert=True)

    elif action == "misaeyes":
        c_id, target_id = int(data[1]), int(data[2])
        game = games.get(c_id)
        if game:
            prof = get_user_profile(call.from_user.id)
            if game['misa_uses'].get(call.from_user.id, 0) > 0:
                game['misa_uses'][call.from_user.id] -= 1
            elif "👁 Shinigami Ko'zlari" in prof['inventory']:
                prof['inventory'].remove("👁 Shinigami Ko'zlari")
            t_role = game['roles'].get(target_id, "Noma'lum")
            t_name = game['players'].get(target_id, "Noma'lum")
            bot.answer_callback_query(call.id, f"👁 Shinigami ko'zi orqali ko'rindi: {t_name} — {t_role}", show_alert=True)

    elif action == "melloattack":
        c_id, target_id = int(data[1]), int(data[2])
        game = games.get(c_id)
        if game:
            if target_id in game['alive']:
                t_name = game['players'].get(target_id, "Noma'lum")
                t_role = game['roles'].get(target_id, "Noma'lum")
                if t_role == "Kira":
                    game['alive'].remove(target_id)
                    bot.send_message(c_id, f"🔥 **MELLO PORTLASH YASADI!** {t_name}ga shafqatsiz xujum qildi — u aynan **KIRA** edi! 🎯")
                    prof = get_user_profile(call.from_user.id)
                    prof['coins'] += 150
                    if "🔥 Xavfli O'yinchi" not in prof['achievements']:
                        prof['achievements'].append("🔥 Xavfli O'yinchi")

                    check_kira_death_and_transfer(c_id, t_name)
                else:
                    game['mello_cd'][call.from_user.id] = 2
                    bot.send_message(c_id, f"🔥 **Mello** xato qildi va begunoh {t_name}ga hujum qildi... Portlash zoye ketdi! Mello 2 kecha harakatsiz qaladi.")
            bot.answer_callback_query(call.id, "Zarba berildi!")

    elif action == "block":
        c_id, target_id = int(data[1]), int(data[2])
        game = games.get(c_id)
        if game:
            game['blocked_player'] = target_id
            bot.answer_callback_query(call.id, "Yo'li tosildi!")

    elif action == "buy":
        item = data[1]
        prof = get_user_profile(call.from_user.id, call.from_user.first_name)
        if prof['coins'] >= 1000:
            if item == "eyes": prof['inventory'].append("👁 Shinigami Ko'zlari")
            elif item == "apple": prof['inventory'].append("🍎 Shinigami Olmasi")
            elif item == "notebook": prof['inventory'].append("📓 Kira Daftari")
            prof['coins'] -= 1000
            bot.answer_callback_query(call.id, "✅ Buyum arsenalingizga qo'shildi!", show_alert=True)
        else:
            bot.answer_callback_query(call.id, "❌ 1000 Coin yetarli emas!", show_alert=True)

    # KIYOMI TAKADA DYNAMIK FAKT
    elif action == "fakefact":
        c_id = int(data[1])
        game = games.get(c_id)
        if game and game['takada_uses'].get(call.from_user.id, 0) > 0:
            game['takada_uses'][call.from_user.id] -= 1

            target_id = random.choice(game['alive'])
            t_name = game['players'][target_id]
            t_role = game['roles'].get(target_id, "Tinch Aholi")

            chosen_type = random.choices(["fake", "partial", "real"], weights=[50, 30, 20], k=1)[0]

            if chosen_type == "fake":
                fake_roles = ["Kira", "L", "Soichiro Yagami", "Aizawa", "Misa"]
                if t_role in fake_roles: fake_roles.remove(t_role)
                msg = f"📺 **OAV EXCLUSIVE ANONS:** Takada jonli efirda shov-shuvli bayonot berdi! **{t_name}** tunda shubhali harakat qilgan va u **{random.choice(fake_roles)}** ekanligi aytilmoqda!"
            elif chosen_type == "partial":
                group_type = "Yovuzlar (Kira tarafdori)" if t_role in ["Kira", "Misa", "Teru Mikami"] else "Tergov guruhiga mansub"
                msg = f"📺 **OAV EXCLUSIVE ANONS:** Kiyomi Takadaning maxfiy tahlillariga ko'ra, **{t_name}** — **{group_type}** vakili!"
            else:
                msg = f"📺 **OAV EXCLUSIVE ANONS:** Maxfiy manbalar tasdiqlashicha, **{t_name}** aynan **{t_role}** rolida o'ynamoqda!"

            bot.send_message(c_id, f"{msg}\n\n🗣 *Guruhdagilar, bu xabar qanchalik haqiqat ekanligini muhokama qiling...*")
            bot.answer_callback_query(call.id, "OAV xabari jonli efirga uzatildi!")

    elif action == "aizawashot":
        if data[1] == "menu":
            c_id = int(data[2])
            game = games.get(c_id)
            if game and game['roles'].get(call.from_user.id) == "Aizawa":
                kb = types.InlineKeyboardMarkup(row_width=1)
                for t_id in game['alive']:
                    if t_id != call.from_user.id:
                        kb.add(types.InlineKeyboardButton(f"💥 {game['players'][t_id]}ni otish", callback_data=f"aizawashot_exec_{c_id}_{t_id}"))
                bot.send_message(call.from_user.id, "💥 **Aizawa:** Qurolni kimga qaratasiz?", reply_markup=kb)

        elif data[1] == "exec":
            c_id, target_id = int(data[2]), int(data[3])
            game = games.get(c_id)
            if game and game['roles'].get(call.from_user.id) == "Aizawa":
                game['aizawa_shots'][call.from_user.id] += 1
                shooter = game['players'][call.from_user.id]
                victim = game['players'][target_id]

                if game['roles'].get(target_id) == "Kira":
                    game['alive'].remove(target_id)
                    bot.send_message(c_id, f"💥 **Aizawa ({shooter})** ikkilanmay tepkini bosdi! {victim} yerga quladi — U AYNAN **KIRA** EDI!")
                    check_kira_death_and_transfer(c_id, victim)
                else:
                    game['alive'].remove(target_id)
                    game['alive'].remove(call.from_user.id)
                    bot.send_message(c_id, f"💥 **Aizawa ({shooter})** shoshqaloqlik qilib begunoh {victim}ni otib qo'ydi! Vijdon azobi va fojia tufayli **Aizawaning o'zi ham halok bo'ldi!**")

    elif action == "join":
        c_id = int(data[1])
        game = games.get(c_id)
        if game and game['status'] == 'waiting':
            if call.from_user.id not in game['players']:
                game['players'][call.from_user.id] = call.from_user.first_name
                get_user_profile(call.from_user.id, call.from_user.first_name)
                bot.answer_callback_query(call.id, "Siz safga qo'shildingiz!")

                kb = types.InlineKeyboardMarkup()
                kb.add(types.InlineKeyboardButton("✋ Qo'shilish", callback_data=f"join_{c_id}"))
                kb.add(types.InlineKeyboardButton("🚀 Boshlash", callback_data=f"start_{c_id}"))

                txt = get_lobby_text(c_id)
                try:
                    bot.edit_message_caption(chat_id=c_id, message_id=game['msg_id'], caption=txt, reply_markup=kb)
                except Exception:
                    try:
                        bot.edit_message_text(chat_id=c_id, message_id=game['msg_id'], text=txt, reply_markup=kb)
                    except Exception:
                        pass
            else:
                bot.answer_callback_query(call.id, "Siz allaqachon safdasiz!", show_alert=True)

    elif action == "start":
        c_id = int(data[1])
        game = games.get(c_id)
        if game and game['status'] == 'waiting':
            if len(game['players']) >= 3:
                start_game_logic(c_id)
            else:
                bot.answer_callback_query(call.id, "O'yin boshlanishi uchun kamida 3 kishi kerak!", show_alert=True)

    elif action == "target":
        c_id, target_id = int(data[1]), int(data[2])
        game = games.get(c_id)
        if game:
            game['pending_kills'].append(target_id)
            prof = get_user_profile(call.from_user.id)
            if len(game['pending_kills']) >= 2 and "📓 Kira Daftari" in prof['inventory']:
                prof['inventory'].remove("📓 Kira Daftari")
            bot.answer_callback_query(call.id, "Ism O'lim Daftariga muhrlandi...")

if __name__ == "__main__":
    threading.Thread(target=run_flask, daemon=True).start()
    bot.polling(none_stop=True)
    
    
    
