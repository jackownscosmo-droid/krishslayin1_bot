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
    "cluster", "getid", "ht", "leave", "leavekrishslayin"
}

# 15 Custom User Target Lines
TARGET_LINES_EXPLICIT = [
    r"""Teri ma randi kyu hai 😂😂🔥🔥🔥🔥😂😂""",
    r"""East ➡️ or west ⬅️ teri ma babita is best🥵⚒🔥🥵⚒🔥""",
    r"""𝘿𝙃𝘼𝙏 ʳⁿᵈⁱᵏᵉʸ 🤦🏿‍♂️💢 𝘿𝙃𝘼𝙏 ʳⁿᵈⁱᵏᵉʸ 🤦🏿‍♂️💢𝘿𝙃𝘼𝙏 ʳⁿᵈⁱᵏᵉʸ 🤦🏿‍♂️💢""",
    r"""ᗷᑌᖇ ᗪᗴᗪO Tᑌᕼᗩᖇ ᗰᗩIYᗩ Kᗴ 😂💔🤤🫦👅🤡""",
    r"""𝐓ᴇʀɪ 𝐌ᴀᴀ 𝐂ʜᴜᴅᴋᴇ 𝐁ʜᴀᴀɢ 𝐑ᴀʜɪ -> 🏃🏻‍♀️🔥🤸🏻‍♀️🔥🏃🏻‍♀️🔥🤸🏻‍♀️🔥""",
    r"""🔺पिल्लै Tᴜᴊʜᴇ ᴍᴀʀᴇɴɢᴇ ʏᴀʜɪ ᴅᴇʟʜɪ ᴍᴀʏᴜʀ ᴠɪʜᴀʀ ᴍᴇ ᴊᴀʙ ᴍᴀʀᴇɴɢᴇ ᴅᴇᴋʜ ʟᴇɴᴀ 🔥>💀""",
    r"""Tri maa ke bosde pr jcb se khudai krwa duga rndyke😂😂🤟💥💥🤟""",
    r"""अच्छा teri maa के बूब्स पे green veins h इसलिए tu itna खिलसता h 😂👏🏻""",
    r"""Clap करो रंडीबाले ne joke mara h 😂👋🏻😂👋🏻😂👋🏻😂👋🏻😂👋🏻😂👋🏻""",
    r"""चलेगी toh teri लंगड़ी maa 😁🔥😂👋🏻""",
    r"""𝐄ɴᴛʀʏ 𝐋ᴇʟɪ 𝐓ᴏ 𝐀sᴍᴀɴ 𝐊ɪ 𝐔ᴄʜᴀɪᴏ 𝐏ᴇ 𝐓ᴇʀɪ 𝐌ᴀ 𝐂ʜᴜᴅᴇɢɪ / 🌘🕊️""",
    r"""subha ho ya sham chudte rhena hai tera kaam😂🔥😂🔥😂🔥""",
    r"""teri ma ke bhosde سے flight✈take off land teri bhen ke bhosde pe krunga""",
    r"""randy pane me to teri ma aval darje ki hakdaar he😁👍😁👍😁👍😁👍""",
    r"""Le धमाकेदार mukka kha रन्डी ke चाइल्ड 👊🏻👊🏻👊🏻🤣🤣"""
]

