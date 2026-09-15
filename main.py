import os
import time
import random
import asyncio
import logging

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

# Global Configuration & Security Protocol
OWNER_ID = int(os.environ.get("OWNER_ID", "123456789"))
AUTHORIZED_ADMINS = set([OWNER_ID])
GBANNED_USERS = set()
CHAT_TASKS = {}

# Raw Text Line Arrays
AUTOREPLY_LINES = [
    "बड़े दुःख के साथ हँसना पढ़ रहा है😂  𝐓ᴜ तेरी माँ रंडी 🤍😅🔥",
    "𝙏𝙚𝙧𝙞 𝙢𝙖𝙖 𝙠𝙚 𝙗𝙝𝙤𝙨𝙙𝙚 𝙢𝙚 𝙡𝙖𝙩 𝙥𝙙𝙚𝙣𝙜𝙚 𝙗𝙝𝙤𝙩 𝙩𝙚𝙯 👻 😂👯😂👯😂👯 😂👯😂👯😂👯 😂👯😂👯😂👯",
    "𝙏𝙀𝙍𝙄 𝙈𝘼 𝑑𝙄𝘿𝙃𝙑𝘼 𝙋𝙀𝙉𝙎𝙄𝙊𝙉 𝙆𝙃𝘼𝙉𝙀 𝙒𝘼𝙇𝙄 𝙍𝙉𝘿𝙄 🤣",
    "तेरी maa की chut में ऐसा HACK lgaunga \nLight की speed में बच्चे देगी",
    "𝑩𝑯𝑨𝑮 𝑹𝑨𝑵𝑫𝒀𝑲𝑬 𝑻𝑬𝑹𝑰 𝑴𝑨 𝑪𝑯𝑼𝑫𝑹𝑰 𝑯𝑨𝑰 ᯓ🏃🏻‍♀️‍➡️ᯓ🏃🏻‍♀️‍➡️ᯓ🏃🏻‍♀️‍➡️ᯓ🏃🏻‍♀️‍➡️ᯓ🏃🏻‍♀️‍➡️ᯓ🏃🏻‍♀️‍➡️ᯓ🏃🏻‍♀️‍➡️ᯓ🏃🏻‍♀️‍➡️ᯓ🏃🏻‍♀️‍➡️ᯓ🏃🏻‍♀️‍➡️ᯓ🏃🏻‍♀️‍➡️",
    "𝘽𝙃𝘼𝙂𝘼 𝘽𝙃𝘼𝙂𝘼 𝙆𝙀 𝙈𝘼𝙍𝙐𝙉𝙂𝘼 🤣🩷🙌🏾",
    "𝐆ʀᴇᴇਬ𝐢 और दर्दनाक 𝐂ʜᴜᴅᴀ𝐢 \nतो तेरी मां ने देखी है 👀😝🤣"
]

TARGET_LINES = [
    "˚∧＿∧   +        — ͟͞͞🥛\n(  •‿• )つ  — ͟͞͞ 🥛         — ͟͞͞🥛 +\n(つ  <                — ͟͞͞🥛\n｜_つ      +  — ͟͞͞🥛         — ͟͞͞🥛 ˚\n`し´Special attack: teri  mummy ka dudh 😂😂 kilas randi ke",
    "𝙉𝙀𝙆𝘼𝘼𝘼𝙇 𝙈𝘼𝘿𝘼𝘼𝙍𝘾𝙃𝘿👍🏼👍🏼👍🏼👍🏼👍🏼",
    "🚓🚜🚌🚙🚃\n     🚙🌍🌎🌏🌎🚕\n  🇩🇪🇪🇸🌍🚔\n🚘🌏🇷🇺🇬🇧🇮🇹🇪🇸🌏🚘\n🚔🌍🇰🇷🇯🇵🇺🇸🇬🇧🌍🚖\n  🚖🌎🇮🇹🇫🇷🇰🇷🌍🚘\n     🚍🌏🌍🌎🌏🚔\n",
    "तेरी बहन का भोसड़ा 😂🤸🏻‍♂️😂🤸🏻‍♂️😂🤸🏻‍♂️😂𝘾𝙃𝙐𝙋 𝙍𝙉𝘿𝙄𝙆𝙀",
    "ᴍᴀᴀғɪ ᴍᴀɴɢʟᴇ ᴋʏᴀ ᴘᴀᴛᴀ ʙᴀᴅʙᴏʏ ᴍᴀᴀғ ᴋʀᴅ ᴛᴜᴊᴇ"
]

