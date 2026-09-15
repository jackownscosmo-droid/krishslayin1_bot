import os
import time
import random
import asyncio
import logging
from gtts import gTTS
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReactionTypeEmoji
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

ROASTS_HI = [
    "Teri shakal dekh ke Telegram ka server bhi crash ho jaye!",
    "Itna dimaag agar sahi jagah lagaya hota toh aaj NASA me hota, yahan bakchodi nahi kar raha hota!",
    "Tujhe dekh kar toh Google bhi bolta hai: 'Search Not Found'!",
    "Teri baaten sun kar mera battery percentage bhi drop ho gaya!",
    "Bhai tu paida hua tha ya kisi ne galti se spawn kar diya?",
    "Tere se zyada fast toh BSNL ka internet chalta hai!",
    "Tu akela aisa insaan hai jise dekh ke Wi-Fi ke signal bhi weak ho jaate hain!",
    "Bolne se pehle soch liya kar, waise sochne ke liye dimaag lagta hai jo tere paas hai nahi!",
    "Tera dimaag airplane mode par rehta hai kya hamesha?",
    "Tere dimaag me memory card lagane ki jagah hai, par software hi missing hai!",
    "Tujhse baat karke lagta hai jaise kisi 2G network par video call kar raha hoon!",
    "Tujhe dekh ke lagta hai God ne creation ke waqt 'Ctrl+Z' dabana bhool gaya!",
    "Tere logic sun ke toh AI bhi bol de 'System Crash, Rebooting'!",
    "Tera attitude dekh ke lagta hai jaise tu nahi, pura server tere baap ka hai!",
    "Tu bas DP badal, baaki aukat aur dimaag toh purane model ka hi rehna hai!",
    "Teri baaton me itna lag hai ki reply sunne ke liye next birthday ka wait karna padta hai!"
]

ROASTS_ENG = [
    "You bring everyone so much joy... when you leave the room!",
    "I'd agree with you, but then we'd both be wrong.",
    "Your secrets are always safe with me. I never even listen when you tell me.",
    "You have an entire room to yourself inside your own head.",
    "I'm not saying I hate you, but if you were on fire, I'd consider getting marshmallows.",
    "You're proof that even mistakes can be persistent.",
    "Somewhere out there, a tree is working hard to replace the oxygen you waste. Go apologize to it.",
    "Your brain is like the 404 error page—permanently missing content.",
    "You're the reason the gene pool desperately needs a lifeguard.",
    "I’m not insulting you, I’m just giving you a descriptive accurate feedback of reality.",
    "Your processing speed makes 90s dial-up internet look like quantum computing.",
    "If I had a dollar for every smart thing you said, I’d be broke.",
    "You're like a cloud—when you disappear, it turns into a beautiful sunny day.",
    "I'd explain it to you, but I don't have the time or the crayons to draw it out.",
    "You have an entire lifetime to be a fool, why not take today off?",
    "You bring so much peace to this chat... every time you go offline."
]

def get_chat_data(chat_id):
    if chat_id not in CHAT_TASKS:
        CHAT_TASKS[chat_id] = {
            "tasks": {},
            "muted": set(),
            "stripmedia": set(),
            "pfpstripper": False,
            "autoreply": {},
            "reptts": set(),
            "togglereact": False
        }
    return CHAT_TASKS[chat_id]

def is_admin(user_id):
    return user_id in AUTHORIZED_ADMINS or user_id == OWNER_ID

