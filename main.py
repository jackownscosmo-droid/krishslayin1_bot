import os
import time
import random
import asyncio
import logging

try:
    from gTTS import gTTS
except ImportError:
    gTTS = None

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder, MessageHandler, 
    CallbackQueryHandler, filters, ContextTypes
)

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# Global Configuration
OWNER_ID = int(os.environ.get("OWNER_ID", "8821066459"))
MAIN_BOT_USERNAME = os.environ.get("MAIN_BOT_USERNAME", "krishslayin1_bot").lower().replace("@", "")
LOG_CHANNEL_ID = os.environ.get("LOG_CHANNEL_ID", None)

AUTHORIZED_ADMINS = set([8821066459, OWNER_ID])
GBANNED_USERS = set()
CHAT_TASKS = {}

# Global Cluster Storage
BOT_INSTANCES = []

# Global Reaction State across all bot instances
GLOBAL_CHAT_REACT_MODE = {}

REACTION_EMOJI = "🤣"

# Commands exclusive ONLY to Main Bot
MAIN_BOT_ONLY_COMMANDS = {
    "menu", "start", "panel", "mute", "unmute", "mutelist", 
    "gban", "ungban", "slayinpowergifted", "slayinpowertaken",
    "cluster", "getid", "ht", "join", "leave", "joinkrishslayin", "leavekrishslayin"
}

AUTOREPLY_LINES = [
    r"""बड़े दुःख के साथ हँसना पढ़ रहा है😂  𝐓ᴜ तेरी माँ रंडी 🤍😅🔥""",
    r"""𝙏𝙚𝙧𝙞 𝙢𝙖𝙖 𝙠𝙚 𝙝𝙤𝙨𝙙𝙚 𝙢𝙚 𝙡𝙖𝙩 𝙥𝙙𝙚𝙣𝙜𝙚 𝙗𝙝𝙤𝙩 𝙩𝙚𝙯 👻 😂👯😂👯😂👯 😂👯😂👯😂👯 😂👯😂👯😂👯""",
    r"""𝙏𝙀𝙍𝙄 𝙈𝘼 𝑑𝙄𝘿🇭🇻𝘼 𝙋𝙀𝙉𝙎𝙄𝙊𝙉 𝙃𝘼𝙉𝙀 𝙒𝘼𝙇𝙄 𝙍𝙉𝘿𝙄 🤣""",
    r"""तेरी maa की chut में ऐसा HACK lgaunga Light की speed में बच्चे देगी""",
    r"""𝑩𝑯𝑨𝑮 𝑹𝑨𝑵𝑫𝒀𝑲𝑬 𝑻𝑬𝑹𝑰 𝑴𝑨 𝑪𝑯𝑼𝑫𝑹𝑰 𝑯𝑨𝑰 ᯓ🏃🏻‍♀️‍➡️ᯓ🏃🏻‍♀️‍➡️ᯓ🏃🏻‍♀️‍➡️""",
    r"""𝘽𝙃𝘼𝙂𝘼 𝘽𝙃𝘼𝙂𝘼 𝙆𝙀 𝙈𝘼𝙍𝙐𝙉𝙂𝘼 🤣🩷🙌🏾"""
]

TARGET_LINES = [
    r"""˚∧＿∧   +        — ͟͞͞🥛 (  •‿• )つ  Special attack: teri mummy ka dudh 😂😂""",
    r"""𝙉𝙀𝙆𝘼𝘼𝘼𝙇 𝙈𝘼𝘿𝘼𝘼𝙍𝘾𝙃𝘿👍🏼👍🏼👍🏼👍🏼👍🏼""",
    r"""तेरी बहन का भोसड़ा 😂🤸🏻‍♂️😂🤸🏻‍♂️ 𝘾𝙃𝙐𝙋 𝙍𝙉𝘿𝙄𝙆𝙀"""
]

FLOOD_LINES = [
    r"""𝙏𝙚𝙧𝙞 𝙢𝙖𝙖 𝙠𝙚 𝙗𝙝𝙤𝙨𝙙𝙚 𝙢𝙚 𝙡𝙖𝙩 𝙥𝙙𝙚𝙣𝙜𝙚 𝙗𝙝𝙤𝙩 𝙩𝙚𝙯 👻 😂👯😂👯""",
    r"""तेरो ma ko चोदने k बाद उसको ऐसे चंद सितारए नजर आएंगे""",
    r"""😝 Beta 🥶 लंड 🔥 पकड़ 😡 muh 😜 pe 😁 रगड़ 😂"""
]

ROASTS_HI = [
    "Teri shakal dekh ke Telegram ka server bhi crash ho jaye!",
    "Itna dimaag agar sahi jagah lagaya hota toh aaj NASA me hota!"
]

ROASTS_ENG = [
    "You bring everyone so much joy... when you leave the room!",
    "Your brain is like the 404 error page—permanently missing content."
]

VALID_COMMANDS = {
    "start", "menu", "panel", "gcnc", "vgcnc", "stopgcnc",
    "target", "vtarget", "stoptarget", "spam", "stopspam",
    "flood", "vflood", "stopflood", "gcpfp", "stopgcpfp",
    "voiceflood", "stopvoiceflood", "mute", "unmute", "mutelist",
    "stripmedia", "stopstripmedia", "pfpstripper", "autoreply",
    "vautoreply", "stopautoreply", "reptts", "stopreptts",
    "clean", "togglereactall", "togglereact", "stopall",
    "scan", "ping", "getid", "status", "omg", "tts",
    "roasthi", "roasteng", "cluster", "broadcast",
    "slayinpowergifted", "slayinpowertaken", "slayinfor",
    "gban", "ungban", "ht", "join", "leave", "joinkrishslayin", "leavekrishslayin"
}

def get_chat_data(chat_id):
    if chat_id not in CHAT_TASKS:
        CHAT_TASKS[chat_id] = {
            "tasks": {},
            "muted": set(),
            "stripmedia": set(),
            "pfpstripper": False,
            "autoreply": {},
            "reptts": set()
        }
    return CHAT_TASKS[chat_id]

def is_admin(user_id):
    return user_id in AUTHORIZED_ADMINS or user_id == OWNER_ID

async def send_log(context: ContextTypes.DEFAULT_TYPE, text: str):
    if LOG_CHANNEL_ID:
        try:
            await context.bot.send_message(chat_id=int(LOG_CHANNEL_ID), text=text, parse_mode="Markdown")
        except Exception as e:
            logging.error(f"Failed to send log: {e}")

# --- Universal Reset & Absolute Stop ---

