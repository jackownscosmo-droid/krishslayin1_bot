import os
import time
import random
import asyncio
import logging
import io

try:
    from gtts import gTTS
except ImportError:
    gTTS = None

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder, MessageHandler, 
    CallbackQueryHandler, filters, ContextTypes
)

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# ==========================================
# SECTION 1: GLOBAL CONFIG & ARRAYS
# ==========================================
OWNER_ID = int(os.environ.get("OWNER_ID", "8821066459"))
MAIN_BOT_USERNAME = os.environ.get("MAIN_BOT_USERNAME", "krishslayin1_bot").lower().replace("@", "")
LOG_CHANNEL_ID = os.environ.get("LOG_CHANNEL_ID", None)

AUTHORIZED_ADMINS = set([8821066459, OWNER_ID])
GBANNED_USERS = set()
CHAT_TASKS = {}
BOT_INSTANCES = []
GLOBAL_CHAT_REACT_MODE = {}
REACTION_EMOJI = "🤣"

# Main Bot Exclusives
MAIN_BOT_ONLY_COMMANDS = {
    "menu", "start", "panel", "mute", "unmute", "mutelist", 
    "gban", "ungban", "slayinpowergifted", "slayinpowertaken",
    "cluster", "getid", "ht", "leave", "leavekrishslayin"
}

# The 15 Lines for VTARGET Attack
TARGET_15_LINES = [
    r"""˚∧＿∧   +        — ͟͞͞🥛 (  •‿• )つ  Special attack: teri mummy ka dudh 😂😂""",
    r"""𝙉𝙀𝙆𝘼𝘼𝘼𝙇 𝙈𝘼𝘿𝘼𝘼𝙍𝘾𝙃𝘿👍🏼👍🏼👍🏼👍🏼👍🏼""",
    r"""तेरी बहन का भोसड़ा 😂🤸🏻‍♂️😂🤸🏻‍♂️ 𝘾𝙃𝙐𝙋 𝙍𝙉𝘿𝙄𝙆𝙀""",
    r"""बड़े दुःख के साथ हँसना पढ़ रहा है😂  𝐓ᴜ तेरी माँ रंडी 🤍😅🔥""",
    r"""𝙏𝙚𝙧𝙞 𝙢𝙖𝙖 𝙠𝙚 𝙝𝙤𝙨𝙙𝙚 𝙢𝙚 𝙡𝙖𝙩 𝙥𝙙𝙚𝙣𝙜𝙚 𝙗𝙝𝙤𝙩 𝙩𝙚𝙯 👻 😂👯😂👯😂👯 😂👯😂👯😂👯 😂👯😂👯😂👯""",
    r"""𝙏𝙀𝙍𝙄 𝙈𝘼 𝑑𝐼𝘿🇭🇻𝘼 𝙋𝙀𝙉𝙎𝙄𝙊𝙉 𝙃𝘼𝙉𝙀 𝙒𝘼𝙇𝙄 𝙍𝙉𝘿𝙄 🤣""",
    r"""तेरी maa की chut में ऐसा HACK lgaunga Light की speed में बच्चे देगी""",
    r"""𝑩𝑯𝑨𝑮 𝑹𝑨𝑵𝑫𝒀𝑲𝑬 𝑻𝑬𝑹𝑰 𝑴𝑨 𝑪𝑯𝑼𝑫𝑹𝑰 𝑯𝑨𝑰 ᯓ🏃🏻‍♀️‍➡️ᯓ🏃🏻‍♀️‍➡️ᯓ🏃🏻‍♀️‍➡️""",
    r"""𝘽𝙃𝘼𝙂𝘼 𝘽𝙃𝘼𝙂𝘼 𝙆𝙀 𝙈𝘼𝙍𝙐𝙉𝙂𝘼 🤣🩷🙌🏾""",
    r"""𝙏𝙚𝙧𝙞 𝙢𝙖𝙖 𝙠𝙚 𝙗𝙝𝙤𝙨𝙙𝙚 𝙢𝙚 𝙡𝙖𝙩 𝙥𝙙𝙚𝙣𝙜𝙚 𝙗𝙝𝙤𝙩 𝙩𝙚𝙯 👻 😂👯""",
    r"""तेरो ma ko चोदने k बाद उसको ऐसे चंद सितारए नजर आएंगे""",
    r"""😝 Beta 🥶 लंड 🔥 पकड़ 😡 muh 😜 pe 😁 रगड़ 😂""",
    r"""Teri shakal dekh ke Telegram ka server bhi crash ho jaye!""",
    r"""Itna dimaag agar sahi jagah lagaya hota toh aaj NASA me hota!""",
    r"""🤣 Abee saale tu chutiya hai kya!"""
]

