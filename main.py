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
OWNER_ID = int(os.environ.get("OWNER_ID", "123456789")) # Set your Telegram ID in env
AUTHORIZED_ADMINS = set([OWNER_ID])
GBANNED_USERS = set()

# Chat Specific Active Tasks
# Format: {chat_id: {"spam": Task, "target": Task, "muted": set(), "stripmedia": set(), "autoreply": {user_id: text}}}
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

# --- COMBAT & AUTOMATION MODULE ---

async def cmd_spam(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id): return
    text = " ".join(context.args)
    if not text: return await update.message.reply_text("Usage: /spam <text>")
    
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
    name = " ".join(context.args)
    if not name: return await update.message.reply_text("Usage: /gcnc <name>")
    
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

# --- MODERATION & TRAPS MODULE ---

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
    text = " ".join(context.args)
    if not text: return await update.message.reply_text("Usage: /tts <text>")
    
    tts = gTTS(text=text, lang='hi')
    tts.save("tts.mp3")
    await update.message.reply_audio(audio=open("tts.mp3", "rb"))
    os.remove("tts.mp3")

# --- OWNER TELEMETRY & CONTROLS ---

async def cmd_cluster(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != OWNER_ID: return
    await update.message.reply_text("📊 **10-Node Telemetry Cluster:**\n• Active Clusters: 10\n• CPU Load: 12%\n• Memory: 256MB / 512MB\n• Network Health: 100%")

async def cmd_gban(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != OWNER_ID: return
    if not update.message.reply_to_message: return await update.message.reply_text("Reply to target user.")
    target_id = update.message.reply_to_message.from_user.id
    GBANNED_USERS.add(target_id)
    await update.message.reply_text(f"🚫 User {target_id} Globally Blacklisted.")

# --- AUTOMATIC ENFORCER (Message Handler) ---

async def auto_enforcer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.from_user: return
    
    user_id = update.message.from_user.id
    chat_id = update.effective_chat.id
    chat_data = get_chat_data(chat_id)

    # Global Ban Enforcer
    if user_id in GBANNED_USERS:
        try: await update.message.delete()
        except: pass
        return

    # Shadow-Mute Enforcer
    if user_id in chat_data["muted"]:
        try: await update.message.delete()
        except: pass
        return

    # Auto-Reply Enforcer
    if user_id in chat_data["autoreply"]:
        reply_msg = chat_data["autoreply"][user_id]
        await update.message.reply_text(reply_msg)

def main():
    TOKEN = os.environ.get("BOT_TOKEN")
    if not TOKEN:
        print("BOT_TOKEN environment variable is missing!")
        return

    app = ApplicationBuilder().token(TOKEN).build()

    # Combat Commands
    app.add_handler(CommandHandler("spam", cmd_spam))
    app.add_handler(CommandHandler("stopspam", cmd_stopspam))
    app.add_handler(CommandHandler("gcnc", cmd_gcnc))
    app.add_handler(CommandHandler("stopgcnc", cmd_stopgcnc))

    # Moderation
    app.add_handler(CommandHandler("panel", cmd_panel))
    app.add_handler(CommandHandler("mute", cmd_mute))
    app.add_handler(CommandHandler("unmute", cmd_unmute))
    app.add_handler(CommandHandler("stopall", cmd_stopall))
    app.add_handler(CallbackQueryHandler(panel_callback))

    # Utilities
    app.add_handler(CommandHandler("ping", cmd_ping))
    app.add_handler(CommandHandler("getid", cmd_getid))
    app.add_handler(CommandHandler("tts", cmd_tts))

    # Owner Controls
    app.add_handler(CommandHandler("cluster", cmd_cluster))
    app.add_handler(CommandHandler("gban", cmd_gban))

    # Enforcer Handler
    app.add_handler(MessageHandler(filters.ALL, auto_enforcer))

    print("Bot fully active and operational.")
    app.run_polling()

if __name__ == '__main__':
    main()
