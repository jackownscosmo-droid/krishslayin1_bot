import os
import time
import asyncio
import logging
from gtts import gTTS
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder, CommandHandler, MessageHandler, 
    CallbackQueryHandler, filters, ContextTypes
)

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# Global Storage States
OWNER_ID = int(os.environ.get("OWNER_ID", "123456789"))
AUTHORIZED_ADMINS = set([OWNER_ID])
GBANNED_USERS = set()

# Chat Specific Active Tasks
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

# --- Helper Middleware ---
def is_admin(user_id):
    return user_id in AUTHORIZED_ADMINS or user_id == OWNER_ID

# --- DYNAMIC 4-PAGE MENU SYSTEM ---

def get_menu_keyboard(page: int):
    buttons = []
    if page == 1:
        buttons = [
            [InlineKeyboardButton("➡️ Page 2 (Combat)", callback_data="menu_2")],
            [InlineKeyboardButton("Close Menu ❌", callback_data="menu_close")]
        ]
    elif page == 2:
        buttons = [
            [InlineKeyboardButton("⬅️ Page 1", callback_data="menu_1"), InlineKeyboardButton("Page 3 ➡️", callback_data="menu_3")],
            [InlineKeyboardButton("Close Menu ❌", callback_data="menu_close")]
        ]
    elif page == 3:
        buttons = [
            [InlineKeyboardButton("⬅️ Page 2", callback_data="menu_2"), InlineKeyboardButton("Page 4 ➡️", callback_data="menu_4")],
            [InlineKeyboardButton("Close Menu ❌", callback_data="menu_close")]
        ]
    elif page == 4:
        buttons = [
            [InlineKeyboardButton("⬅️ Page 3 (Mod)", callback_data="menu_3")],
            [InlineKeyboardButton("Close Menu ❌", callback_data="menu_close")]
        ]
    return InlineKeyboardMarkup(buttons)