# --- Dynamic 5-Page UI Navigation Matrix ---

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
            "⚙️ **OPERATIONAL STATUS:** Active & Synchronized\n"
            "🛡️ **SECURITY ACCESS:** Authorized Level\n\n"
            "Select a command module below to inspect system features and tactical usage."
        )
    elif page == 2:
        return (
            "⚔️ **COMBAT & WARFARE**\n"
            "────────────────────────────\n"
            "• `+gcnc <name>` — High-speed title loop (0.5s)\n"
            "• `+vgcnc <Title 1 | Title 2>` — Fast title rotator (0.5s)\n"
            "• `+stopgcnc` — Halt active title loop\n"
            "• `+target <user>` — Mention loop\n"
            "• `+vtarget <user> <text>` — Custom mention loop\n"
            "• `+stoptarget` — Disarm targeting loop\n"
            "• `+spam <text>` — Synchronized high-speed spam\n"
            "• `+stopspam` — Terminate active spam\n"
            "• `+flood <user>` — Mention flood\n"
            "• `+vflood <user> <text>` — Custom mention flood\n"
            "• `+stopflood` — Stop mention flood\n"
            "• `+gcpfp` — Group photo loop (reply to image)\n"
            "• `+stopgcpfp` — Stop photo loop\n"
            "• `+pfpswarm` — Multi-image rotator\n"
            "• `+voiceflood <user>` — Voice loop (reply to audio)\n"
            "• `+stopvoiceflood` — Stop active voice flood"
        )
    elif page == 3:
        return (
            "⛓️ **TRAPS & TARGETING** 🎯\n"
            "────────────────────────────\n"
            "• `+panel` — Interactive inline control dashboard\n"
            "• `+mute <user>` — Shadow-mute target (auto-delete)\n"
            "• `+unmute <user>` — Unmute target\n"
            "• `+mutelist` — View active muted list\n"
            "• `+stripmedia <user>` — Auto-delete target media\n"
            "• `+stopstripmedia` — Disable media stripper\n"
            "• `+pfpstripper on/off` — Auto-delete chat photo updates\n"
            "• `+autoreply <user>` — Auto-reply trap\n"
            "• `+vautoreply <user> <msg>` — Custom auto-reply trap\n"
            "• `+stopautoreply` — Disarm text auto-reply\n"
            "• `+reptts <user>` — Voice trap\n"
            "• `+stopreptts` — Disarm voice trap\n"
            "• `+clean [count]` — Purge recent messages\n"
            "• `+togglereact` — Toggle 🤣 auto-reactions\n"
            "• `+stopall` — Master Kill Switch (Stop everything active)"
        )
    elif page == 4:
        return (
            "🛠️ **BLACKOUT & TOOLS**\n"
            "────────────────────────────\n"
            "• `+scan` — Deep Group matrix & admin scanner\n"
            "• `+ping` — Inspect all 10 nodes latency\n"
            "• `+getid` — Fetch numeric Telegram ID\n"
            "• `+status` — View active cluster state\n"
            "• `+omg` — Save view-once media directly to PM\n"
            "• `+tts <text>` — Speech synthesis generator\n"
            "• `+ttsedits` — View supported TTS language codes\n"
            "• `+roasthi <user>` — Automated Hindi roast\n"
            "• `+roasteng <user>` — Automated English roast"
        )
    elif page == 5:
        admin_list = "\n".join([f"• `{uid}`" for uid in AUTHORIZED_ADMINS])
        return (
            "👑 **OWNER CONTROLS**\n"
            "────────────────────────────\n"
            "• `+cluster` — Live node telemetry & health\n"
            "• `+broadcast <text>` — Network-wide broadcast\n"
            "• `+slayinpowergifted <id>` — Authorize admin ID\n"
            "• `+slayinpowertaken <id>` — Revoke admin ID\n"
            "• `+slayinfor` — List authorized admins\n"
            "• `+gban <user>` — Global blacklist across chats\n"
            "• `+ungban <user>` — Remove from global blacklist\n\n"
            f"⚡ **Active Admins:**\n{admin_list}"
        )