FLOOD_LINES = [
    "𝙏𝙚𝙧𝙞 𝙢𝙖𝙖 𝙠𝙚 𝙗𝙝𝙤𝙨𝙙𝙚 𝙢𝙚 𝙡𝙖𝙩 𝙥𝙙𝙚𝙣𝙜𝙚 𝙗𝙝𝙤𝙩 𝙩𝙚𝙯 👻 😂👯😂👯😂👯 😂👯😂👯😂👯 😂👯😂👯😂👯",
    "⋆͙̈ ° ♪ °••° ⋆⋆͙̈ ° ♪ °••° ⋆⋆͙̈ ° ♪ °••° ⋆⋆͙̈ ° ♪ °••° ⋆⋆͙̈ ° ♪ °••° ⋆⋆͙̈ ° ♪ °••° ⋆⋆͙̈ ° ♪ °••° ⋆⋆͙̈ ° ♪ °••° ⋆⋆͙̈ ° ♪ °••° ⋆⋆͙̈ ° ♪ °••° ⋆⋆͙̈ ° ♪ °••° ⋆⋆͙̈ ° ♪ °••° ⋆",
    "तेरो ma ko चोदने k बाद उसको ऐसे चंद सितारए नजर आएंगे",
    "😝 Beta 🥶 लंड 🔥 पकड़ 😡 muh 😜 pe 😁 रगड़ 😂",
    "𝐁ᴀᴀ𝐏 𝐊ᴏ 𝐑ᴇᴘʟ𝐘 𝐁ᴀᴅ𝐈 𝐓ᴇ𝐙 𝐃ᴇʀ𝐀 𝐇ᴀɪ 😁😁🌷",
    "𝙀𝙆 𝘽𝘼𝙍 𝘿𝙄𝙈𝘼𝙂 𝙂𝙃𝘼𝙍𝘼𝙈 𝙃𝙊𝙂𝙀𝙔𝘼 𝙉𝘼 𝘽𝙀𝙏𝘼"
]

ROASTS_HI = [
    "Teri shakal dekh ke Telegram ka server bhi crash ho jaye!",
    "Itna dimaag agar sahi jagah lagaya hota toh aaj NASA me hota, yahan bakchodi nahi kar raha hota!",
    "Tujhe dekh kar toh Google bhi bolta hai: 'Search Not Found'!",
    "Teri baaten sun kar mera battery percentage bhi drop ho gaya!"
]

ROASTS_ENG = [
    "You bring everyone so much joy... when you leave the room!",
    "I'd agree with you, but then we'd both be wrong.",
    "Your brain is like the 404 error page—permanently missing content."
]

REACTION_EMOJIS = ["❤️", "👍", "🔥", "🥰", "👏", "😁", "🤔", "😱", "🎉", "🤣", "💩"]

def get_chat_data(chat_id):
    if chat_id not in CHAT_TASKS:
        CHAT_TASKS[chat_id] = {
            "tasks": {},
            "muted": set(),
            "stripmedia": set(),
            "pfpstripper": False,
            "autoreply": {},
            "reptts": set(),
            "react_mode": None  # None, "all", "admin"
        }
    return CHAT_TASKS[chat_id]

def is_admin(user_id):
    return user_id in AUTHORIZED_ADMINS or user_id == OWNER_ID