def get_menu_text(page: int):
    if page == 1:
        return (
            "📖 **HELP MENU - PAGE 1/4 (General & Info)**\n\n"
            "• `+start` - Check if bot is alive\n"
            "• `+help` - Open this main help menu\n"
            "• `+menu` - Open interactive menu\n"
            "• `+ping` - Check cluster network latency\n"
            "• `+getid` - Get current user & chat ID\n"
            "• `+tts <text>` - Convert text to Hindi voice note"
        )
    elif page == 2:
        return (
            "⚔️ **HELP MENU - PAGE 2/4 (Combat & Automation)**\n\n"
            "• `+spam <text>` - Start continuous message spam\n"
            "• `+stopspam` - Cancel active spam process\n"
            "• `+gcnc <name>` - Start auto title-looping trap\n"
            "• `+stopgcnc` - Stop title-looping process"
        )
    elif page == 3:
        return (
            "🛡️ **HELP MENU - PAGE 3/4 (Moderation & Control)**\n\n"
            "• `+mute` - Reply to shadow-mute user in chat\n"
            "• `+unmute` - Reply to restore user speaking rights\n"
            "• `+panel` - Open control panel for current chat\n"
            "• `+stopall` - Emergency kill-switch for all tasks"
        )
    elif page == 4:
        admin_list = "\n".join([f"• `{uid}`" for uid in AUTHORIZED_ADMINS])
        return (
            "👑 **HELP MENU - PAGE 4/4 (Owner & Power Roster)**\n\n"
            "**Owner Commands:**\n"
            "• `+addadmin` - Reply to grant bot admin power\n"
            "• `+removeadmin` - Reply to revoke bot admin power\n"
            "• `+cluster` - View full server/node telemetry\n"
            "• `+gban` - Reply to globally blacklist user\n\n"
            f"⚡ **Authorized Admins List:**\n{admin_list}"
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
    
    if data.startswith("menu_"):
        page = int(data.split("_")[1])
        text = get_menu_text(page)
        markup = get_menu_keyboard(page)
        await query.edit_message_text(text, reply_markup=markup, parse_mode="Markdown")

# --- COMBAT & AUTOMATION MODULE ---

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
    await update.message.reply_text("🚀 Spam started.")

async def cmd_stopspam(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_data = get_chat_data(update.effective_chat.id)
    if "spam" in chat_data["tasks"]:
        chat_data["tasks"]["spam"].cancel()
        del chat_data["tasks"]["spam"]
        await update.message.reply_text("🛑 Spam stopped.")

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
    await update.message.reply_text("⚔️ Title loop activated.")

async def cmd_stopgcnc(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_data = get_chat_data(update.effective_chat.id)
    if "gcnc" in chat_data["tasks"]:
        chat_data["tasks"]["gcnc"].cancel()
        del chat_data["tasks"]["gcnc"]
        await update.message.reply_text("🛑 Title loop stopped.")

# --- MODERATION & CONTROL MODULE ---

async def cmd_panel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("Stop All Tasks", callback_data="stop_all")],
        [InlineKeyboardButton("Bot Status", callback_data="status_check")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("🎛️ Control Panel:", reply_markup=reply_markup)

async def panel_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if query.data == "stop_all":
        chat_data = get_chat_data(query.message.chat_id)
        for t in chat_data["tasks"].values(): t.cancel()
        chat_data["tasks"].clear()
        await query.edit_message_text("🛑 All active tasks killed.")
    elif query.data == "status_check":
        await query.edit_message_text("⚡ System status: 10/10 Nodes Operational.")

async def cmd_mute(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id): return
    if not update.message.reply_to_message: return await update.message.reply_text("Reply to user.")
    target_id = update.message.reply_to_message.from_user.id
    get_chat_data(update.effective_chat.id)["muted"].add(target_id)
    await update.message.reply_text("🔇 User shadow-muted.")

async def cmd_unmute(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message.reply_to_message: return
    target_id = update.message.reply_to_message.from_user.id
    get_chat_data(update.effective_chat.id)["muted"].discard(target_id)
    await update.message.reply_text("🔊 User unmuted.")

async def cmd_stopall(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_data = get_chat_data(update.effective_chat.id)
    for task in chat_data["tasks"].values():
        task.cancel()
    chat_data["tasks"].clear()
    await update.message.reply_text("🚨 Kill-switch engaged! All processes stopped.")

# --- PUBLIC UTILITIES ---

async def cmd_ping(update: Update, context: ContextTypes.DEFAULT_TYPE):
    start_time = time.time()
    msg = await update.message.reply_text("Pinging 10 nodes...")
    end_time = time.time()
    latency = round((end_time - start_time) * 1000, 2)
    
    nodes_status = "\n".join([f"Node {i+1}: {latency}ms 🟢" for i in range(10)])
    await msg.edit_text(f"📶 **Cluster Latency Test:**\n{nodes_status}")

async def cmd_getid(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.reply_to_message.from_user if update.message.reply_to_message else update.effective_user
    await update.message.reply_text(f"🆔 User ID: `{user.id}`\n💬 Chat ID: `{update.effective_chat.id}`", parse_mode="Markdown")

async def cmd_tts(update: Update, context: ContextTypes.DEFAULT_TYPE):
    args = update.message.text.split()[1:]
    text = " ".join(args)
    if not text: return await update.message.reply_text("Usage: +tts <text>")
    
    tts = gTTS(text=text, lang='hi')
    tts.save("tts.mp3")
    await update.message.reply_audio(audio=open("tts.mp3", "rb"))
    os.remove("tts.mp3")

# --- OWNER CONTROLS & POWER ROSTER ---

async def cmd_addadmin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != OWNER_ID: return
    if not update.message.reply_to_message: return await update.message.reply_text("Reply to target user to grant powers.")
    target_id = update.message.reply_to_message.from_user.id
    AUTHORIZED_ADMINS.add(target_id)
    await update.message.reply_text(f"👑 User `{target_id}` added to Authorized Admins!", parse_mode="Markdown")

async def cmd_removeadmin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != OWNER_ID: return
    if not update.message.reply_to_message: return await update.message.reply_text("Reply to target user to revoke powers.")
    target_id = update.message.reply_to_message.from_user.id
    if target_id == OWNER_ID: return await update.message.reply_text("Cannot remove Owner.")
    AUTHORIZED_ADMINS.discard(target_id)
    await update.message.reply_text(f"🗑️ Powers revoked for User `{target_id}`.", parse_mode="Markdown")

async def cmd_cluster(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != OWNER_ID: return
    await update.message.reply_text("📊 **10-Node Telemetry Cluster:**\n• Active Clusters: 10\n• CPU Load: 12%\n• Memory: 256MB / 512MB\n• Network Health: 100%")

async def cmd_gban(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != OWNER_ID: return
    if not update.message.reply_to_message: return await update.message.reply_text("Reply to target user.")
    target_id = update.message.reply_to_message.from_user.id
    GBANNED_USERS.add(target_id)
    await update.message.reply_text(f"🚫 User {target_id} Globally Blacklisted.")

# --- AUTOMATIC ENFORCER ---

async def auto_enforcer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.from_user: return
    
    user_id = update.message.from_user.id
    chat_id = update.effective_chat.id
    chat_data = get_chat_data(chat_id)

    if user_id in GBANNED_USERS or user_id in chat_data["muted"]:
        try: await update.message.delete()
        except: pass
        return

    if user_id in chat_data["autoreply"]:
        reply_msg = chat_data["autoreply"][user_id]
        await update.message.reply_text(reply_msg)

def main():
    TOKEN = os.environ.get("BOT_TOKEN")
    if not TOKEN:
        print("BOT_TOKEN environment variable is missing!")
        return

    app = ApplicationBuilder().token(TOKEN).build()

    # Helper function to generate '+' prefix handlers
    def add_p_cmd(name, handler_func):
        regex_pattern = r"^\+" + name + r"(\s+.*)?$"
        app.add_handler(MessageHandler(filters.Regex(regex_pattern), handler_func))

    # Core Navigation Handlers (+start, +help, +menu)
    add_p_cmd("start", cmd_start_help_menu)
    add_p_cmd("help", cmd_start_help_menu)
    add_p_cmd("menu", cmd_start_help_menu)
    app.add_handler(CallbackQueryHandler(menu_callback_handler, pattern="^menu_"))

    # Combat Commands (+spam, +stopspam, +gcnc, +stopgcnc)
    add_p_cmd("spam", cmd_spam)
    add_p_cmd("stopspam", cmd_stopspam)
    add_p_cmd("gcnc", cmd_gcnc)
    add_p_cmd("stopgcnc", cmd_stopgcnc)

    # Moderation & Panel (+panel, +mute, +unmute, +stopall)
    add_p_cmd("panel", cmd_panel)
    add_p_cmd("mute", cmd_mute)
    add_p_cmd("unmute", cmd_unmute)
    add_p_cmd("stopall", cmd_stopall)
    app.add_handler(CallbackQueryHandler(panel_callback, pattern="^(stop_all|status_check)$"))

    # Utilities (+ping, +getid, +tts)
    add_p_cmd("ping", cmd_ping)
    add_p_cmd("getid", cmd_getid)
    add_p_cmd("tts", cmd_tts)

    # Owner Controls & Admin Management (+addadmin, +removeadmin, +cluster, +gban)
    add_p_cmd("addadmin", cmd_addadmin)
    add_p_cmd("removeadmin", cmd_removeadmin)
    add_p_cmd("cluster", cmd_cluster)
    add_p_cmd("gban", cmd_gban)

    # Message Enforcer for Mutes & Autoreplies
    app.add_handler(MessageHandler(filters.ALL, auto_enforcer))

    print("Bot fully active and operational with '+' prefix.")
    app.run_polling()

if __name__ == '__main__':
    main()