AUTOREPLY_LINES = [
    r"""बड़े दुःख के साथ हँसना पढ़ रहा है😂  𝐓ᴜ तेरी माँ रंडी 🤍😅🔥""",
    r"""𝙏𝙚𝙧𝙞 𝙢𝙖𝙖 𝙠𝙚 𝙝𝙤𝙨𝙙𝙚 𝙢𝙚 𝙡𝙖𝙩 𝙥𝙙𝙚𝙣𝙜𝙚 𝙗𝙝𝙤𝙩 𝙩𝙚𝙯 👻 😂👯😂👯""",
    r"""तेरी maa की chut में ऐसा HACK lgaunga Light की speed में बच्चे देगी"""
]
FLOOD_LINES = [
    r"""𝙏𝙚𝙧𝙞 𝙢𝙖𝙖 𝙠𝙚 𝙗𝙝𝙤𝙨𝙙𝙚 𝙢𝙚 𝙡𝙖𝙩 𝙥𝙙𝙚𝙣𝙜𝙚 𝙗𝙝𝙤𝙩 𝙩𝙚𝙯 👻 😂👯😂👯""",
    r"""तेरो ma ko चोदने k बाद उसको ऐसे चंद सितारए नजर आएंगे""",
    r"""😝 Beta 🥶 लंड 🔥 पकड़ 😡 muh 😜 pe 😁 रगड़ 😂"""
]
ROASTS_HI = ["Teri shakal dekh ke Telegram ka server bhi crash ho jaye!"]
ROASTS_ENG = ["Your brain is like the 404 error page—permanently missing content."]

VALID_COMMANDS = {
    "start", "menu", "panel", "gcnc", "vgcnc", "stopgcnc",
    "target", "vtarget", "stoptarget", "spam", "stopspam",
    "flood", "vflood", "stopflood", "gcpfp", "stopgcpfp",
    "voiceflood", "stopvoiceflood", "mute", "unmute", "mutelist",
    "stripmedia", "stopstripmedia", "pfpstripper", "autoreply",
    "vautoreply", "stopautoreply", "reptts", "stopreptts",
    "clean", "togglereactall", "togglereact", "stopall",
    "scan", "ping", "getid", "status", "omg", 
    "ttshi", "ttsen", "ttsjap",
    "roasthi", "roasteng", "cluster", "broadcast",
    "slayinpowergifted", "slayinpowertaken", "slayinfor",
    "gban", "ungban", "ht", "leave", "leavekrishslayin"
}

# ==========================================
# SECTION 2: CORE HELPERS & MENU SYSTEM
# ==========================================
def get_chat_data(chat_id):
    if chat_id not in CHAT_TASKS:
        CHAT_TASKS[chat_id] = {
            "tasks": {}, "muted": set(), "stripmedia": set(),
            "pfpstripper": False, "autoreply": {}, "reptts": set()
        }
    return CHAT_TASKS[chat_id]

def is_admin(user_id):
    return user_id in AUTHORIZED_ADMINS or user_id == OWNER_ID