AUTOREPLY_LINES = [
    r"""बड़े दुःख के साथ हँसना पढ़ रहा है😂  𝐓ᴜ तेरी माँ रंडी 🤍😅🔥""",
    r"""𝙏𝙚𝙧𝙞 𝙢𝙖𝙖 𝙠𝙚 𝙝𝙤𝙨𝙙𝙚 𝙢𝙚 𝙡𝙖𝙩 𝙥𝙙𝙚𝙣𝙜𝙚 𝙗𝙝𝙤𝙩 𝙩𝙚𝙯 👻 😂👯😂👯😂👯 😂👯😂👯😂👯 😂👯😂👯😂👯""",
    r"""𝙏𝙀𝙍𝙄 𝙈𝘼 𝑑𝙄𝘿🇭🇻𝘼 𝙋𝙀𝙉𝙎𝙄𝙊𝙉 𝙃𝘼𝙉𝙀 𝙒𝘼𝙇𝙄 𝙍𝙉𝘿𝙄 🤣"""
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
    "scan", "ping", "getid", "status", "omg", "tts", "ttshi", "ttsen", "ttsjap", "ttsgerman",
    "roasthi", "roasteng", "cluster", "broadcast",
    "slayinpowergifted", "slayinpowertaken", "slayinfor",
    "gban", "ungban", "ht", "leave", "leavekrishslayin"
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
        except Exception:
            pass

# --- Reset Switch ---

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
            "• +vtarget <user> [@bot1 @bot2] — Custom target attack\n"
            "• +stoptarget — Disarm targeting loop\n"
            "• +spam <text> — Multi-bot high-speed spam\n"
            "• +stopspam — EMERGENCY KILL-SWITCH\n"
            "• +flood <user> — Mention flood\n"
            "• +vflood <user> <text> — Custom mention flood\n"
            "• +stopflood — Stop mention flood"
        )
    elif page == 3:
        return (
            "⛓️ TRAPS & TARGETING 🎯\n"
            "────────────────────────────\n"
            "• +ht — Shadow-mute with fake unmute button\n"
            "• +mute <user> — Shadow-mute target\n"
            "• +unmute <user> — Unmute target\n"
            "• +mutelist — View muted users\n"
            "• +stripmedia <user> — Auto-delete media\n"
            "• +stopstripmedia — Disable media stripper\n"
            "• +pfpstripper on/off — Delete group PFP changes\n"
            "• +autoreply <user> — Auto-reply trap\n"
            "• +vautoreply <user> <msg> — Custom reply trap\n"
            "• +stopautoreply — Disarm auto-reply\n"
            "• +reptts <user> — Voice trap (Reads target msg)\n"
            "• +stopreptts — Disarm voice trap"
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
            "• +tts <text> — Hindi Voice\n"
            "• +ttshi <text> — Hindi Voice\n"
            "• +ttsen <text> — English Voice\n"
            "• +ttsjap <text> — Japanese Voice\n"
            "• +ttsgerman <text> — German Voice"
        )
    elif page == 5:
        return (
            "👑 OWNER CONTROLS\n"
            "────────────────────────────\n"
            "• +leave <@bot_username> — Leave specific bot\n"
            "• +leavekrishslayin — Leave all bots\n"
            "• +cluster — Node telemetry\n"
            "• +broadcast <text> — Network broadcast"
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

    elif data == "stop_all":
        await hard_stop_all(query.message.chat_id, context, query.from_user.id)
        return await query.edit_message_text("🚨 ALL ACTIVE TASKS TERMINATED.", reply_markup=get_menu_keyboard(1))
    
    elif data.startswith("menu_"):
        page = int(data.split("_")[1])
        await query.edit_message_text(get_menu_text(page), reply_markup=get_menu_keyboard(page), parse_mode="Markdown")

# --- Combat & Attacks ---

async def cmd_target(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id): return
    args = update.message.text.split()[1:]
    target_user = args[0] if args else "@target"
    reply_to_msg_id = update.message.reply_to_message.message_id if update.message.reply_to_message else update.message.message_id

    chat_data = get_chat_data(update.effective_chat.id)
    if "target" in chat_data["tasks"]: chat_data["tasks"]["target"].cancel()

    async def multi_target_loop():
        bot_idx = 0
        total_bots = max(1, len(BOT_INSTANCES))
        while True:
            current_bot = BOT_INSTANCES[bot_idx % total_bots] if BOT_INSTANCES else context.bot
            line = random.choice(TARGET_LINES_EXPLICIT)
            try:
                await current_bot.send_message(
                    chat_id=update.effective_chat.id, 
                    text=f"{target_user}\n{line}",
                    reply_to_message_id=reply_to_msg_id
                )
            except Exception: pass
            bot_idx += 1
            await asyncio.sleep(0.3)

    task = asyncio.create_task(multi_target_loop())
    chat_data["tasks"]["target"] = task

async def cmd_vtarget(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id): return
    args = update.message.text.split()[1:]
    if not args:
        return await context.bot.send_message(chat_id=update.effective_chat.id, text="Usage: +vtarget <username> [@bot1 @bot2]")

    target_user = args[0]
    tagged_bots = [arg.lower().replace("@", "") for arg in args[1:] if arg.startswith("@")]

    reply_to_msg_id = update.message.reply_to_message.message_id if update.message.reply_to_message else update.message.message_id

    active_bots = []
    if tagged_bots:
        for bot in BOT_INSTANCES:
            me = await bot.get_me()
            if me.username.lower() in tagged_bots:
                active_bots.append(bot)
    else:
        active_bots = BOT_INSTANCES if BOT_INSTANCES else [context.bot]

    if not active_bots:
        return await context.bot.send_message(chat_id=update.effective_chat.id, text="⚠️ Tagged bot(s) active list me nahi mile.")

    chat_data = get_chat_data(update.effective_chat.id)
    if "target" in chat_data["tasks"]: chat_data["tasks"]["target"].cancel()

    async def multi_vtarget_loop():
        bot_idx = 0
        total_bots = len(active_bots)
        while True:
            current_bot = active_bots[bot_idx % total_bots]
            line = random.choice(TARGET_LINES_EXPLICIT)
            try:
                await current_bot.send_message(
                    chat_id=update.effective_chat.id, 
                    text=f"{target_user}\n{line}",
                    reply_to_message_id=reply_to_msg_id
                )
            except Exception: pass
            bot_idx += 1
            await asyncio.sleep(0.3)

    task = asyncio.create_task(multi_vtarget_loop())
    chat_data["tasks"]["target"] = task

async def cmd_stoptarget(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_data = get_chat_data(update.effective_chat.id)
    if "target" in chat_data["tasks"]:
        chat_data["tasks"]["target"].cancel()
        del chat_data["tasks"]["target"]
        await context.bot.send_message(chat_id=update.effective_chat.id, text="🛑 Target Attack Stopped.")

async def cmd_vflood(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id): return
    args = update.message.text.split()[1:]
    if len(args) < 2: 
        return await context.bot.send_message(chat_id=update.effective_chat.id, text="Usage: +vflood <user> <text>")
    
    user, custom_text = args[0], " ".join(args[1:])
    chat_data = get_chat_data(update.effective_chat.id)
    if "flood" in chat_data["tasks"]: chat_data["tasks"]["flood"].cancel()

    async def multi_vflood_loop():
        bot_idx = 0
        total_bots = max(1, len(BOT_INSTANCES))
        while True:
            current_bot = BOT_INSTANCES[bot_idx % total_bots] if BOT_INSTANCES else context.bot
            try: 
                await current_bot.send_message(chat_id=update.effective_chat.id, text=f"🌊 {user} {custom_text}")
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

# --- Multi-Language TTS Section ---

async def generate_and_send_tts(chat_id, text, lang, context):
    if gTTS is None:
        return await context.bot.send_message(chat_id=chat_id, text=f"🔊 TTS Voice ({lang}): {text}")
    try:
        tts = gTTS(text=text, lang=lang)
        file_name = f"tts_{random.randint(1000, 9999)}.mp3"
        tts.save(file_name)
        with open(file_name, "rb") as voice_file:
            await context.bot.send_voice(chat_id=chat_id, voice=voice_file)
        if os.path.exists(file_name):
            os.remove(file_name)
    except Exception as e:
        await context.bot.send_message(chat_id=chat_id, text=f"🔊 TTS Error: {str(e)}")

async def cmd_tts(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = " ".join(update.message.text.split()[1:])
    if not text: return await context.bot.send_message(chat_id=update.effective_chat.id, text="Usage: +tts <text>")
    await generate_and_send_tts(update.effective_chat.id, text, "hi", context)

async def cmd_ttshi(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = " ".join(update.message.text.split()[1:])
    if not text: return await context.bot.send_message(chat_id=update.effective_chat.id, text="Usage: +ttshi <text>")
    await generate_and_send_tts(update.effective_chat.id, text, "hi", context)

async def cmd_ttsen(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = " ".join(update.message.text.split()[1:])
    if not text: return await context.bot.send_message(chat_id=update.effective_chat.id, text="Usage: +ttsen <text>")
    await generate_and_send_tts(update.effective_chat.id, text, "en", context)

async def cmd_ttsjap(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = " ".join(update.message.text.split()[1:])
    if not text: return await context.bot.send_message(chat_id=update.effective_chat.id, text="Usage: +ttsjap <text>")
    await generate_and_send_tts(update.effective_chat.id, text, "ja", context)

async def cmd_ttsgerman(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = " ".join(update.message.text.split()[1:])
    if not text: return await context.bot.send_message(chat_id=update.effective_chat.id, text="Usage: +ttsgerman <text>")
    await generate_and_send_tts(update.effective_chat.id, text, "de", context)

# --- Dynamic Cluster Leave Commands ---

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
        await context.bot.send_message(chat_id=update.effective_chat.id, text=f"⚠️ Bot @{target_bot_username} cluster me nahi mila.")

async def cmd_leavekrishslayin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != OWNER_ID: return
    await context.bot.send_message(chat_id=update.effective_chat.id, text="👋 Initiating Mass Leave across all bots...")
    for bot in BOT_INSTANCES:
        try:
            await bot.leave_chat(chat_id=update.effective_chat.id)
        except Exception: pass

# --- Global Engine Router ---

async def global_message_router(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.from_user: return
    user_id = update.message.from_user.id
    chat_id = update.effective_chat.id
    text = update.message.text.strip() if update.message.text else ""

    bot_username = (await context.bot.get_me()).username.lower()
    is_main_bot = (MAIN_BOT_USERNAME == "" or bot_username == MAIN_BOT_USERNAME)

    cmd_name = ""
    is_valid_cmd = False
    if text.startswith("+"):
        possible_cmd = text.split()[0][1:].lower()
        if possible_cmd in VALID_COMMANDS:
            cmd_name = possible_cmd
            is_valid_cmd = True

    if is_valid_cmd:
        if cmd_name in MAIN_BOT_ONLY_COMMANDS and not is_main_bot:
            return

        routes = {
            "start": lambda u, c: c.bot.send_message(chat_id=chat_id, text=get_menu_text(1), reply_markup=get_menu_keyboard(1), parse_mode="Markdown"),
            "menu": lambda u, c: c.bot.send_message(chat_id=chat_id, text=get_menu_text(1), reply_markup=get_menu_keyboard(1), parse_mode="Markdown"),
            "target": cmd_target, "vtarget": cmd_vtarget, "stoptarget": cmd_stoptarget,
            "vflood": cmd_vflood, "stopflood": cmd_stopflood,
            "tts": cmd_tts, "ttshi": cmd_ttshi, "ttsen": cmd_ttsen, "ttsjap": cmd_ttsjap, "ttsgerman": cmd_ttsgerman,
            "leave": cmd_leave, "leavekrishslayin": cmd_leavekrishslayin
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
    print(f"✅ Bot #{bot_index} (@{(await app.bot.get_me()).username}) connected.")

    await app.updater.start_polling()
    await asyncio.Event().wait()

async def run_all_bots():
    tokens = []
    for key, value in os.environ.items():
        if key.startswith("BOT_TOKEN") and value.strip():
            tokens.append(value.strip())

    if not tokens:
        print("❌ Error: No BOT_TOKEN found!")
        return

    tasks = [asyncio.create_task(start_single_bot(token, idx)) for idx, token in enumerate(tokens, start=1)]
    await asyncio.gather(*tasks)

if __name__ == '__main__':
    try:
        asyncio.run(run_all_bots())
    except (KeyboardInterrupt, SystemExit):
        print("🛑 All bots stopped.")