# --- Interactive Dynamic UI ---

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
            "• +gcnc <name> — Coordinated title loop\n"
            "• +vgcnc [spd] <Title 1 | Title 2> — Title rotator\n"
            "• +stopgcnc — Halt active title loop\n"
            "• +target <user> — Mention loop\n"
            "• +vtarget <user> <text> — Custom mention loop\n"
            "• +stoptarget — Disarm targeting loop\n"
            "• +spam <text> — High-speed spam\n"
            "• +stopspam — Terminate active spam\n"
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
            "• +cluster — Node telemetry\n"
            "• +broadcast <text> — Network broadcast\n"
            "• +slayinpowergifted <id> — Add admin\n"
            "• +slayinpowertaken <id> — Revoke admin\n"
            "• +slayinfor — List admins\n"
            "• +gban <user> — Global ban\n"
            "• +ungban <user> — Global unban\n\n"
            f"⚡ Active Admins:\n{admin_list}"
        )

# --- Menu Callbacks ---

async def menu_callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data
    
    if data == "menu_close":
        return await query.message.delete()
    elif data == "open_panel":
        keyboard = [
            [InlineKeyboardButton("Abort All Active Tasks 🚨", callback_data="stop_all")],
            [InlineKeyboardButton("✝️ Return to Main Menu", callback_data="menu_1")]
        ]
        return await query.edit_message_text("🎛️ BATTLE-DECK CONTROL PANEL:\nDirect chat override active.", reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")
    elif data == "stop_all":
        chat_data = get_chat_data(query.message.chat_id)
        for task in list(chat_data["tasks"].values()): task.cancel()
        chat_data["tasks"].clear()
        chat_data["react_mode"] = None
        return await query.edit_message_text("🚨 ALL ACTIVE TASKS ABORTED.", reply_markup=get_menu_keyboard(1))
    elif data.startswith("menu_"):
        page = int(data.split("_")[1])
        await query.edit_message_text(get_menu_text(page), reply_markup=get_menu_keyboard(page), parse_mode="Markdown")

# --- Commands Implementation ---

async def cmd_gcnc(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id): return
    args = update.message.text.split()[1:]
    name = " ".join(args) or "KRISHSLAYIN"
    chat_data = get_chat_data(update.effective_chat.id)
    if "gcnc" in chat_data["tasks"]: chat_data["tasks"]["gcnc"].cancel()

    async def gcnc_loop():
        titles = [f"⚡ {name} ⚡", f"🔥 {name} 🔥", f"👑 {name} 👑"]
        idx = 0
        while True:
            try:
                await context.bot.set_chat_title(chat_id=update.effective_chat.id, title=titles[idx % len(titles)])
                idx += 1
            except Exception: pass
            await asyncio.sleep(1.5)
    task = asyncio.create_task(gcnc_loop())
    chat_data["tasks"]["gcnc"] = task
    await context.bot.send_message(chat_id=update.effective_chat.id, text="⚔️ Title loop activated.")

async def cmd_vgcnc(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id): return
    raw_text = update.message.text.replace("+vgcnc", "").strip()
    parts = raw_text.split(" ", 1)
    titles_raw = parts[1] if len(parts) > 1 else parts[0]
    titles = [t.strip() for t in titles_raw.split("|") if t.strip()]
    if not titles: return await context.bot.send_message(chat_id=update.effective_chat.id, text="Usage: +vgcnc Title 1 | Title 2")

    chat_data = get_chat_data(update.effective_chat.id)
    if "gcnc" in chat_data["tasks"]: chat_data["tasks"]["gcnc"].cancel()

    async def vgcnc_loop():
        idx = 0
        while True:
            try:
                await context.bot.set_chat_title(chat_id=update.effective_chat.id, title=titles[idx % len(titles)])
                idx += 1
            except Exception: pass
            await asyncio.sleep(1.5)
    task = asyncio.create_task(vgcnc_loop())
    chat_data["tasks"]["gcnc"] = task
    await context.bot.send_message(chat_id=update.effective_chat.id, text="⚡ Title Rotator engaged.")

async def cmd_stopgcnc(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_data = get_chat_data(update.effective_chat.id)
    if "gcnc" in chat_data["tasks"]:
        chat_data["tasks"]["gcnc"].cancel()
        del chat_data["tasks"]["gcnc"]
        await context.bot.send_message(chat_id=update.effective_chat.id, text="🛑 Title loop disarmed.")

async def cmd_target(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id): return
    args = update.message.text.split()[1:]
    user = args[0] if args else "@target"
    chat_data = get_chat_data(update.effective_chat.id)
    if "target" in chat_data["tasks"]: chat_data["tasks"]["target"].cancel()

    async def target_loop():
        while True:
            line = random.choice(TARGET_LINES)
            await context.bot.send_message(chat_id=update.effective_chat.id, text=f"{user}\n{line}")
            await asyncio.sleep(1.5)
    task = asyncio.create_task(target_loop())
    chat_data["tasks"]["target"] = task
    await context.bot.send_message(chat_id=update.effective_chat.id, text=f"🎯 Targeting engaged on {user}.")

async def cmd_vtarget(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id): return
    args = update.message.text.split()[1:]
    if len(args) < 2: return await context.bot.send_message(chat_id=update.effective_chat.id, text="Usage: +vtarget <user> <text>")
    user, custom_text = args[0], " ".join(args[1:])
    chat_data = get_chat_data(update.effective_chat.id)
    if "target" in chat_data["tasks"]: chat_data["tasks"]["target"].cancel()

    async def vtarget_loop():
        while True:
            await context.bot.send_message(chat_id=update.effective_chat.id, text=f"{user} {custom_text}")
            await asyncio.sleep(1.5)
    task = asyncio.create_task(vtarget_loop())
    chat_data["tasks"]["target"] = task
    await context.bot.send_message(chat_id=update.effective_chat.id, text=f"🎯 Custom targeting engaged on {user}.")

async def cmd_stoptarget(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_data = get_chat_data(update.effective_chat.id)
    if "target" in chat_data["tasks"]:
        chat_data["tasks"]["target"].cancel()
        del chat_data["tasks"]["target"]
        await context.bot.send_message(chat_id=update.effective_chat.id, text="🛑 Targeting disarmed.")

async def cmd_spam(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id): return
    text = " ".join(update.message.text.split()[1:])
    if not text: return await context.bot.send_message(chat_id=update.effective_chat.id, text="Usage: +spam <text>")
    chat_data = get_chat_data(update.effective_chat.id)
    if "spam" in chat_data["tasks"]: chat_data["tasks"]["spam"].cancel()

    async def spam_loop():
        while True:
            await context.bot.send_message(chat_id=update.effective_chat.id, text=text)
            await asyncio.sleep(0.4)
    task = asyncio.create_task(spam_loop())
    chat_data["tasks"]["spam"] = task
    await context.bot.send_message(chat_id=update.effective_chat.id, text="🚀 High-speed spam initialized.")

async def cmd_stopspam(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_data = get_chat_data(update.effective_chat.id)
    if "spam" in chat_data["tasks"]:
        chat_data["tasks"]["spam"].cancel()
        del chat_data["tasks"]["spam"]
        await context.bot.send_message(chat_id=update.effective_chat.id, text="🛑 Active spam terminated.")

async def cmd_flood(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id): return
    args = update.message.text.split()[1:]
    user = args[0] if args else "@target"
    chat_data = get_chat_data(update.effective_chat.id)
    if "flood" in chat_data["tasks"]: chat_data["tasks"]["flood"].cancel()

    async def flood_loop():
        while True:
            for line in FLOOD_LINES:
                await context.bot.send_message(chat_id=update.effective_chat.id, text=f"{user}\n{line}")
                await asyncio.sleep(0.4)
    task = asyncio.create_task(flood_loop())
    chat_data["tasks"]["flood"] = task
    await context.bot.send_message(chat_id=update.effective_chat.id, text=f"🌊 Flood active on {user}.")

async def cmd_vflood(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id): return
    args = update.message.text.split()[1:]
    if len(args) < 2: return await context.bot.send_message(chat_id=update.effective_chat.id, text="Usage: +vflood <user> <text>")
    user, text = args[0], " ".join(args[1:])
    chat_data = get_chat_data(update.effective_chat.id)
    if "flood" in chat_data["tasks"]: chat_data["tasks"]["flood"].cancel()

    async def vflood_loop():
        while True:
            await context.bot.send_message(chat_id=update.effective_chat.id, text=f"🌊 {user} {text}")
            await asyncio.sleep(0.3)
    task = asyncio.create_task(vflood_loop())
    chat_data["tasks"]["flood"] = task
    await context.bot.send_message(chat_id=update.effective_chat.id, text="🌊 Custom flood active.")

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

    async def photo_loop():
        while True:
            try: await context.bot.set_chat_photo(chat_id=update.effective_chat.id, photo=file_id)
            except Exception: pass
            await asyncio.sleep(5)
    task = asyncio.create_task(photo_loop())
    chat_data["tasks"]["gcpfp"] = task
    await context.bot.send_message(chat_id=update.effective_chat.id, text="🖼️ Photo loop engaged.")

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

    async def voice_loop():
        while True:
            await context.bot.send_voice(chat_id=update.effective_chat.id, voice=file_id)
            await asyncio.sleep(1)
    task = asyncio.create_task(voice_loop())
    chat_data["tasks"]["voiceflood"] = task
    await context.bot.send_message(chat_id=update.effective_chat.id, text="🎤 Voice flood active.")

async def cmd_stopvoiceflood(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_data = get_chat_data(update.effective_chat.id)
    if "voiceflood" in chat_data["tasks"]:
        chat_data["tasks"]["voiceflood"].cancel()
        del chat_data["tasks"]["voiceflood"]
        await context.bot.send_message(chat_id=update.effective_chat.id, text="🛑 Voice flood stopped.")

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

# Reaction Switch Commands
async def cmd_togglereactall(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id): return
    chat_data = get_chat_data(update.effective_chat.id)
    if chat_data["react_mode"] == "all":
        chat_data["react_mode"] = None
        await context.bot.send_message(chat_id=update.effective_chat.id, text="❌ Auto-Reaction for ALL users Disabled.")
    else:
        chat_data["react_mode"] = "all"
        await context.bot.send_message(chat_id=update.effective_chat.id, text="✅ Auto-Reaction Enabled for ALL users!")

async def cmd_togglereact(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id): return
    chat_data = get_chat_data(update.effective_chat.id)
    if chat_data["react_mode"] == "admin":
        chat_data["react_mode"] = None
        await context.bot.send_message(chat_id=update.effective_chat.id, text="❌ Admin Auto-Reaction Disabled.")
    else:
        chat_data["react_mode"] = "admin"
        await context.bot.send_message(chat_id=update.effective_chat.id, text="✅ Auto-Reaction Enabled for OWNER & ADMINS only!")

async def cmd_stopall(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id): return
    chat_data = get_chat_data(update.effective_chat.id)
    for task in list(chat_data["tasks"].values()): task.cancel()
    chat_data["tasks"].clear()
    chat_data["react_mode"] = None
    await context.bot.send_message(chat_id=update.effective_chat.id, text="🚨 EMERGENCY KILL SWITCH ENGAGED! All threads stopped.")

# --- Utilities & Owner Commands ---

async def cmd_scan(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat = update.effective_chat
    members = await chat.get_member_count()
    await context.bot.send_message(chat_id=update.effective_chat.id, text=f"📊 CHAT MATRIX SCAN:\n• Title: {chat.title}\n• ID: {chat.id}\n• Members: {members}")

async def cmd_ping(update: Update, context: ContextTypes.DEFAULT_TYPE):
    start = time.time()
    msg = await context.bot.send_message(chat_id=update.effective_chat.id, text="📡 Pinging cluster...")
    latency = round((time.time() - start) * 1000, 2)
    await msg.edit_text(f"📶 LATENCY TELEMETRY: {latency}ms 🟢")

async def cmd_getid(update: Update, context: ContextTypes.DEFAULT_TYPE):
    target = update.message.reply_to_message.from_user if update.message.reply_to_message else update.effective_user
    await context.bot.send_message(chat_id=update.effective_chat.id, text=f"🆔 User ID: {target.id}\n💬 Chat ID: {update.effective_chat.id}")

async def cmd_status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    tasks = len(get_chat_data(update.effective_chat.id)["tasks"])
    await context.bot.send_message(chat_id=update.effective_chat.id, text=f"⚙️ CLUSTER STATE: Active\n🔥 Active Tasks: {tasks}")

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

async def cmd_cluster(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != OWNER_ID: return
    await context.bot.send_message(chat_id=update.effective_chat.id, text="🖥️ CLUSTER HEALTH: Master Nodes Operating Efficiently.")

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

async def cmd_ungban(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != OWNER_ID: return
    reply = update.message.reply_to_message
    args = update.message.text.split()[1:]
    target_id = reply.from_user.id if reply else (int(args[0]) if args and args[0].isdigit() else None)
    if not target_id: return await context.bot.send_message(chat_id=update.effective_chat.id, text="Reply to target user or pass ID.")
    GBANNED_USERS.discard(target_id)
    await context.bot.send_message(chat_id=update.effective_chat.id, text=f"✅ Target {target_id} removed from blacklist.")

# --- Master Message Core Router ---

async def global_message_router(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.from_user: return
    user_id = update.message.from_user.id
    username = update.message.from_user.username.lower() if update.message.from_user.username else ""
    chat_id = update.effective_chat.id
    chat_data = get_chat_data(chat_id)
    text = update.message.text.strip() if update.message.text else ""

    # PFP Stripper check
    if chat_data.get("pfpstripper") and update.message.new_chat_photo:
        try: 
            await context.bot.delete_message(chat_id=chat_id, message_id=update.message.message_id)
            return
        except Exception: pass

    # Global Ban & Auto Mute Traps
    if user_id in GBANNED_USERS or user_id in chat_data["muted"]:
        try: return await update.message.delete()
        except Exception: pass

    # Media Stripper Trap
    if user_id in chat_data["stripmedia"] and (update.message.photo or update.message.video or update.message.document):
        try: return await update.message.delete()
        except Exception: pass

    # Auto Reply Trap
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

    # Repeat Voice Trap (reptts)
    if user_id in chat_data["reptts"] and text and gTTS is not None:
        try:
            tts = gTTS(text=text, lang="hi")
            tts.save("reptts.mp3")
            await context.bot.send_voice(chat_id=chat_id, voice=open("reptts.mp3", "rb"))
        except Exception: pass

    # Reaction Logic Trigger
    react_mode = chat_data.get("react_mode")
    if react_mode is not None and not text.startswith("+"):
        should_react = False
        if react_mode == "all":
            should_react = True
        elif react_mode == "admin":
            if is_admin(user_id):
                should_react = True

        if should_react:
            try:
                selected_emoji = random.choice(REACTION_EMOJIS)
                await context.bot.set_message_reaction(chat_id=chat_id, message_id=update.message.message_id, reaction=[selected_emoji])
            except Exception: pass

    # Dynamic Commands Router
    if text.startswith("+"):
        try: await update.message.delete()
        except Exception: pass

        cmd = text.split()[0][1:].lower()
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
            "mute": cmd_mute, "unmute": cmd_unmute, "mutelist": cmd_mutelist,
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
            "slayinfor": cmd_slayinfor, "gban": cmd_gban, "ungban": cmd_ungban
        }
        if cmd in routes:
            handler = routes[cmd]
            await handler(update, context)

def main():
    TOKEN = os.environ.get("BOT_TOKEN")
    if not TOKEN:
        print("BOT_TOKEN missing!")
        return

    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CallbackQueryHandler(menu_callback_handler))
    app.add_handler(MessageHandler(filters.ALL, global_message_router))

    print("Krishslayin ✝️ Core Fully Synchronized.")
    app.run_polling()

if __name__ == '__main__':
    main()