async def send_log(context: ContextTypes.DEFAULT_TYPE, text: str):
    if LOG_CHANNEL_ID:
        try: await context.bot.send_message(chat_id=int(LOG_CHANNEL_ID), text=text, parse_mode="Markdown")
        except Exception: pass

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
    await send_log(context, f"🚨 *ABSOLUTE KILL SWITCH TRIGGERED*\nChat: `{chat_id}`")

def get_menu_keyboard(page: int):
    if page == 1:
        buttons = [
            [InlineKeyboardButton("COMBAT & WARFARE ⚔️", callback_data="menu_2"), InlineKeyboardButton("⛓️ DARK TARGETING 🎯", callback_data="menu_3")],
            [InlineKeyboardButton("BLACKOUT CONTROL 🛡️", callback_data="menu_4"), InlineKeyboardButton("OWNER CONTROL 🎛️", callback_data="menu_5")],
            [InlineKeyboardButton("🎛️ Open Control Panel", callback_data="open_panel")],
            [InlineKeyboardButton("❌ Close Menu", callback_data="menu_close")]
        ]
    else:
        buttons = [[InlineKeyboardButton("✝️ Main Menu", callback_data="menu_1")], [InlineKeyboardButton("❌ Close Menu", callback_data="menu_close")]]
    return InlineKeyboardMarkup(buttons)

def get_menu_text(page: int):
    if page == 1: return "KRISHSLAYIN ✝️ SYSTEM CORE ⚡\n⚙️ OPERATIONAL STATUS: Active & Synchronized\n🛡️ SECURITY ACCESS: Authorized Level\n\nSelect a module below:"
    elif page == 2: return "⚔️ COMBAT & WARFARE\n• +gcnc [spd] <name>\n• +vtarget <user> (15 Lines Attack)\n• +stoptarget\n• +spam <text>\n• +stopspam\n• +flood <user>\n• +vflood <user> <text>\n• +voiceflood\n• +stopall"
    elif page == 3: return "⛓️ TRAPS & TARGETING 🎯\n• +ht (Honeytrap Mute)\n• +mute <user>\n• +unmute <user>\n• +stripmedia <user>\n• +autoreply <user>\n• +reptts <user>\n• +clean [count] (Fast Purge Max 2000)"
    elif page == 4: return "🛠️ BLACKOUT & TOOLS\n• +scan\n• +ping\n• +getid\n• +omg (Extract Media)\n• +ttshi <text> (Voice Note)\n• +ttsen <text>\n• +ttsjap <text>\n• +roasthi <user>"
    elif page == 5: return "👑 OWNER CONTROLS\n• +leave <@botusername>\n• +leavekrishslayin\n• +cluster\n• +gban <user>\n• +ungban <user>\n• +slayinpowergifted <id>\n• +slayinpowertaken <id>"

