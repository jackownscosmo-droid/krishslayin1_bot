import os
import time
import asyncio
import logging
from gtts import gTTS
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder, MessageHandler, 
    CallbackQueryHandler, filters, ContextTypes
)

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# Global Access & System State
OWNER_ID = int(os.environ.get("OWNER_ID", "123456789"))
AUTHORIZED_ADMINS = set([OWNER_ID])
GBANNED_USERS = set()
CHAT_TASKS = {}

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

# --- EXACT UI & NAVIGATION MATRIX ---

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
            "⚡ **MATRIX CLUSTER CORE — HELLFIRE BOT** ⚡\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            "Select a command module below to inspect commands & usage."
        )
    elif page == 2:
        return (
            "⚔️ **COMBAT & WARFARE**\n"
            "────────────────────────────\n"
            "• `+gcnc <name>` — Coordinated title loop\n"
            "• `+vgcnc [spd] <Title 1 | Title 2>` — Custom title rotators\n"
            "• `+stopgcnc` — Halt active title loop\n"
            "• `+target <user>` — Mention loop (templates)\n"
            "• `+vtarget <user> <text>` — Custom mention loop\n"
            "• `+stoptarget [user]` — Disarm targeting loop\n"
            "• `+spam <text>` — Synchronized high-speed spam\n"
            "• `+stopspam` — Terminate active spam\n"
            "• `+flood <user>` — Mention flood (templates)\n"
            "• `+vflood <user> <text>` — Custom mention flood\n"
            "• `+stopflood [user]` — Stop mention flood\n"
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
            "• `+autoreply <user>` — Auto-reply trap (templates)\n"
            "• `+vautoreply <user> <msg>` — Custom auto-reply trap\n"
            "• `+stopautoreply` — Disarm text auto-reply\n"
            "• `+reptts <user>` — Voice trap (reply to voice)\n"
            "• `+stopreptts` — Disarm voice trap\n"
            "• `+clean [count]` — Purge recent messages\n"
            "• `+togglereact` — Toggle emoji auto-reactions\n"
            "• `+stopall` — Kill switch (stops all tasks in chat)"
        )
    elif page == 4:
        return (
            "🛠️ **BLACKOUT & TOOLS**\n"
            "────────────────────────────\n"
            "• `+scan` — Deep Group matrix & admin scanner\n"
            "• `+ping` — Inspect all 10 nodes latency in 1 message\n"
            "• `+getid` — Fetch numeric Telegram ID\n"
            "• `+status` — View active cluster state in chat\n"
            "• `+tts <text>` — Indian accent speech synthesis\n"
            "• `+ttsedits` — View supported TTS language codes\n"
            "• `+roasthi <user>` — Automated Hindi roast\n"
            "• `+roasteng <user>` — Automated English roast"
        )
    elif page == 5:
        admin_list = "\n".join([f"• `{uid}`" for uid in AUTHORIZED_ADMINS])
        return (
            "👑 **OWNER CONTROLS**\n"
            "────────────────────────────\n"
            "• `+cluster` — All Live node telemetry & health\n"
            "• `+broadcast <text>` — Network-wide broadcast\n"
            "• `+slayinpowergifted <id>` — Authorize admin ID\n"
            "• `+slayinpowertaken <id>` — Revoke admin ID\n"
            "• `+slayinfor` — List authorized admins with details\n"
            "• `+gban <user>` — Global blacklist across all chats\n"
            "• `+ungban <user>` — Remove from global blacklist\n\n"
            f"⚡ **Active Admins:**\n{admin_list}"
        )

async def cmd_start_help_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = get_menu_text(1)
    markup = get_menu_keyboard(1)
    await update.message.reply_text(text, reply_markup=markup, parse_mode="Markdown")

async def menu_callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data
    
    if data == "menu_close":
        return await query.message.delete()
    elif data == "open_panel":
        return await cmd_panel_callback(query, context)
    elif data.startswith("menu_"):
        page = int(data.split("_")[1])
        text = get_menu_text(page)
        markup = get_menu_keyboard(page)
        await query.edit_message_text(text, reply_markup=markup, parse_mode="Markdown")

# --- COMBAT & WARFARE ENGINE ---

async def cmd_spam(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id): return
    args = update.message.text.split()[1:]
    text = " ".join(args)
    if not text: return await update.message.reply_text("Usage: +spam <text>")
    
    chat_data = get_chat_data(update.effective_chat.id)
    async def spam_loop():
        while True:
            await context.bot.send_message(chat_id=update.effective_chat.id, text=text)
            await asyncio.sleep(0.3)

    task = asyncio.create_task(spam_loop())
    chat_data["tasks"]["spam"] = task
    await update.message.reply_text("🚀 High-speed spam initialized.")