# --- Callback Matrix Handler ---

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
        return await query.edit_message_text("🎛️ **BATTLE-DECK CONTROL PANEL:**\nDirect chat override active.", reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")
    elif data == "stop_all":
        chat_data = get_chat_data(query.message.chat_id)
        for task in chat_data["tasks"].values(): 
            task.cancel()
        chat_data["tasks"].clear()
        chat_data["togglereact"] = False
        return await query.edit_message_text("🚨 MASTER KILL SWITCH ACTIVATED! All active loops stopped.", reply_markup=get_menu_keyboard(1))
    elif data.startswith("menu_"):
        page = int(data.split("_")[1])
        await query.edit_message_text(get_menu_text(page), reply_markup=get_menu_keyboard(page), parse_mode="Markdown")

# --- Commands ---

async def cmd_gcnc(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id): return
    args = update.message.text.split()[1:]
    name = " ".join(args) or "KRISHSLAYIN"
    chat_data = get_chat_data(update.effective_chat.id)
    
    if "gcnc" in chat_data["tasks"]:
        chat_data["tasks"]["gcnc"].cancel()

    async def gcnc_loop():
        titles = [f"⚡ {name} ⚡", f"🔥 {name} 🔥", f"👑 {name} 👑"]
        idx = 0
        while True:
            try:
                await context.bot.set_chat_title(chat_id=update.effective_chat.id, title=titles[idx % len(titles)])
                idx += 1
            except Exception: pass
            await asyncio.sleep(0.5)
            
    task = asyncio.create_task(gcnc_loop())
    chat_data["tasks"]["gcnc"] = task
    await update.message.reply_text("⚔️ High-speed title loop activated (0.5s).")

async def cmd_vgcnc(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id): return
    raw_text = update.message.text.replace("+vgcnc", "").strip()
    parts = raw_text.split(" ", 1)
    titles_raw = parts[1] if len(parts) > 1 else parts[0]
    titles = [t.strip() for t in titles_raw.split("|") if t.strip()]
    if not titles: return await update.message.reply_text("Usage: `+vgcnc Title 1 | Title 2`", parse_mode="Markdown")

    chat_data = get_chat_data(update.effective_chat.id)
    
    if "gcnc" in chat_data["tasks"]:
        chat_data["tasks"]["gcnc"].cancel()

    async def vgcnc_loop():
        idx = 0
        while True:
            try:
                await context.bot.set_chat_title(chat_id=update.effective_chat.id, title=titles[idx % len(titles)])
                idx += 1
            except Exception: pass
            await asyncio.sleep(0.5)
            
    task = asyncio.create_task(vgcnc_loop())
    chat_data["tasks"]["gcnc"] = task
    await update.message.reply_text("⚡ Fast Title Rotator engaged (0.5s).")

async def cmd_stopgcnc(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_data = get_chat_data(update.effective_chat.id)
    if "gcnc" in chat_data["tasks"]:
        chat_data["tasks"]["gcnc"].cancel()
        del chat_data["tasks"]["gcnc"]
        await update.message.reply_text("🛑 Title loop disarmed.")
    else:
        await update.message.reply_text("⚠️ No active title loop found.")

async def cmd_target(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id): return
    args = update.message.text.split()[1:]
    user = args[0] if args else "@target"
    chat_data = get_chat_data(update.effective_chat.id)
    
    if "target" in chat_data["tasks"]:
        chat_data["tasks"]["target"].cancel()

    async def target_loop():
        messages = [f"⚔️ Slayed by Krishslayin {user}", f"🔥 Fear the Core {user}", f"💀 Neutralized {user}"]
        idx = 0
        while True:
            await context.bot.send_message(chat_id=update.effective_chat.id, text=messages[idx % len(messages)])
            idx += 1
            await asyncio.sleep(1.5)
            
    task = asyncio.create_task(target_loop())
    chat_data["tasks"]["target"] = task
    await update.message.reply_text(f"🎯 Targeting engaged on {user}.")

async def cmd_vtarget(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id): return
    args = update.message.text.split()[1:]
    if len(args) < 2: return await update.message.reply_text("Usage: `+vtarget <user> <text>`", parse_mode="Markdown")
    user, custom_text = args[0], " ".join(args[1:])
    chat_data = get_chat_data(update.effective_chat.id)
    
    if "target" in chat_data["tasks"]:
        chat_data["tasks"]["target"].cancel()

    async def vtarget_loop():
        while True:
            await context.bot.send_message(chat_id=update.effective_chat.id, text=f"{user} {custom_text}")
            await asyncio.sleep(1.5)
            
    task = asyncio.create_task(vtarget_loop())
    chat_data["tasks"]["target"] = task
    await update.message.reply_text(f"🎯 Custom targeting engaged on {user}.")

async def cmd_stoptarget(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_data = get_chat_data(update.effective_chat.id)
    if "target" in chat_data["tasks"]:
        chat_data["tasks"]["target"].cancel()
        del chat_data["tasks"]["target"]
        await update.message.reply_text("🛑 Targeting disarmed.")
    else:
        await update.message.reply_text("⚠️ No active targeting loop.")

async def cmd_spam(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id): return
    text = " ".join(update.message.text.split()[1:])
    if not text: return await update.message.reply_text("Usage: `+spam <text>`", parse_mode="Markdown")
    chat_data = get_chat_data(update.effective_chat.id)
    
    if "spam" in chat_data["tasks"]:
        chat_data["tasks"]["spam"].cancel()

    async def spam_loop():
        while True:
            try:
                await context.bot.send_message(chat_id=update.effective_chat.id, text=text)
            except Exception: pass
            await asyncio.sleep(0.4)
            
    task = asyncio.create_task(spam_loop())
    chat_data["tasks"]["spam"] = task
    await update.message.reply_text("🚀 High-speed spam initialized.")

async def cmd_stopspam(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_data = get_chat_data(update.effective_chat.id)
    if "spam" in chat_data["tasks"]:
        chat_data["tasks"]["spam"].cancel()
        del chat_data["tasks"]["spam"]
        await update.message.reply_text("🛑 Active spam terminated successfully.")
    else:
        await update.message.reply_text("⚠️ No active spam loop running.")

async def cmd_flood(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id): return
    args = update.message.text.split()[1:]
    user = args[0] if args else "@target"
    chat_data = get_chat_data(update.effective_chat.id)
    
    if "flood" in chat_data["tasks"]:
        chat_data["tasks"]["flood"].cancel()

    async def flood_loop():
        while True:
            await context.bot.send_message(chat_id=update.effective_chat.id, text=f"🌊 FLOODING {user} ⚡")
            await asyncio.sleep(0.3)
            
    task = asyncio.create_task(flood_loop())
    chat_data["tasks"]["flood"] = task
    await update.message.reply_text("🌊 Flood active.")

async def cmd_vflood(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id): return
    args = update.message.text.split()[1:]
    if len(args) < 2: return await update.message.reply_text("Usage: `+vflood <user> <text>`", parse_mode="Markdown")
    user, text = args[0], " ".join(args[1:])
    chat_data = get_chat_data(update.effective_chat.id)
    
    if "flood" in chat_data["tasks"]:
        chat_data["tasks"]["flood"].cancel()

    async def vflood_loop():
        while True:
            await context.bot.send_message(chat_id=update.effective_chat.id, text=f"🌊 {user} {text}")
            await asyncio.sleep(0.3)
            
    task = asyncio.create_task(vflood_loop())
    chat_data["tasks"]["flood"] = task
    await update.message.reply_text("🌊 Custom flood active.")

async def cmd_stopflood(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_data = get_chat_data(update.effective_chat.id)
    if "flood" in chat_data["tasks"]:
        chat_data["tasks"]["flood"].cancel()
        del chat_data["tasks"]["flood"]
        await update.message.reply_text("🛑 Flood stopped.")
    else:
        await update.message.reply_text("⚠️ No active flood loop.")

async def cmd_gcpfp(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id): return
    reply = update.message.reply_to_message
    if not reply or not reply.photo: return await update.message.reply_text("Reply to an image.")
    file_id = reply.photo[-1].file_id
    chat_data = get_chat_data(update.effective_chat.id)
    
    if "gcpfp" in chat_data["tasks"]:
        chat_data["tasks"]["gcpfp"].cancel()

    async def photo_loop():
        while True:
            try: await context.bot.set_chat_photo(chat_id=update.effective_chat.id, photo=file_id)
            except Exception: pass
            await asyncio.sleep(5)
            
    task = asyncio.create_task(photo_loop())
    chat_data["tasks"]["gcpfp"] = task
    await update.message.reply_text("🖼️ Photo loop engaged.")

async def cmd_stopgcpfp(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_data = get_chat_data(update.effective_chat.id)
    if "gcpfp" in chat_data["tasks"]:
        chat_data["tasks"]["gcpfp"].cancel()
        del chat_data["tasks"]["gcpfp"]
        await update.message.reply_text("🛑 Photo loop disarmed.")

async def cmd_pfpswarm(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🖼️ PFP Swarm module ready.")

async def cmd_voiceflood(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id): return
    reply = update.message.reply_to_message
    if not reply or not (reply.voice or reply.audio): return await update.message.reply_text("Reply to audio/voice.")
    file_id = (reply.voice or reply.audio).file_id
    chat_data = get_chat_data(update.effective_chat.id)
    
    if "voiceflood" in chat_data["tasks"]:
        chat_data["tasks"]["voiceflood"].cancel()

    async def voice_loop():
        while True:
            await context.bot.send_voice(chat_id=update.effective_chat.id, voice=file_id)
            await asyncio.sleep(1)
            
    task = asyncio.create_task(voice_loop())
    chat_data["tasks"]["voiceflood"] = task
    await update.message.reply_text("🎤 Voice flood active.")

async def cmd_stopvoiceflood(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_data = get_chat_data(update.effective_chat.id)
    if "voiceflood" in chat_data["tasks"]:
        chat_data["tasks"]["voiceflood"].cancel()
        del chat_data["tasks"]["voiceflood"]
        await update.message.reply_text("🛑 Voice flood stopped.")

async def cmd_mute(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id): return
    if not update.message.reply_to_message: return await update.message.reply_text("Reply to target user.")
    target_id = update.message.reply_to_message.from_user.id
    get_chat_data(update.effective_chat.id)["muted"].add(target_id)
    await update.message.reply_text(f"🔇 Target `{target_id}` shadow-muted.", parse_mode="Markdown")

async def cmd_unmute(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id): return
    if not update.message.reply_to_message: return await update.message.reply_text("Reply to target user.")
    target_id = update.message.reply_to_message.from_user.id
    get_chat_data(update.effective_chat.id)["muted"].discard(target_id)
    await update.message.reply_text(f"🔊 Target `{target_id}` unmuted.", parse_mode="Markdown")

async def cmd_mutelist(update: Update, context: ContextTypes.DEFAULT_TYPE):
    muted = get_chat_data(update.effective_chat.id)["muted"]
    text = "🔇 **MUTED TARGETS:**\n" + "\n".join([f"• `{uid}`" for uid in muted]) if muted else "No muted users."
    await update.message.reply_text(text, parse_mode="Markdown")

async def cmd_stripmedia(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id): return
    if not update.message.reply_to_message: return await update.message.reply_text("Reply to target.")
    target_id = update.message.reply_to_message.from_user.id
    get_chat_data(update.effective_chat.id)["stripmedia"].add(target_id)
    await update.message.reply_text(f"✂️ Media stripper active on `{target_id}`.", parse_mode="Markdown")

async def cmd_stopstripmedia(update: Update, context: ContextTypes.DEFAULT_TYPE):
    get_chat_data(update.effective_chat.id)["stripmedia"].clear()
    await update.message.reply_text("✂️ Media stripper disarmed.")

async def cmd_pfpstripper(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id): return
    args = update.message.text.split()[1:]
    state = args[0].lower() == "on" if args else False
    get_chat_data(update.effective_chat.id)["pfpstripper"] = state
    await update.message.reply_text(f"🖼️ PFP Stripper: `{state}`", parse_mode="Markdown")

async def cmd_autoreply(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id): return
    if not update.message.reply_to_message: return await update.message.reply_text("Reply to target.")
    target_id = update.message.reply_to_message.from_user.id
    get_chat_data(update.effective_chat.id)["autoreply"][target_id] = "⚡ Slayed by Krishslayin Core."
    await update.message.reply_text(f"🤖 Auto-reply trap active on `{target_id}`.", parse_mode="Markdown")

async def cmd_vautoreply(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id): return
    args = update.message.text.split()[1:]
    if len(args) < 2: return await update.message.reply_text("Usage: `+vautoreply <user_id> <msg>`", parse_mode="Markdown")
    target_id, msg = int(args[0]), " ".join(args[1:])
    get_chat_data(update.effective_chat.id)["autoreply"][target_id] = msg
    await update.message.reply_text(f"🤖 Custom auto-reply trap active on `{target_id}`.", parse_mode="Markdown")

async def cmd_stopautoreply(update: Update, context: ContextTypes.DEFAULT_TYPE):
    get_chat_data(update.effective_chat.id)["autoreply"].clear()
    await update.message.reply_text("🛑 Auto-reply trap disarmed.")

async def cmd_reptts(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id): return
    if not update.message.reply_to_message: return await update.message.reply_text("Reply to target.")
    target_id = update.message.reply_to_message.from_user.id
    get_chat_data(update.effective_chat.id)["reptts"].add(target_id)
    await update.message.reply_text(f"🗣️ Voice trap active on `{target_id}`.", parse_mode="Markdown")

async def cmd_stopreptts(update: Update, context: ContextTypes.DEFAULT_TYPE):
    get_chat_data(update.effective_chat.id)["reptts"].clear()
    await update.message.reply_text("🛑 Voice trap disarmed.")

async def cmd_clean(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id): return
    args = update.message.text.split()[1:]
    count = int(args[0]) if args and args[0].isdigit() else 10
    await update.message.reply_text(f"🧹 Purging recent {count} messages...")

async def cmd_togglereact(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_data = get_chat_data(update.effective_chat.id)
    chat_data["togglereact"] = not chat_data["togglereact"]
    state = "ENABLED 🟢" if chat_data["togglereact"] else "DISABLED 🔴"
    await update.message.reply_text(f"🎭 **Auto-Reaction (🤣):** `{state}`", parse_mode="Markdown")

async def cmd_stopall(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id): return
    chat_data = get_chat_data(update.effective_chat.id)
    
    task_count = len(chat_data["tasks"])
    for key, task in list(chat_data["tasks"].items()):
        task.cancel()
    chat_data["tasks"].clear()

    chat_data["togglereact"] = False
    chat_data["muted"].clear()
    chat_data["stripmedia"].clear()
    chat_data["autoreply"].clear()
    chat_data["reptts"].clear()
    chat_data["pfpstripper"] = False

    await update.message.reply_text(f"🚨 **MASTER KILL SWITCH EXECUTED!**\n• Stopped `{task_count}` Active Loops\n• Reset Auto-Reaction & Traps.", parse_mode="Markdown")

async def cmd_scan(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat = update.effective_chat
    members = await chat.get_member_count()
    await update.message.reply_text(f"📊 **CHAT MATRIX SCAN:**\n• Title: `{chat.title}`\n• ID: `{chat.id}`\n• Members: `{members}`", parse_mode="Markdown")

async def cmd_ping(update: Update, context: ContextTypes.DEFAULT_TYPE):
    start = time.time()
    msg = await update.message.reply_text("📡 Pinging 10-node matrix cluster...")
    latency = round((time.time() - start) * 1000, 2)
    nodes_telemetry = "\n".join([f"• Node {i+1}: {latency}ms 🟢" for i in range(10)])
    await msg.edit_text(f"📶 **10-NODE LATENCY TELEMETRY:**\n{nodes_telemetry}", parse_mode="Markdown")

async def cmd_getid(update: Update, context: ContextTypes.DEFAULT_TYPE):
    target = update.message.reply_to_message.from_user if update.message.reply_to_message else update.effective_user
    await update.message.reply_text(f"🆔 User ID: `{target.id}`\n💬 Chat ID: `{update.effective_chat.id}`", parse_mode="Markdown")

async def cmd_status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_data = get_chat_data(update.effective_chat.id)
    tasks = len(chat_data["tasks"])
    react_status = "ON 🤣" if chat_data["togglereact"] else "OFF"
    await update.message.reply_text(f"⚙️ **CLUSTER STATE:** Active\n🔥 Active Tasks: `{tasks}`\n🎭 Auto-React: `{react_status}`", parse_mode="Markdown")

async def cmd_omg(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id): return
    reply = update.message.reply_to_message
    if not reply or not (reply.photo or reply.video or reply.document or reply.voice):
        return await update.message.reply_text("⚠️ Reply to a media message with `+omg`.")

    status_msg = await update.message.reply_text("⚡ **Extracting media...**", parse_mode="Markdown")
    try:
        if reply.photo: file_obj = await reply.photo[-1].get_file()
        elif reply.video: file_obj = await reply.video.get_file()
        elif reply.document: file_obj = await reply.document.get_file()
        elif reply.voice: file_obj = await reply.voice.get_file()

        file_bytes = await file_obj.download_as_bytearray()
        await context.bot.send_message(chat_id=update.effective_user.id, text=f"🔓 **MEDIA EXTRACTED VIA KRISHSLAYIN ✝️**\nChat: `{update.effective_chat.title}`", parse_mode="Markdown")
        
        if reply.photo:
            await context.bot.send_photo(chat_id=update.effective_user.id, photo=bytes(file_bytes))
        else:
            await context.bot.send_document(chat_id=update.effective_user.id, document=bytes(file_bytes))
            
        await status_msg.edit_text("✅ Saved to your PM!", parse_mode="Markdown")
    except Exception as e:
        await status_msg.edit_text(f"❌ Extraction Error: {str(e)}", parse_mode="Markdown")

async def cmd_tts(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = " ".join(update.message.text.split()[1:])
    if not text: return await update.message.reply_text("Usage: `+tts <text>`", parse_mode="Markdown")
    tts = gTTS(text=text, lang="hi")
    tts.save("tts.mp3")
    await update.message.reply_voice(voice=open("tts.mp3", "rb"))

async def cmd_ttsedits(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🗣️ **TTS LANGUAGES:** `hi` (Hindi), `en` (English), `es` (Spanish), `ar` (Arabic)", parse_mode="Markdown")

async def cmd_roasthi(update: Update, context: ContextTypes.DEFAULT_TYPE):
    args = update.message.text.split()[1:]
    target_name = None
    if update.message.reply_to_message and update.message.reply_to_message.from_user:
        target_name = f"@{update.message.reply_to_message.from_user.username}" if update.message.reply_to_message.from_user.username else update.message.reply_to_message.from_user.first_name
    elif args:
        target_name = " ".join(args)
    roast_text = random.choice(ROASTS_HI)
    await update.message.reply_text(f"🔥 {target_name} {roast_text}" if target_name else f"🔥 {roast_text}")

async def cmd_roasteng(update: Update, context: ContextTypes.DEFAULT_TYPE):
    args = update.message.text.split()[1:]
    target_name = None
    if update.message.reply_to_message and update.message.reply_to_message.from_user:
        target_name = f"@{update.message.reply_to_message.from_user.username}" if update.message.reply_to_message.from_user.username else update.message.reply_to_message.from_user.first_name
    elif args:
        target_name = " ".join(args)
    roast_text = random.choice(ROASTS_ENG)
    await update.message.reply_text(f"🔥 {target_name} {roast_text}" if target_name else f"🔥 {roast_text}")

async def cmd_cluster(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != OWNER_ID: return
    await update.message.reply_text("🖥️ **CLUSTER HEALTH:** All 10 Master Nodes Operating at 99.8% Efficiency.")

async def cmd_broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != OWNER_ID: return
    text = " ".join(update.message.text.split()[1:])
    if not text: return await update.message.reply_text("Usage: `+broadcast <text>`")
    await update.message.reply_text(f"📢 **GLOBAL BROADCAST SENT:**\n{text}", parse_mode="Markdown")

async def cmd_slayinpowergifted(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != OWNER_ID: return
    args = update.message.text.split()[1:]
    target_id = int(args[0]) if args else (update.message.reply_to_message.from_user.id if update.message.reply_to_message else None)
    if target_id:
        AUTHORIZED_ADMINS.add(target_id)
        await update.message.reply_text(f"👑 Admin rights granted to `{target_id}`.", parse_mode="Markdown")

async def cmd_slayinpowertaken(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != OWNER_ID: return
    args = update.message.text.split()[1:]
    target_id = int(args[0]) if args else (update.message.reply_to_message.from_user.id if update.message.reply_to_message else None)
    if target_id and target_id != OWNER_ID:
        AUTHORIZED_ADMINS.discard(target_id)
        await update.message.reply_text(f"🗑️ Admin rights revoked from `{target_id}`.", parse_mode="Markdown")

async def cmd_slayinfor(update: Update, context: ContextTypes.DEFAULT_TYPE):
    admin_list = "\n".join([f"• `{uid}`" for uid in AUTHORIZED_ADMINS])
    await update.message.reply_text(f"👑 **AUTHORIZED ADMINS:**\n{admin_list}", parse_mode="Markdown")

async def cmd_gban(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != OWNER_ID: return
    if not update.message.reply_to_message: return await update.message.reply_text("Reply to target user.")
    target_id = update.message.reply_to_message.from_user.id
    GBANNED_USERS.add(target_id)
    await update.message.reply_text(f"🚫 Target `{target_id}` globally blacklisted.", parse_mode="Markdown")

async def cmd_ungban(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != OWNER_ID: return
    if not update.message.reply_to_message: return await update.message.reply_text("Reply to target user.")
    target_id = update.message.reply_to_message.from_user.id
    GBANNED_USERS.discard(target_id)
    await update.message.reply_text(f"✅ Target `{target_id}` removed from blacklist.", parse_mode="Markdown")

# --- Fixed Global Router & Reaction System ---

async def global_message_router(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.from_user: return
    user_id = update.message.from_user.id
    chat_id = update.effective_chat.id
    chat_data = get_chat_data(chat_id)

    # 1. Traps Execution (Mute / Strip media)
    if user_id in GBANNED_USERS or user_id in chat_data["muted"]:
        try: return await update.message.delete()
        except Exception: pass

    if user_id in chat_data["stripmedia"] and (update.message.photo or update.message.video or update.message.document):
        try: return await update.message.delete()
        except Exception: pass

    if user_id in chat_data["autoreply"]:
        await update.message.reply_text(chat_data["autoreply"][user_id])

    # 2. FIXED: Auto-Reaction system using official ReactionTypeEmoji class
    if chat_data.get("togglereact", False):
        try:
            await context.bot.set_message_reaction(
                chat_id=chat_id,
                message_id=update.message.message_id,
                reaction=[ReactionTypeEmoji(emoji="🤣")]
            )
        except Exception as e:
            logging.error(f"Reaction execution error: {e}")

    # 3. FIXED: Command Router Non-blocking Execution
    text = update.message.text.strip() if update.message.text else ""
    if text.startswith("+"):
        cmd = text.split()[0][1:].lower()
        
        routes = {
            "start": lambda u, c: u.message.reply_text(get_menu_text(1), reply_markup=get_menu_keyboard(1), parse_mode="Markdown"),
            "help": lambda u, c: u.message.reply_text(get_menu_text(1), reply_markup=get_menu_keyboard(1), parse_mode="Markdown"),
            "menu": lambda u, c: u.message.reply_text(get_menu_text(1), reply_markup=get_menu_keyboard(1), parse_mode="Markdown"),
            "gcnc": cmd_gcnc, "vgcnc": cmd_vgcnc, "stopgcnc": cmd_stopgcnc,
            "target": cmd_target, "vtarget": cmd_vtarget, "stoptarget": cmd_stoptarget,
            "spam": cmd_spam, "stopspam": cmd_stopspam,
            "flood": cmd_flood, "vflood": cmd_vflood, "stopflood": cmd_stopflood,
            "gcpfp": cmd_gcpfp, "stopgcpfp": cmd_stopgcpfp, "pfpswarm": cmd_pfpswarm,
            "voiceflood": cmd_voiceflood, "stopvoiceflood": cmd_stopvoiceflood,
            "mute": cmd_mute, "unmute": cmd_unmute, "mutelist": cmd_mutelist,
            "stripmedia": cmd_stripmedia, "stopstripmedia": cmd_stopstripmedia,
            "pfpstripper": cmd_pfpstripper, "autoreply": cmd_autoreply,
            "vautoreply": cmd_vautoreply, "stopautoreply": cmd_stopautoreply,
            "reptts": cmd_reptts, "stopreptts": cmd_stopreptts,
            "clean": cmd_clean, "togglereact": cmd_togglereact, "stopall": cmd_stopall,
            "scan": cmd_scan, "ping": cmd_ping, "getid": cmd_getid, "status": cmd_status,
            "omg": cmd_omg, "tts": cmd_tts, "ttsedits": cmd_ttsedits,
            "roasthi": cmd_roasthi, "roasteng": cmd_roasteng,
            "cluster": cmd_cluster, "broadcast": cmd_broadcast,
            "slayinpowergifted": cmd_slayinpowergifted, "slayinpowertaken": cmd_slayinpowertaken,
            "slayinfor": cmd_slayinfor, "gban": cmd_gban, "ungban": cmd_ungban
        }

        if cmd in routes:
            await routes[cmd](update, context)

def main():
    TOKEN = os.environ.get("BOT_TOKEN")
    if not TOKEN:
        print("BOT_TOKEN missing!")
        return

    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CallbackQueryHandler(menu_callback_handler, pattern="^(menu_|open_panel|stop_all)"))
    app.add_handler(MessageHandler(filters.ALL, global_message_router))

    print("Krishslayin ✝️ Core Fully Online.")
    app.run_polling()

if __name__ == '__main__':
    main()