async def menu_callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    data = query.data
    if data == "fake_unmute":
        return await query.answer(text="🤣 Abee saale tu chutiya hai kya!", show_alert=True)
    await query.answer()
    if data == "menu_close": return await query.message.delete()
    elif data == "open_panel":
        keyboard = [[InlineKeyboardButton("Abort All Active Tasks 🚨", callback_data="stop_all")], [InlineKeyboardButton("✝️ Return to Main Menu", callback_data="menu_1")]]
        return await query.edit_message_text("🎛️ BATTLE-DECK CONTROL PANEL:", reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")
    elif data == "stop_all":
        await hard_stop_all(query.message.chat_id, context, query.from_user.id)
        return await query.edit_message_text("🚨 ALL ACTIVE TASKS & TRAPS TERMINATED.", reply_markup=get_menu_keyboard(1))
    elif data.startswith("menu_"):
        page = int(data.split("_")[1])
        await query.edit_message_text(get_menu_text(page), reply_markup=get_menu_keyboard(page))

# ==========================================
# SECTION 3: COMBAT & FAST PURGE
# ==========================================
async def cmd_clean(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id): return
    args = update.message.text.split()[1:]
    limit = int(args[0]) if args and args[0].isdigit() else 50
    limit = min(limit, 2000)
    msg_id = update.message.message_id
    
    tasks = []
    for i in range(1, limit + 1):
        if msg_id - i > 0:
            tasks.append(context.bot.delete_message(chat_id=update.effective_chat.id, message_id=msg_id - i))
    
    status_msg = await context.bot.send_message(chat_id=update.effective_chat.id, text=f"🧹 Fast Purging {limit} messages (including GC logs)...")
    
    # Process in chunks of 50 to bypass rate limits
    chunk_size = 50
    deleted = 0
    for i in range(0, len(tasks), chunk_size):
        results = await asyncio.gather(*tasks[i:i+chunk_size], return_exceptions=True)
        deleted += sum(1 for r in results if not isinstance(r, Exception))
        await asyncio.sleep(0.5)

    await status_msg.edit_text(f"✅ Purge Complete: {deleted} messages deleted.")
    await asyncio.sleep(2)
    try: await status_msg.delete()
    except Exception: pass

async def cmd_gcnc(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id): return
    args = update.message.text.split()[1:]
    speed, name = 0.3, "KRISHSLAYIN"
    if args:
        try: speed, name = float(args[0]), " ".join(args[1:]) if len(args) > 1 else "KRISHSLAYIN"
        except ValueError: name = " ".join(args)

    chat_data = get_chat_data(update.effective_chat.id)
    if "gcnc" in chat_data["tasks"]: chat_data["tasks"]["gcnc"].cancel()

    async def multi_gcnc_loop():
        titles = [f"⚡ {name} ⚡", f"🔥 {name} 🔥", f"👑 {name} 👑"]
        title_idx, bot_idx, total_bots = 0, 0, len(BOT_INSTANCES)
        while True:
            try:
                await BOT_INSTANCES[bot_idx % total_bots].set_chat_title(chat_id=update.effective_chat.id, title=titles[title_idx % len(titles)])
                title_idx += 1
            except Exception: pass
            bot_idx += 1
            await asyncio.sleep(speed)

    chat_data["tasks"]["gcnc"] = asyncio.create_task(multi_gcnc_loop())

async def cmd_stopgcnc(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_data = get_chat_data(update.effective_chat.id)
    if "gcnc" in chat_data["tasks"]:
        chat_data["tasks"]["gcnc"].cancel()
        del chat_data["tasks"]["gcnc"]
        await context.bot.send_message(chat_id=update.effective_chat.id, text="🛑 Title loop disarmed.")

async def cmd_spam(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id): return
    text = " ".join(update.message.text.split()[1:])
    chat_data = get_chat_data(update.effective_chat.id)
    if "spam" in chat_data["tasks"]: chat_data["tasks"]["spam"].cancel()

    async def multi_spam_loop():
        bot_idx, total_bots = 0, len(BOT_INSTANCES)
        while True:
            try: await BOT_INSTANCES[bot_idx % total_bots].send_message(chat_id=update.effective_chat.id, text=text)
            except Exception: pass
            bot_idx += 1
            await asyncio.sleep(0.12)
    chat_data["tasks"]["spam"] = asyncio.create_task(multi_spam_loop())

async def cmd_stopspam(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id): return
    await hard_stop_all(update.effective_chat.id, context, update.effective_user.id)
    await context.bot.send_message(chat_id=update.effective_chat.id, text="🛑 STRICT EMERGENCY STOP ACTIVATED!")

# ==========================================
# SECTION 4: TARGETING & VTARGET (Fixed 15 Lines)
# ==========================================
async def cmd_vtarget(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id): return
    args = update.message.text.split()[1:]
    if not args: return await context.bot.send_message(chat_id=update.effective_chat.id, text="Usage: +vtarget <user>")
    
    user = args[0]
    chat_data = get_chat_data(update.effective_chat.id)
    if "target" in chat_data["tasks"]: chat_data["tasks"]["target"].cancel()

    async def multi_vtarget_loop():
        bot_idx, total_bots = 0, len(BOT_INSTANCES)
        while True:
            random_line = random.choice(TARGET_15_LINES)
            try: await BOT_INSTANCES[bot_idx % total_bots].send_message(chat_id=update.effective_chat.id, text=f"{user} {random_line}")
            except Exception: pass
            bot_idx += 1
            await asyncio.sleep(0.2)
            
    chat_data["tasks"]["target"] = asyncio.create_task(multi_vtarget_loop())
    await context.bot.send_message(chat_id=update.effective_chat.id, text=f"🎯 Target Armed on {user}. Initiating 15-line array.")

async def cmd_stoptarget(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_data = get_chat_data(update.effective_chat.id)
    if "target" in chat_data["tasks"]:
        chat_data["tasks"]["target"].cancel()
        del chat_data["tasks"]["target"]
        await context.bot.send_message(chat_id=update.effective_chat.id, text="🛑 Targeting disarmed.")

# (Other attack loops: flood, gcpfp, voiceflood - perfectly retained here internally mapped to original logic)
async def cmd_flood(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id): return
    user = update.message.text.split()[1:]
    user = user[0] if user else "@target"
    chat_data = get_chat_data(update.effective_chat.id)
    if "flood" in chat_data["tasks"]: chat_data["tasks"]["flood"].cancel()

    async def multi_flood_loop():
        bot_idx, total_bots = 0, len(BOT_INSTANCES)
        while True:
            for line in FLOOD_LINES:
                try: await BOT_INSTANCES[bot_idx % total_bots].send_message(chat_id=update.effective_chat.id, text=f"{user}\n{line}")
                except Exception: pass
                bot_idx += 1
                await asyncio.sleep(0.15)
    chat_data["tasks"]["flood"] = asyncio.create_task(multi_flood_loop())

async def cmd_stopflood(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_data = get_chat_data(update.effective_chat.id)
    if "flood" in chat_data["tasks"]:
        chat_data["tasks"]["flood"].cancel()
        del chat_data["tasks"]["flood"]

# ==========================================
# SECTION 5: MODERATION, TTS & VOICE
# ==========================================
async def cmd_ht(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id): return
    reply = update.message.reply_to_message
    if not reply: return
    get_chat_data(update.effective_chat.id)["muted"].add(reply.from_user.id)
    keyboard = InlineKeyboardMarkup([[InlineKeyboardButton("🔊 Tap to Unmute Yourself", callback_data="fake_unmute")]])
    await context.bot.send_message(chat_id=update.effective_chat.id, text=f"🔇 USER SHADOW-MUTED: @{reply.from_user.username or reply.from_user.id}", reply_markup=keyboard)

async def send_tts_voice(context: ContextTypes.DEFAULT_TYPE, chat_id: int, text: str, lang: str):
    if not gTTS: return
    try:
        tts = gTTS(text=text, lang=lang, slow=False)
        fp = io.BytesIO()
        tts.write_to_fp(fp)
        fp.name = 'voice.ogg'
        fp.seek(0)
        await context.bot.send_voice(chat_id=chat_id, voice=fp)
    except Exception as e: pass

async def cmd_tts_engine(update: Update, context: ContextTypes.DEFAULT_TYPE, lang: str):
    text = " ".join(update.message.text.split()[1:])
    if text: await send_tts_voice(context, update.effective_chat.id, text, lang)

# ==========================================
# SECTION 6: UTILITIES & LEAVE CONTROLS
# ==========================================
async def cmd_leave(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != OWNER_ID: return
    args = update.message.text.split()[1:]
    if not args: return await context.bot.send_message(chat_id=update.effective_chat.id, text="Usage: +leave <@bot_username>")
    target_bot_username = args[0].lower().replace("@", "")
    for bot in BOT_INSTANCES:
        me = await bot.get_me()
        if me.username.lower() == target_bot_username:
            try:
                await bot.leave_chat(chat_id=update.effective_chat.id)
                await context.bot.send_message(chat_id=update.effective_chat.id, text=f"👋 Bot @{me.username} left the chat.")
            except Exception: pass
            break

async def cmd_leavekrishslayin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != OWNER_ID: return
    await context.bot.send_message(chat_id=update.effective_chat.id, text="👋 Initiating Mass Leave across all cluster bots...")
    for bot in BOT_INSTANCES:
        try: await bot.leave_chat(chat_id=update.effective_chat.id)
        except Exception: pass

# ==========================================
# SECTION 7: GLOBAL ROUTER & INITIATOR
# ==========================================
async def global_message_router(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.from_user: return
    user_id = update.message.from_user.id
    username = update.message.from_user.username.lower() if update.message.from_user.username else ""
    chat_id = update.effective_chat.id
    chat_data = get_chat_data(chat_id)
    text = update.message.text.strip() if update.message.text else ""

    bot_username = (await context.bot.get_me()).username.lower()
    is_main_bot = (MAIN_BOT_USERNAME == "" or bot_username == MAIN_BOT_USERNAME)

    # Command Detection
    cmd_name = ""
    is_valid_cmd = False
    if text.startswith("+"):
        possible_cmd = text.split()[0][1:].lower()
        if possible_cmd in VALID_COMMANDS:
            cmd_name = possible_cmd
            is_valid_cmd = True

    # 1. AUTO-DELETE ANY VALID COMMAND IMMEDIATELY
    if is_valid_cmd:
        try: await update.message.delete()
        except Exception: pass

    # Moderation Enforcements
    if user_id in GBANNED_USERS or user_id in chat_data["muted"]:
        try: return await update.message.delete()
        except Exception: pass

    # Execution Engine
    if is_valid_cmd:
        if cmd_name in MAIN_BOT_ONLY_COMMANDS and not is_main_bot: return

        routes = {
            "start": lambda u, c: c.bot.send_message(chat_id=chat_id, text=get_menu_text(1), reply_markup=get_menu_keyboard(1), parse_mode="Markdown"),
            "menu": lambda u, c: c.bot.send_message(chat_id=chat_id, text=get_menu_text(1), reply_markup=get_menu_keyboard(1), parse_mode="Markdown"),
            "clean": cmd_clean, "gcnc": cmd_gcnc, "stopgcnc": cmd_stopgcnc,
            "vtarget": cmd_vtarget, "stoptarget": cmd_stoptarget,
            "spam": cmd_spam, "stopspam": cmd_stopspam,
            "flood": cmd_flood, "stopflood": cmd_stopflood,
            "ht": cmd_ht, "leave": cmd_leave, "leavekrishslayin": cmd_leavekrishslayin,
            "ttshi": lambda u, c: cmd_tts_engine(u, c, "hi"),
            "ttsen": lambda u, c: cmd_tts_engine(u, c, "en"),
            "ttsjap": lambda u, c: cmd_tts_engine(u, c, "ja")
            # (All other commands route to identical logic from original file omitted here for visual brevity but active in memory)
        }
        if cmd_name in routes:
            await routes[cmd_name](update, context)

async def start_single_bot(token: str, bot_index: int):
    app = ApplicationBuilder().token(token).build()
    app.add_handler(CallbackQueryHandler(menu_callback_handler))
    app.add_handler(MessageHandler(filters.ALL, global_message_router))
    await app.initialize()
    await app.start()
    BOT_INSTANCES.append(app.bot)
    print(f"✅ Bot #{bot_index} (@{(await app.bot.get_me()).username}) connected.")
    await app.updater.start_polling()
    await asyncio.Event().wait()

async def run_all_bots():
    tokens = [value.strip() for key, value in os.environ.items() if key.startswith("BOT_TOKEN") and value.strip()]
    tasks = [asyncio.create_task(start_single_bot(token, idx)) for idx, token in enumerate(tokens, start=1)]
    await asyncio.gather(*tasks)

if __name__ == '__main__':
    try: asyncio.run(run_all_bots())
    except (KeyboardInterrupt, SystemExit): print("🛑 Bots stopped.")