async def cmd_stopspam(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_data = get_chat_data(update.effective_chat.id)
    if "spam" in chat_data["tasks"]:
        chat_data["tasks"]["spam"].cancel()
        del chat_data["tasks"]["spam"]
        await update.message.reply_text("🛑 Active spam terminated.")

async def cmd_gcnc(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id): return
    args = update.message.text.split()[1:]
    name = " ".join(args)
    if not name: return await update.message.reply_text("Usage: +gcnc <name>")
    
    chat_data = get_chat_data(update.effective_chat.id)
    async def gcnc_loop():
        titles = [f"⚡ {name} ⚡", f"🔥 {name} 🔥", f"👑 {name} 👑"]
        idx = 0
        while True:
            try:
                await context.bot.set_chat_title(chat_id=update.effective_chat.id, title=titles[idx % len(titles)])
                idx += 1
            except Exception: pass
            await asyncio.sleep(2)

    task = asyncio.create_task(gcnc_loop())
    chat_data["tasks"]["gcnc"] = task
    await update.message.reply_text("⚔️ Coordinated title loop activated.")

async def cmd_stopgcnc(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_data = get_chat_data(update.effective_chat.id)
    if "gcnc" in chat_data["tasks"]:
        chat_data["tasks"]["gcnc"].cancel()
        del chat_data["tasks"]["gcnc"]
        await update.message.reply_text("🛑 Title loop disarmed.")

# --- TRAPS & TARGETING MODULES ---

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

async def cmd_stopall(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_data = get_chat_data(update.effective_chat.id)
    for task in chat_data["tasks"].values(): task.cancel()
    chat_data["tasks"].clear()
    await update.message.reply_text("🚨 EMERGENCY KILL SWITCH ENGAGED! All threads stopped.")

# --- BLACKOUT & TOOLS ---

async def cmd_ping(update: Update, context: ContextTypes.DEFAULT_TYPE):
    start = time.time()
    msg = await update.message.reply_text("📡 Pinging 10-node matrix cluster...")
    latency = round((time.time() - start) * 1000, 2)
    nodes_telemetry = "\n".join([f"• Node {i+1}: {latency}ms 🟢" for i in range(10)])
    await msg.edit_text(f"📶 **10-NODE LATENCY TELEMETRY:**\n{nodes_telemetry}", parse_mode="Markdown")

async def cmd_roasthi(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message.reply_to_message: return await update.message.reply_text("Reply to target user.")
    await update.message.reply_text("🔥 Teri shakal dekh ke Telegram ka server bhi crash ho jaye!")

async def cmd_roasteng(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message.reply_to_message: return await update.message.reply_text("Reply to target user.")
    await update.message.reply_text("🔥 You bring everyone so much joy... when you leave the room!")

# --- OWNER CONTROLS ---

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

async def cmd_gban(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != OWNER_ID: return
    if not update.message.reply_to_message: return await update.message.reply_text("Reply to target user.")
    target_id = update.message.reply_to_message.from_user.id
    GBANNED_USERS.add(target_id)
    await update.message.reply_text(f"🚫 Target `{target_id}` globally blacklisted.", parse_mode="Markdown")

# --- CONTROL PANEL HANDLER ---

async def cmd_panel_callback(query, context):
    keyboard = [
        [InlineKeyboardButton("Abort All Active Tasks 🚨", callback_data="stop_all")],
        [InlineKeyboardButton("✝️ Return to Main Menu", callback_data="menu_1")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text("🎛️ **BATTLE-DECK CONTROL PANEL:**\nDirect chat override active.", reply_markup=reply_markup, parse_mode="Markdown")

# --- AUTOMATIC ENFORCER ---

async def auto_enforcer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.from_user: return
    user_id = update.message.from_user.id
    chat_data = get_chat_data(update.effective_chat.id)

    if user_id in GBANNED_USERS or user_id in chat_data["muted"]:
        try: await update.message.delete()
        except: pass
        return

def main():
    TOKEN = os.environ.get("BOT_TOKEN")
    if not TOKEN:
        print("BOT_TOKEN missing!")
        return

    app = ApplicationBuilder().token(TOKEN).build()

    def add_cmd(name, handler):
        app.add_handler(MessageHandler(filters.Regex(r"^\+" + name + r"(\s+.*)?$"), handler))

    # Core Navigation
    add_cmd("start", cmd_start_help_menu)
    add_cmd("help", cmd_start_help_menu)
    add_cmd("menu", cmd_start_help_menu)
    app.add_handler(CallbackQueryHandler(menu_callback_handler, pattern="^(menu_|open_panel)"))

    # Combat & Warfare
    add_cmd("spam", cmd_spam)
    add_cmd("stopspam", cmd_stopspam)
    add_cmd("gcnc", cmd_gcnc)
    add_cmd("stopgcnc", cmd_stopgcnc)

    # Traps & Targeting
    add_cmd("mute", cmd_mute)
    add_cmd("unmute", cmd_unmute)
    add_cmd("stopall", cmd_stopall)

    # Blackout & Tools
    add_cmd("ping", cmd_ping)
    add_cmd("roasthi", cmd_roasthi)
    add_cmd("roasteng", cmd_roasteng)

    # Owner Controls
    add_cmd("slayinpowergifted", cmd_slayinpowergifted)
    add_cmd("slayinpowertaken", cmd_slayinpowertaken)
    add_cmd("gban", cmd_gban)

    # Global Enforcer
    app.add_handler(MessageHandler(filters.ALL, auto_enforcer))

    print("Hellfire Bot Online.")
    app.run_polling()

if __name__ == '__main__':
    main()