async def hard_stop_all(chat_id: int, context: ContextTypes.DEFAULT_TYPE, user_id: int):
    chat_data = get_chat_data(chat_id)
    
    for task_name, task in list(chat_data["tasks"].items()):
        task.cancel()
    chat_data["tasks"].clear()

    chat_data["muted"].clear()
    chat_data["stripmedia"].clear()
    chat_data["autoreply"].clear()
    chat_data["reptts"].clear()
    chat_data["pfpstripper"] = False
    GLOBAL_CHAT_REACT_MODE[chat_id] = None

    await send_log(context, f"🚨 *ABSOLUTE KILL SWITCH TRIGGERED*\nChat: `{chat_id}`\nAdmin/User: `{user_id}`")

# --- UI Helpers ---

def get_menu_keyboard(page: int):
    if page == 1:
        buttons = [
            [
                InlineKeyboardButton("COMBAT & WARFARE ⚔️", callback_data="menu_2"),
                InlineKeyboardButton("⛓️ DARK TARGETING 🎯", callback_data="menu_3")
            ],
            [
                InlineKeyboardButton("BLACKOUT CONTROL 🛡️", callback_data="menu_4"),
                InlineKeyboardButton("OWNER CONTROL 🎛️", callback_data="menu_5")
            ],
            [InlineKeyboardButton("🎛️ Open Control Panel", callback_data="open_panel")],
            [InlineKeyboardButton("❌ Close Menu", callback_data="menu_close")]
        ]
    else:
        buttons = [
            [InlineKeyboardButton("✝️ Main Menu", callback_data="menu_1")],
            [InlineKeyboardButton("❌ Close Menu", callback_data="menu_close")]
        ]
    return InlineKeyboardMarkup(buttons)

def get_menu_text(page: int):
    if page == 1:
        return (
            "KRISHSLAYIN ✝️ SYSTEM CORE ⚡\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            "⚙️ OPERATIONAL STATUS: Active & Synchronized\n"
            "🛡️ SECURITY ACCESS: Authorized Level\n\n"
            "Select a command module below to inspect system features."
        )
    elif page == 2:
        return (
            "⚔️ COMBAT & WARFARE\n"
            "────────────────────────────\n"
            "• +gcnc [spd] <name> — Coordinated title loop\n"
            "• +vgcnc [spd] <Title 1 | Title 2> — Title rotator\n"
            "• +stopgcnc — Halt active title loop\n"
            "• +target <user> — Mention loop\n"
            "• +vtarget <user> <text> — Custom mention loop\n"
            "• +stoptarget — Disarm targeting loop\n"
            "• +spam <text> — Multi-bot high-speed spam\n"
            "• +stopspam — EMERGENCY KILL-SWITCH (STOPS EVERYTHING)\n"
            "• +flood <user> — Mention flood\n"
            "• +vflood <user> <text> — Custom mention flood\n"
            "• +stopflood — Stop mention flood\n"
            "• +gcpfp — Group photo loop\n"
            "• +stopgcpfp — Stop photo loop\n"
            "• +voiceflood — Voice loop\n"
            "• +stopvoiceflood — Stop voice flood"
        )
    elif page == 3:
        return (
            "⛓️ TRAPS & TARGETING 🎯\n"
            "────────────────────────────\n"
            "• +panel — Interactive inline dashboard\n"
            "• +ht — Honeytrap (Shadow-mute with fake unmute button)\n"
            "• +mute <user> — Shadow-mute target\n"
            "• +unmute <user> — Unmute target\n"
            "• +mutelist — View muted users\n"
            "• +stripmedia <user> — Auto-delete media\n"
            "• +stopstripmedia — Disable media stripper\n"
            "• +pfpstripper on/off — Delete group PFP changes\n"
            "• +autoreply <user> — Auto-reply trap\n"
            "• +vautoreply <user> <msg> — Custom reply trap\n"
            "• +stopautoreply — Disarm auto-reply\n"
            "• +reptts <user> — Voice trap\n"
            "• +stopreptts — Disarm voice trap\n"
            "• +clean [count] — Purge recent messages\n"
            "• +togglereactall — Toggle reactions for ALL users\n"
            "• +togglereact — Toggle reactions for ADMINS ONLY\n"
            "• +stopall — Emergency Kill Switch"
        )
    elif page == 4:
        return (
            "🛠️ BLACKOUT & TOOLS\n"
            "────────────────────────────\n"
            "• +scan — Group scanner\n"
            "• +ping — Matrix latency test\n"
            "• +getid — Fetch numeric ID\n"
            "• +status — Cluster state\n"
            "• +omg — Extract view-once media to PM\n"
            "• +tts <text> — Text to speech\n"
            "• +roasthi <user> — Hindi roast\n"
            "• +roasteng <user> — English roast"
        )
    elif page == 5:
        admin_list = "\n".join([f"• {uid}" for uid in AUTHORIZED_ADMINS])
        return (
            "👑 OWNER CONTROLS\n"
            "────────────────────────────\n"
            "• +join <@bot_username> — Send specific bot to GC via invite link\n"
            "• +leave <@bot_username> — Remove specific bot from chat\n"
            "• +joinkrishslayin — Mass join all cluster bots\n"
            "• +leavekrishslayin — Mass leave all cluster bots\n"
            "• +cluster — Node telemetry\n"
            "• +broadcast <text> — Network broadcast\n"
            "• +slayinpowergifted <id> — Add admin\n"
            "• +slayinpowertaken <id> — Revoke admin\n"
            "• +slayinfor — List admins\n"
            "• +gban <user> — Global ban\n"
            "• +ungban <user> — Global unban\n\n"
            f"⚡ Active Admins:\n{admin_list}"
        )

# --- Callbacks ---

async def menu_callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    data = query.data
    
    if data == "fake_unmute":
        return await query.answer(
            text="🤣 Abee saale tu chutiya hai kya, mute tune lagaya jo tu hatayega!", 
            show_alert=True
        )

    await query.answer()
    
    if data == "menu_close":
        return await query.message.delete()
    elif data == "open_panel":
        keyboard = [
            [InlineKeyboardButton("Abort All Active Tasks 🚨", callback_data="stop_all")],
            [InlineKeyboardButton("✝️ Return to Main Menu", callback_data="menu_1")]
        ]
        return await query.edit_message_text("🎛️ BATTLE-DECK CONTROL PANEL:\nDirect chat override active.", reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")
    elif data == "stop_all":
        await hard_stop_all(query.message.chat_id, context, query.from_user.id)
        return await query.edit_message_text("🚨 ALL ACTIVE TASKS & TRAPS TERMINATED 100%.", reply_markup=get_menu_keyboard(1))
    elif data.startswith("menu_"):
        page = int(data.split("_")[1])
        await query.edit_message_text(get_menu_text(page), reply_markup=get_menu_keyboard(page), parse_mode="Markdown")

# --- Multi-Bot Cluster Combat Commands ---

async def cmd_gcnc(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id): return
    args = update.message.text.split()[1:]
    speed = 0.3
    name = "KRISHSLAYIN"

    if args:
        try:
            speed = float(args[0])
            name = " ".join(args[1:]) if len(args) > 1 else "KRISHSLAYIN"
        except ValueError:
            name = " ".join(args)

    chat_data = get_chat_data(update.effective_chat.id)
    if "gcnc" in chat_data["tasks"]: chat_data["tasks"]["gcnc"].cancel()

    async def multi_gcnc_loop():
        titles = [f"⚡ {name} ⚡", f"🔥 {name} 🔥", f"👑 {name} 👑"]
        title_idx = 0
        bot_idx = 0
        total_bots = max(1, len(BOT_INSTANCES))
        while True:
            current_bot = BOT_INSTANCES[bot_idx % total_bots] if BOT_INSTANCES else context.bot
            try:
                await current_bot.set_chat_title(chat_id=update.effective_chat.id, title=titles[title_idx % len(titles)])
                title_idx += 1
            except Exception: pass
            bot_idx += 1
            await asyncio.sleep(speed)

    task = asyncio.create_task(multi_gcnc_loop())
    chat_data["tasks"]["gcnc"] = task
    await context.bot.send_message(chat_id=update.effective_chat.id, text=f"⚔️ Cluster Bots engaged in GCNC Loop (Speed: {speed}s).")

async def cmd_vgcnc(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id): return
    raw_text = update.message.text.replace("+vgcnc", "").strip()
    parts = raw_text.split(" ", 1)
    
    speed = 0.3
    titles_raw = ""

    if len(parts) > 0:
        try:
            speed = float(parts[0])
            titles_raw = parts[1] if len(parts) > 1 else ""
        except ValueError:
            titles_raw = raw_text

    titles = [t.strip() for t in titles_raw.split("|") if t.strip()]
    if not titles: return await context.bot.send_message(chat_id=update.effective_chat.id, text="Usage: +vgcnc [speed] Title 1 | Title 2")

    chat_data = get_chat_data(update.effective_chat.id)
    if "gcnc" in chat_data["tasks"]: chat_data["tasks"]["gcnc"].cancel()

    async def multi_vgcnc_loop():
        title_idx = 0
        bot_idx = 0
        total_bots = max(1, len(BOT_INSTANCES))
        while True:
            current_bot = BOT_INSTANCES[bot_idx % total_bots] if BOT_INSTANCES else context.bot
            try:
                await current_bot.set_chat_title(chat_id=update.effective_chat.id, title=titles[title_idx % len(titles)])
                title_idx += 1
            except Exception: pass
            bot_idx += 1
            await asyncio.sleep(speed)

    task = asyncio.create_task(multi_vgcnc_loop())
    chat_data["tasks"]["gcnc"] = task
    await context.bot.send_message(chat_id=update.effective_chat.id, text=f"⚡ Cluster Bots engaged in VGCNC Rotator (Speed: {speed}s).")

async def cmd_stopgcnc(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_data = get_chat_data(update.effective_chat.id)
    if "gcnc" in chat_data["tasks"]:
        chat_data["tasks"]["gcnc"].cancel()
        del chat_data["tasks"]["gcnc"]
        await context.bot.send_message(chat_id=update.effective_chat.id, text="🛑 Title loop disarmed across all cluster bots.")

async def cmd_spam(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id): return
    text = " ".join(update.message.text.split()[1:])
    if not text: return await context.bot.send_message(chat_id=update.effective_chat.id, text="Usage: +spam <text>")
    chat_data = get_chat_data(update.effective_chat.id)
    if "spam" in chat_data["tasks"]: chat_data["tasks"]["spam"].cancel()

    async def multi_spam_loop():
        bot_idx = 0
        total_bots = max(1, len(BOT_INSTANCES))
        while True:
            current_bot = BOT_INSTANCES[bot_idx % total_bots] if BOT_INSTANCES else context.bot
            try: await current_bot.send_message(chat_id=update.effective_chat.id, text=text)
            except Exception: pass
            bot_idx += 1
            await asyncio.sleep(0.12)

    task = asyncio.create_task(multi_spam_loop())
    chat_data["tasks"]["spam"] = task

async def cmd_stopspam(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id): return
    await hard_stop_all(update.effective_chat.id, context, update.effective_user.id)
    await context.bot.send_message(
        chat_id=update.effective_chat.id, 
        text="🛑 STRICT EMERGENCY STOP: All active tasks, spam, GCNC, traps, and loops have been KILLED instantly!"
    )

async def cmd_target(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id): return
    args = update.message.text.split()[1:]
    user = args[0] if args else "@target"
    chat_data = get_chat_data(update.effective_chat.id)
    if "target" in chat_data["tasks"]: chat_data["tasks"]["target"].cancel()

    async def multi_target_loop():
        bot_idx = 0
        total_bots = max(1, len(BOT_INSTANCES))
        while True:
            current_bot = BOT_INSTANCES[bot_idx % total_bots] if BOT_INSTANCES else context.bot
            line = random.choice(TARGET_LINES)
            try: await current_bot.send_message(chat_id=update.effective_chat.id, text=f"{user}\n{line}")
            except Exception: pass
            bot_idx += 1
            await asyncio.sleep(0.2)

    task = asyncio.create_task(multi_target_loop())
    chat_data["tasks"]["target"] = task

async def cmd_vtarget(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id): return
    args = update.message.text.split()[1:]
    if len(args) < 2: return await context.bot.send_message(chat_id=update.effective_chat.id, text="Usage: +vtarget <user> <text>")
    user, custom_text = args[0], " ".join(args[1:])
    chat_data = get_chat_data(update.effective_chat.id)
    if "target" in chat_data["tasks"]: chat_data["tasks"]["target"].cancel()

    async def multi_vtarget_loop():
        bot_idx = 0
        total_bots = max(1, len(BOT_INSTANCES))
        while True:
            current_bot = BOT_INSTANCES[bot_idx % total_bots] if BOT_INSTANCES else context.bot
            try: await current_bot.send_message(chat_id=update.effective_chat.id, text=f"{user} {custom_text}")
            except Exception: pass
            bot_idx += 1
            await asyncio.sleep(0.2)

    task = asyncio.create_task(multi_vtarget_loop())
    chat_data["tasks"]["target"] = task

async def cmd_stoptarget(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_data = get_chat_data(update.effective_chat.id)
    if "target" in chat_data["tasks"]:
        chat_data["tasks"]["target"].cancel()
        del chat_data["tasks"]["target"]
        await context.bot.send_message(chat_id=update.effective_chat.id, text="🛑 Targeting disarmed.")

async def cmd_flood(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id): return
    args = update.message.text.split()[1:]
    user = args[0] if args else "@target"
    chat_data = get_chat_data(update.effective_chat.id)
    if "flood" in chat_data["tasks"]: chat_data["tasks"]["flood"].cancel()

    async def multi_flood_loop():
        bot_idx = 0
        total_bots = max(1, len(BOT_INSTANCES))
        while True:
            for line in FLOOD_LINES:
                current_bot = BOT_INSTANCES[bot_idx % total_bots] if BOT_INSTANCES else context.bot
                try: await current_bot.send_message(chat_id=update.effective_chat.id, text=f"{user}\n{line}")
                except Exception: pass
                bot_idx += 1
                await asyncio.sleep(0.15)

    task = asyncio.create_task(multi_flood_loop())
    chat_data["tasks"]["flood"] = task

async def cmd_vflood(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id): return
    args = update.message.text.split()[1:]
    if len(args) < 2: return await context.bot.send_message(chat_id=update.effective_chat.id, text="Usage: +vflood <user> <text>")
    user, text = args[0], " ".join(args[1:])
    chat_data = get_chat_data(update.effective_chat.id)
    if "flood" in chat_data["tasks"]: chat_data["tasks"]["flood"].cancel()

    async def multi_vflood_loop():
        bot_idx = 0
        total_bots = max(1, len(BOT_INSTANCES))
        while True:
            current_bot = BOT_INSTANCES[bot_idx % total_bots] if BOT_INSTANCES else context.bot
            try: await current_bot.send_message(chat_id=update.effective_chat.id, text=f"🌊 {user} {text}")
            except Exception: pass
            bot_idx += 1
            await asyncio.sleep(0.15)

    task = asyncio.create_task(multi_vflood_loop())
    chat_data["tasks"]["flood"] = task

async def cmd_stopflood(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_data = get_chat_data(update.effective_chat.id)
    if "flood" in chat_data["tasks"]:
        chat_data["tasks"]["flood"].cancel()
        del chat_data["tasks"]["flood"]
        await context.bot.send_message(chat_id=update.effective_chat.id, text="🛑 Flood stopped.")

async def cmd_gcpfp(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id): return
    reply = update.message.reply_to_message
    if not reply or not reply.photo: return await context.bot.send_message(chat_id=update.effective_chat.id, text="Reply to an image.")
    file_id = reply.photo[-1].file_id
    chat_data = get_chat_data(update.effective_chat.id)
    if "gcpfp" in chat_data["tasks"]: chat_data["tasks"]["gcpfp"].cancel()

    async def multi_photo_loop():
        bot_idx = 0
        total_bots = max(1, len(BOT_INSTANCES))
        while True:
            current_bot = BOT_INSTANCES[bot_idx % total_bots] if BOT_INSTANCES else context.bot
            try: await current_bot.set_chat_photo(chat_id=update.effective_chat.id, photo=file_id)
            except Exception: pass
            bot_idx += 1
            await asyncio.sleep(3)

    task = asyncio.create_task(multi_photo_loop())
    chat_data["tasks"]["gcpfp"] = task

async def cmd_stopgcpfp(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_data = get_chat_data(update.effective_chat.id)
    if "gcpfp" in chat_data["tasks"]:
        chat_data["tasks"]["gcpfp"].cancel()
        del chat_data["tasks"]["gcpfp"]
        await context.bot.send_message(chat_id=update.effective_chat.id, text="🛑 Photo loop disarmed.")

async def cmd_voiceflood(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id): return
    reply = update.message.reply_to_message
    if not reply or not (reply.voice or reply.audio): return await context.bot.send_message(chat_id=update.effective_chat.id, text="Reply to audio/voice.")
    file_id = (reply.voice or reply.audio).file_id
    chat_data = get_chat_data(update.effective_chat.id)
    if "voiceflood" in chat_data["tasks"]: chat_data["tasks"]["voiceflood"].cancel()

    async def multi_voice_loop():
        bot_idx = 0
        total_bots = max(1, len(BOT_INSTANCES))
        while True:
            current_bot = BOT_INSTANCES[bot_idx % total_bots] if BOT_INSTANCES else context.bot
            try: await current_bot.send_voice(chat_id=update.effective_chat.id, voice=file_id)
            except Exception: pass
            bot_idx += 1
            await asyncio.sleep(0.2)

    task = asyncio.create_task(multi_voice_loop())
    chat_data["tasks"]["voiceflood"] = task

async def cmd_stopvoiceflood(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_data = get_chat_data(update.effective_chat.id)
    if "voiceflood" in chat_data["tasks"]:
        chat_data["tasks"]["voiceflood"].cancel()
        del chat_data["tasks"]["voiceflood"]
        await context.bot.send_message(chat_id=update.effective_chat.id, text="🛑 Voice flood stopped.")

# --- Moderation & Traps Commands ---

async def cmd_ht(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id): return
    reply = update.message.reply_to_message
    args = update.message.text.split()[1:]
    
    target_user = reply.from_user if reply else None
    target_id = target_user.id if target_user else (int(args[0]) if args and args[0].isdigit() else None)

    if not target_id: 
        return await context.bot.send_message(
            chat_id=update.effective_chat.id, 
            text="⚠️ Reply to target user's message or pass User ID."
        )

    get_chat_data(update.effective_chat.id)["muted"].add(target_id)
    target_mention = f"@{target_user.username}" if (target_user and target_user.username) else f"`{target_id}`"
    
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("🔊 Tap to Unmute Yourself", callback_data="fake_unmute")]
    ])
    
    await context.bot.send_message(
        chat_id=update.effective_chat.id, 
        text=f"🔇 USER SHADOW-MUTED: {target_mention}",
        reply_markup=keyboard,
        parse_mode="Markdown"
    )

async def cmd_mute(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id): return
    reply = update.message.reply_to_message
    args = update.message.text.split()[1:]
    target_id = reply.from_user.id if reply else (int(args[0]) if args and args[0].isdigit() else None)
    if not target_id: return await context.bot.send_message(chat_id=update.effective_chat.id, text="Reply to target or pass User ID.")
    get_chat_data(update.effective_chat.id)["muted"].add(target_id)
    await context.bot.send_message(chat_id=update.effective_chat.id, text=f"🔇 Target {target_id} shadow-muted.")

async def cmd_unmute(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id): return
    reply = update.message.reply_to_message
    args = update.message.text.split()[1:]
    target_id = reply.from_user.id if reply else (int(args[0]) if args and args[0].isdigit() else None)
    if not target_id: return await context.bot.send_message(chat_id=update.effective_chat.id, text="Reply to target or pass User ID.")
    get_chat_data(update.effective_chat.id)["muted"].discard(target_id)
    await context.bot.send_message(chat_id=update.effective_chat.id, text=f"🔊 Target {target_id} unmuted.")

async def cmd_mutelist(update: Update, context: ContextTypes.DEFAULT_TYPE):
    muted = get_chat_data(update.effective_chat.id)["muted"]
    text = "🔇 MUTED TARGETS:\n" + "\n".join([f"• {uid}" for uid in muted]) if muted else "No muted users."
    await context.bot.send_message(chat_id=update.effective_chat.id, text=text)

async def cmd_stripmedia(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id): return
    reply = update.message.reply_to_message
    args = update.message.text.split()[1:]
    target_id = reply.from_user.id if reply else (int(args[0]) if args and args[0].isdigit() else None)
    if not target_id: return await context.bot.send_message(chat_id=update.effective_chat.id, text="Reply to target or pass User ID.")
    get_chat_data(update.effective_chat.id)["stripmedia"].add(target_id)
    await context.bot.send_message(chat_id=update.effective_chat.id, text=f"✂️ Media stripper active on {target_id}.")

async def cmd_stopstripmedia(update: Update, context: ContextTypes.DEFAULT_TYPE):
    get_chat_data(update.effective_chat.id)["stripmedia"].clear()
    await context.bot.send_message(chat_id=update.effective_chat.id, text="✂️ Media stripper disarmed.")

async def cmd_pfpstripper(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id): return
    args = update.message.text.split()[1:]
    state = args[0].lower() == "on" if args else False
    get_chat_data(update.effective_chat.id)["pfpstripper"] = state
    await context.bot.send_message(chat_id=update.effective_chat.id, text=f"🖼️ PFP Stripper: {state}")

async def cmd_autoreply(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id): return
    reply = update.message.reply_to_message
    args = update.message.text.split()[1:]
    
    target_id = None
    target_username = None

    if reply and reply.from_user:
        target_id = reply.from_user.id
    elif args:
        if args[0].isdigit():
            target_id = int(args[0])
        elif args[0].startswith("@"):
            target_username = args[0].lower().replace("@", "")

    if not target_id and not target_username:
        return await context.bot.send_message(chat_id=update.effective_chat.id, text="Reply to target, pass User ID, or mention @username.")

    target_key = target_id if target_id else target_username
    get_chat_data(update.effective_chat.id)["autoreply"][target_key] = "RANDOM_LINES"
    await context.bot.send_message(chat_id=update.effective_chat.id, text=f"🤖 Auto-reply trap active on {args[0] if args else target_id}.")

async def cmd_vautoreply(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id): return
    args = update.message.text.split()[1:]
    if len(args) < 2: return await context.bot.send_message(chat_id=update.effective_chat.id, text="Usage: +vautoreply <user/id/@username> <msg>")
    
    target_input = args[0]
    msg = " ".join(args[1:])
    target_key = int(target_input) if target_input.isdigit() else target_input.lower().replace("@", "")

    get_chat_data(update.effective_chat.id)["autoreply"][target_key] = msg
    await context.bot.send_message(chat_id=update.effective_chat.id, text=f"🤖 Custom auto-reply trap active on {target_input}.")

async def cmd_stopautoreply(update: Update, context: ContextTypes.DEFAULT_TYPE):
    get_chat_data(update.effective_chat.id)["autoreply"].clear()
    await context.bot.send_message(chat_id=update.effective_chat.id, text="🛑 Auto-reply trap disarmed.")

async def cmd_reptts(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id): return
    reply = update.message.reply_to_message
    args = update.message.text.split()[1:]
    target_id = reply.from_user.id if reply else (int(args[0]) if args and args[0].isdigit() else None)
    if not target_id: return await context.bot.send_message(chat_id=update.effective_chat.id, text="Reply to target or pass User ID.")
    get_chat_data(update.effective_chat.id)["reptts"].add(target_id)
    await context.bot.send_message(chat_id=update.effective_chat.id, text=f"🗣️ Voice trap active on {target_id}.")

async def cmd_stopreptts(update: Update, context: ContextTypes.DEFAULT_TYPE):
    get_chat_data(update.effective_chat.id)["reptts"].clear()
    await context.bot.send_message(chat_id=update.effective_chat.id, text="🛑 Voice trap disarmed.")

async def cmd_clean(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id): return
    args = update.message.text.split()[1:]
    count = int(args[0]) if args and args[0].isdigit() else 10
    msg_id = update.message.message_id
    deleted = 0
    for i in range(count + 1):
        try:
            await context.bot.delete_message(chat_id=update.effective_chat.id, message_id=msg_id - i)
            deleted += 1
        except Exception: pass
    status = await context.bot.send_message(chat_id=update.effective_chat.id, text=f"🧹 Purged {deleted} messages.")
    await asyncio.sleep(2)
    try: await status.delete()
    except Exception: pass

# --- Universal Synchronized Reactions ---

async def cmd_togglereactall(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id): return
    chat_id = update.effective_chat.id
    current_mode = GLOBAL_CHAT_REACT_MODE.get(chat_id)
    
    if current_mode == "all":
        GLOBAL_CHAT_REACT_MODE[chat_id] = None
        await context.bot.send_message(chat_id=chat_id, text="❌ Auto-Reaction for ALL users Disabled.")
    else:
        GLOBAL_CHAT_REACT_MODE[chat_id] = "all"
        await context.bot.send_message(chat_id=chat_id, text="✅ Auto-Reaction Enabled for ALL users!")

async def cmd_togglereact(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id): return
    chat_id = update.effective_chat.id
    current_mode = GLOBAL_CHAT_REACT_MODE.get(chat_id)

    if current_mode == "admin":
        GLOBAL_CHAT_REACT_MODE[chat_id] = None
        await context.bot.send_message(chat_id=chat_id, text="❌ Admin Auto-Reaction Disabled.")
    else:
        GLOBAL_CHAT_REACT_MODE[chat_id] = "admin"
        await context.bot.send_message(chat_id=chat_id, text="✅ Auto-Reaction Enabled for OWNER & ADMINS only!")

async def cmd_stopall(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id): return
    await hard_stop_all(update.effective_chat.id, context, update.effective_user.id)
    await context.bot.send_message(chat_id=update.effective_chat.id, text="🚨 ALL THREADS, TRAPS & ACTIVE TASKS KILLED SUCCESSFULLY!")

# --- Utilities & Owner Commands ---

async def cmd_scan(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat = update.effective_chat
    members = await chat.get_member_count()
    await context.bot.send_message(chat_id=update.effective_chat.id, text=f"📊 CHAT MATRIX SCAN:\n• Title: {chat.title}\n• ID: {chat.id}\n• Members: {members}")

async def cmd_ping(update: Update, context: ContextTypes.DEFAULT_TYPE):
    start = time.time()
    msg = await context.bot.send_message(chat_id=update.effective_chat.id, text="📡 Pinging cluster...")
    latency = round((time.time() - start) * 1000, 2)
    indicator = "🟢" if latency <= 1000.0 else "🔴"
    await msg.edit_text(f"📶 LATENCY TELEMETRY: {latency}ms {indicator}")

async def cmd_getid(update: Update, context: ContextTypes.DEFAULT_TYPE):
    target = update.message.reply_to_message.from_user if update.message.reply_to_message else update.effective_user
    await context.bot.send_message(chat_id=update.effective_chat.id, text=f"🆔 User ID: {target.id}\n💬 Chat ID: {update.effective_chat.id}")

async def cmd_status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    tasks = len(get_chat_data(update.effective_chat.id)["tasks"])
    await context.bot.send_message(chat_id=update.effective_chat.id, text=f"⚙️ CLUSTER STATE: Active ({len(BOT_INSTANCES)} Bots Connected)\n🔥 Active Tasks: {tasks}")

async def cmd_omg(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id): return
    reply = update.message.reply_to_message
    if not reply or not (reply.photo or reply.video or reply.document or reply.voice):
        return await context.bot.send_message(chat_id=update.effective_chat.id, text="⚠️ Reply to a media message with +omg.")

    status_msg = await context.bot.send_message(chat_id=update.effective_chat.id, text="⚡ Extracting media...")
    try:
        if reply.photo: file_obj = await reply.photo[-1].get_file()
        elif reply.video: file_obj = await reply.video.get_file()
        elif reply.document: file_obj = await reply.document.get_file()
        elif reply.voice: file_obj = await reply.voice.get_file()

        file_bytes = await file_obj.download_as_bytearray()
        await context.bot.send_message(chat_id=update.effective_user.id, text=f"🔓 MEDIA EXTRACTED VIA KRISHSLAYIN ✝️\nChat: {update.effective_chat.title}")
        
        if reply.photo:
            await context.bot.send_photo(chat_id=update.effective_user.id, photo=bytes(file_bytes))
        else:
            await context.bot.send_document(chat_id=update.effective_user.id, document=bytes(file_bytes))
            
        await status_msg.edit_text("✅ Saved to your PM!")
    except Exception as e:
        await status_msg.edit_text(f"❌ Extraction Error: {str(e)}")

async def cmd_tts(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = " ".join(update.message.text.split()[1:])
    if not text: return await context.bot.send_message(chat_id=update.effective_chat.id, text="Usage: +tts <text>")
    if gTTS is None:
        return await context.bot.send_message(chat_id=update.effective_chat.id, text=f"🔊 TTS Voice: {text}")
    try:
        tts = gTTS(text=text, lang="hi")
        tts.save("tts.mp3")
        await context.bot.send_voice(chat_id=update.effective_chat.id, voice=open("tts.mp3", "rb"))
    except Exception:
        await context.bot.send_message(chat_id=update.effective_chat.id, text=f"🔊 TTS Voice: {text}")

async def cmd_roasthi(update: Update, context: ContextTypes.DEFAULT_TYPE):
    args = update.message.text.split()[1:]
    target_name = None
    if update.message.reply_to_message and update.message.reply_to_message.from_user:
        target_name = f"@{update.message.reply_to_message.from_user.username}" if update.message.reply_to_message.from_user.username else update.message.reply_to_message.from_user.first_name
    elif args:
        target_name = " ".join(args)
        
    roast_text = random.choice(ROASTS_HI)
    text = f"🔥 {target_name} {roast_text}" if target_name else f"🔥 {roast_text}"
    await context.bot.send_message(chat_id=update.effective_chat.id, text=text)

async def cmd_roasteng(update: Update, context: ContextTypes.DEFAULT_TYPE):
    args = update.message.text.split()[1:]
    target_name = None
    if update.message.reply_to_message and update.message.reply_to_message.from_user:
        target_name = f"@{update.message.reply_to_message.from_user.username}" if update.message.reply_to_message.from_user.username else update.message.reply_to_message.from_user.first_name
    elif args:
        target_name = " ".join(args)
        
    roast_text = random.choice(ROASTS_ENG)
    text = f"🔥 {target_name} {roast_text}" if target_name else f"🔥 {roast_text}"
    await context.bot.send_message(chat_id=update.effective_chat.id, text=text)

# --- Dynamic Cluster Join/Leave Commands ---

async def cmd_join(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != OWNER_ID: return
    args = update.message.text.split()[1:]
    if len(args) < 1:
        return await context.bot.send_message(chat_id=update.effective_chat.id, text="Usage: +join <@bot_username> [invite_link]")
    
    target_bot_username = args[0].lower().replace("@", "")
    invite_link = args[1] if len(args) > 1 else None
    
    found = False
    for bot in BOT_INSTANCES:
        me = await bot.get_me()
        if me.username.lower() == target_bot_username:
            found = True
            try:
                if invite_link:
                    await bot.join_chat(invite_link)
                else:
                    await bot.send_message(chat_id=update.effective_chat.id, text=f"✅ Bot @{me.username} active in chat.")
                await context.bot.send_message(chat_id=update.effective_chat.id, text=f"✅ Bot @{me.username} successfully processed join.")
            except Exception as e:
                await context.bot.send_message(chat_id=update.effective_chat.id, text=f"❌ Failed to join with @{me.username}: {e}")
            break
            
    if not found:
        await context.bot.send_message(chat_id=update.effective_chat.id, text=f"⚠️ Bot @{target_bot_username} cluster instance me nahi mila.")

async def cmd_leave(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != OWNER_ID: return
    args = update.message.text.split()[1:]
    if not args:
        return await context.bot.send_message(chat_id=update.effective_chat.id, text="Usage: +leave <@bot_username>")
    
    target_bot_username = args[0].lower().replace("@", "")
    
    found = False
    for bot in BOT_INSTANCES:
        me = await bot.get_me()
        if me.username.lower() == target_bot_username:
            found = True
            try:
                await bot.leave_chat(chat_id=update.effective_chat.id)
                await context.bot.send_message(chat_id=update.effective_chat.id, text=f"👋 Bot @{me.username} left the chat.")
            except Exception as e:
                await context.bot.send_message(chat_id=update.effective_chat.id, text=f"❌ Failed to leave: {e}")
            break
            
    if not found:
        await context.bot.send_message(chat_id=update.effective_chat.id, text=f"⚠️ Bot @{target_bot_username} cluster instance me nahi mila.")

async def cmd_joinkrishslayin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != OWNER_ID: return
    args = update.message.text.split()[1:]
    invite_link = args[0] if args else None
    
    joined = 0
    failed = 0
    for bot in BOT_INSTANCES:
        try:
            if invite_link:
                await bot.join_chat(invite_link)
            joined += 1
        except Exception:
            failed += 1
            
    await context.bot.send_message(
        chat_id=update.effective_chat.id, 
        text=f"🌐 MASS JOIN COMPLETE:\n✅ Connected: {joined}\n❌ Failed: {failed}"
    )

async def cmd_leavekrishslayin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != OWNER_ID: return
    await context.bot.send_message(chat_id=update.effective_chat.id, text="👋 Initiating Mass Leave across all cluster bots...")
    
    for bot in BOT_INSTANCES:
        try:
            await bot.leave_chat(chat_id=update.effective_chat.id)
        except Exception: pass

# --- Owner Telemetry & Management Commands ---

async def cmd_cluster(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != OWNER_ID: return

    chat_tasks = len(get_chat_data(update.effective_chat.id)["tasks"])
    node_lines = []
    active_nodes = 0
    total_nodes = len(BOT_INSTANCES)

    for idx, bot in enumerate(BOT_INSTANCES, start=1):
        try:
            me = await bot.get_me()
            node_name = f"@{me.username}"
            is_main = (MAIN_BOT_USERNAME == "" or me.username.lower() == MAIN_BOT_USERNAME)
            tag = "[MAIN]" if is_main else "[ONLINE]"
            
            node_lines.append(f"├─ Node-0{idx} : 🟢 {node_name} {tag}")
            active_nodes += 1
        except Exception:
            node_lines.append(f"├─ Node-0{idx} : 🔴 [OFFLINE / ERROR]")

    if node_lines:
        node_lines[-1] = node_lines[-1].replace("├─", "└─")

    node_matrix = "\n".join(node_lines)
    
    cluster_text = (
        "🌐 SYSTEM CLUSTER TELEMETRY\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"Status          : ACTIVE 🟢\n"
        f"Connected Nodes : {active_nodes:02d} / {total_nodes:02d}\n"
        f"Active Tasks    : {chat_tasks:02d}\n\n"
        "🤖 NODE MATRIX DISTRIBUTOR\n"
        f"{node_matrix}\n\n"
        f"👤 Authorized Operator : {OWNER_ID}\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    )

    await context.bot.send_message(chat_id=update.effective_chat.id, text=cluster_text)

async def cmd_broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != OWNER_ID: return
    text = " ".join(update.message.text.split()[1:])
    if not text: return await context.bot.send_message(chat_id=update.effective_chat.id, text="Usage: +broadcast <text>")
    await context.bot.send_message(chat_id=update.effective_chat.id, text=f"📢 GLOBAL BROADCAST SENT:\n{text}")

async def cmd_slayinpowergifted(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != OWNER_ID: return
    args = update.message.text.split()[1:]
    target_id = int(args[0]) if args and args[0].isdigit() else (update.message.reply_to_message.from_user.id if update.message.reply_to_message else None)
    if target_id:
        AUTHORIZED_ADMINS.add(target_id)
        await context.bot.send_message(chat_id=update.effective_chat.id, text=f"👑 Admin rights granted to {target_id}.")

async def cmd_slayinpowertaken(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != OWNER_ID: return
    args = update.message.text.split()[1:]
    target_id = int(args[0]) if args and args[0].isdigit() else (update.message.reply_to_message.from_user.id if update.message.reply_to_message else None)
    if target_id and target_id != OWNER_ID:
        AUTHORIZED_ADMINS.discard(target_id)
        await context.bot.send_message(chat_id=update.effective_chat.id, text=f"🗑️ Admin rights revoked from {target_id}.")

async def cmd_slayinfor(update: Update, context: ContextTypes.DEFAULT_TYPE):
    admin_list = "\n".join([f"• {uid}" for uid in AUTHORIZED_ADMINS])
    await context.bot.send_message(chat_id=update.effective_chat.id, text=f"👑 AUTHORIZED ADMINS:\n{admin_list}")

async def cmd_gban(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != OWNER_ID: return
    reply = update.message.reply_to_message
    args = update.message.text.split()[1:]
    target_id = reply.from_user.id if reply else (int(args[0]) if args and args[0].isdigit() else None)
    if not target_id: return await context.bot.send_message(chat_id=update.effective_chat.id, text="Reply to target user or pass ID.")
    GBANNED_USERS.add(target_id)
    await context.bot.send_message(chat_id=update.effective_chat.id, text=f"🚫 Target {target_id} globally blacklisted.")
    await send_log(context, f"🚫 *GLOBAL BAN APPLIED*\nTarget: `{target_id}`\nAdmin: `{update.effective_user.id}`")

async def cmd_ungban(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != OWNER_ID: return
    reply = update.message.reply_to_message
    args = update.message.text.split()[1:]
    target_id = reply.from_user.id if reply else (int(args[0]) if args and args[0].isdigit() else None)
    if not target_id: return await context.bot.send_message(chat_id=update.effective_chat.id, text="Reply to target user or pass ID.")
    GBANNED_USERS.discard(target_id)
    await context.bot.send_message(chat_id=update.effective_chat.id, text=f"✅ Target {target_id} removed from blacklist.")
    await send_log(context, f"✅ *GLOBAL UNBAN APPLIED*\nTarget: `{target_id}`\nAdmin: `{update.effective_user.id}`")

# --- Global Engine Router ---

async def global_message_router(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.from_user: return
    user_id = update.message.from_user.id
    username = update.message.from_user.username.lower() if update.message.from_user.username else ""
    chat_id = update.effective_chat.id
    chat_data = get_chat_data(chat_id)
    text = update.message.text.strip() if update.message.text else ""

    bot_username = (await context.bot.get_me()).username.lower()
    is_main_bot = (MAIN_BOT_USERNAME == "" or bot_username == MAIN_BOT_USERNAME)

    # Check command validity
    cmd_name = ""
    is_valid_cmd = False
    if text.startswith("+"):
        possible_cmd = text.split()[0][1:].lower()
        if possible_cmd in VALID_COMMANDS:
            cmd_name = possible_cmd
            is_valid_cmd = True

    # Auto Delete Owner's Command Trigger Message
    if user_id == OWNER_ID and is_valid_cmd:
        try: await update.message.delete()
        except Exception: pass

    # Photo Stripper Trap
    if chat_data.get("pfpstripper") and update.message.new_chat_photo:
        try: 
            await context.bot.delete_message(chat_id=chat_id, message_id=update.message.message_id)
            return
        except Exception: pass

    # Muted & Blacklisted Enforcement
    if user_id in GBANNED_USERS or user_id in chat_data["muted"]:
        try: return await update.message.delete()
        except Exception: pass

    # Media Stripper Enforcement
    if user_id in chat_data["stripmedia"] and (update.message.photo or update.message.video or update.message.document):
        try: return await update.message.delete()
        except Exception: pass

    # Auto-Reply Trap
    autoreply_map = chat_data.get("autoreply", {})
    if user_id in autoreply_map or username in autoreply_map:
        target_key = user_id if user_id in autoreply_map else username
        custom_val = autoreply_map[target_key]
        reply_text = random.choice(AUTOREPLY_LINES) if custom_val == "RANDOM_LINES" else custom_val
        try: 
            await context.bot.send_message(
                chat_id=chat_id, 
                text=reply_text, 
                reply_to_message_id=update.message.message_id
            )
        except Exception: pass

    # Audio Repeat Trap (reptts)
    if user_id in chat_data["reptts"] and text and gTTS is not None:
        try:
            tts = gTTS(text=text, lang="hi")
            tts.save("reptts.mp3")
            await context.bot.send_voice(chat_id=chat_id, voice=open("reptts.mp3", "rb"))
        except Exception: pass

    # Synchronized Reaction Logic
    react_mode = GLOBAL_CHAT_REACT_MODE.get(chat_id)
    if react_mode is not None and not is_valid_cmd:
        should_react = False
        if react_mode == "all":
            should_react = True
        elif react_mode == "admin":
            if is_admin(user_id):
                should_react = True

        if should_react:
            try:
                await context.bot.set_message_reaction(
                    chat_id=chat_id, 
                    message_id=update.message.message_id, 
                    reaction=[REACTION_EMOJI]
                )
            except Exception: pass

    # Command Execution Engine
    if is_valid_cmd:
        if cmd_name in MAIN_BOT_ONLY_COMMANDS and not is_main_bot:
            return

        if user_id != OWNER_ID:
            try: await update.message.delete()
            except Exception: pass

        routes = {
            "start": lambda u, c: c.bot.send_message(chat_id=chat_id, text=get_menu_text(1), reply_markup=get_menu_keyboard(1), parse_mode="Markdown"),
            "menu": lambda u, c: c.bot.send_message(chat_id=chat_id, text=get_menu_text(1), reply_markup=get_menu_keyboard(1), parse_mode="Markdown"),
            "panel": lambda u, c: c.bot.send_message(chat_id=chat_id, text="🎛️ BATTLE-DECK CONTROL PANEL:", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("Abort All Active Tasks 🚨", callback_data="stop_all")]]), parse_mode="Markdown"),
            "gcnc": cmd_gcnc, "vgcnc": cmd_vgcnc, "stopgcnc": cmd_stopgcnc,
            "target": cmd_target, "vtarget": cmd_vtarget, "stoptarget": cmd_stoptarget,
            "spam": cmd_spam, "stopspam": cmd_stopspam,
            "flood": cmd_flood, "vflood": cmd_vflood, "stopflood": cmd_stopflood,
            "gcpfp": cmd_gcpfp, "stopgcpfp": cmd_stopgcpfp,
            "voiceflood": cmd_voiceflood, "stopvoiceflood": cmd_stopvoiceflood,
            "ht": cmd_ht, "mute": cmd_mute, "unmute": cmd_unmute, "mutelist": cmd_mutelist,
            "stripmedia": cmd_stripmedia, "stopstripmedia": cmd_stopstripmedia,
            "pfpstripper": cmd_pfpstripper,
            "autoreply": cmd_autoreply, "vautoreply": cmd_vautoreply, "stopautoreply": cmd_stopautoreply,
            "reptts": cmd_reptts, "stopreptts": cmd_stopreptts,
            "clean": cmd_clean, "togglereactall": cmd_togglereactall, "togglereact": cmd_togglereact, "stopall": cmd_stopall,
            "scan": cmd_scan, "ping": cmd_ping, "getid": cmd_getid, "status": cmd_status,
            "omg": cmd_omg, "tts": cmd_tts,
            "roasthi": cmd_roasthi, "roasteng": cmd_roasteng,
            "cluster": cmd_cluster, "broadcast": cmd_broadcast,
            "slayinpowergifted": cmd_slayinpowergifted, "slayinpowertaken": cmd_slayinpowertaken,
            "slayinfor": cmd_slayinfor, "gban": cmd_gban, "ungban": cmd_ungban,
            "join": cmd_join, "leave": cmd_leave,
            "joinkrishslayin": cmd_joinkrishslayin, "leavekrishslayin": cmd_leavekrishslayin
        }
        if cmd_name in routes:
            handler = routes[cmd_name]
            await handler(update, context)

async def start_single_bot(token: str, bot_index: int):
    app = ApplicationBuilder().token(token).build()
    app.add_handler(CallbackQueryHandler(menu_callback_handler))
    app.add_handler(MessageHandler(filters.ALL, global_message_router))

    await app.initialize()
    await app.start()

    BOT_INSTANCES.append(app.bot)
    print(f"✅ Bot #{bot_index} (@{(await app.bot.get_me()).username}) connected to Cluster.")

    await app.updater.start_polling()
    await asyncio.Event().wait()

async def run_all_bots():
    tokens = []
    for key, value in os.environ.items():
        if key.startswith("BOT_TOKEN") and value.strip():
            tokens.append(value.strip())

    if not tokens:
        print("❌ Error: No BOT_TOKEN found in Environment Variables!")
        return

    print(f"🚀 Initializing {len(tokens)} bots in Synchronized Cluster Mode...")

    tasks = [asyncio.create_task(start_single_bot(token, idx)) for idx, token in enumerate(tokens, start=1)]
    await asyncio.gather(*tasks)

if __name__ == '__main__':
    try:
        asyncio.run(run_all_bots())
    except (KeyboardInterrupt, SystemExit):
        print("🛑 All bots stopped successfully.")
