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
    "Tere dimaag me memory card lagane ki jagah hai, par software hi missing hai!"
]

ROASTS_ENG = [
    "You bring everyone so much joy... when you leave the room!",
    "I'd agree with you, but then we'd both be wrong.",
    "Your secrets are always safe with me. I never even listen when you tell me.",
    "You have an entire room to yourself inside your own head.",
    "I'm not saying I hate you, but if you were on fire, I'd consider getting marshmallows."
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
            "• `+stopflood` — Stop mention flood"
        )
    elif page == 3:
        return (
            "⛓️ **TRAPS & TARGETING** 🎯\n"
            "────────────────────────────\n"
            "• `+mute <user>` — Shadow-mute target\n"
            "• `+unmute <user>` — Unmute target\n"
            "• `+autoreply <user>` — Auto-reply trap\n"
            "• `+togglereact` — Toggle Real 🤣 Reaction (Owner/Admins)\n"
            "• `+stopall` — Master Kill Switch"
        )
    elif page == 4:
        return (
            "🛠️ **BLACKOUT & TOOLS**\n"
            "────────────────────────────\n"
            "• `+scan` — Deep Group matrix scanner\n"
            "• `+ping` — Inspect latency\n"
            "• `+getid` — Fetch numeric ID\n"
            "• `+tts <text>` — Voice synthesis\n"
            "• `+roasthi <user>` — Hindi roast"
        )
    elif page == 5:
        admin_list = "\n".join([f"• `{uid}`" for uid in AUTHORIZED_ADMINS])
        return (
            "👑 **OWNER CONTROLS**\n"
            "────────────────────────────\n"
            "• `+broadcast <text>` — Network broadcast\n"
            "• `+gban <user>` — Global blacklist\n\n"
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
        return await query.edit_message_text("🚨 MASTER KILL SWITCH ACTIVATED!", reply_markup=get_menu_keyboard(1))
    elif data.startswith("menu_"):
        page = int(data.split("_")[1])
        await query.edit_message_text(get_menu_text(page), reply_markup=get_menu_keyboard(page), parse_mode="Markdown")

# --- Commands ---

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
            try: await context.bot.set_chat_title(chat_id=update.effective_chat.id, title=titles[idx % len(titles)])
            except Exception: pass
            idx += 1
            await asyncio.sleep(0.5)
            
    task = asyncio.create_task(gcnc_loop())
    chat_data["tasks"]["gcnc"] = task
    await update.message.reply_text("⚔️ High-speed title loop activated.")

async def cmd_stopgcnc(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_data = get_chat_data(update.effective_chat.id)
    if "gcnc" in chat_data["tasks"]:
        chat_data["tasks"]["gcnc"].cancel()
        del chat_data["tasks"]["gcnc"]
        await update.message.reply_text("🛑 Title loop disarmed.")

async def cmd_target(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id): return
    args = update.message.text.split()[1:]
    user = args[0] if args else "@target"
    chat_data = get_chat_data(update.effective_chat.id)
    if "target" in chat_data["tasks"]: chat_data["tasks"]["target"].cancel()

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

async def cmd_stoptarget(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_data = get_chat_data(update.effective_chat.id)
    if "target" in chat_data["tasks"]:
        chat_data["tasks"]["target"].cancel()
        del chat_data["tasks"]["target"]
        await update.message.reply_text("🛑 Targeting disarmed.")

async def cmd_spam(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id): return
    text = " ".join(update.message.text.split()[1:])
    if not text: return await update.message.reply_text("Usage: `+spam <text>`", parse_mode="Markdown")
    chat_data = get_chat_data(update.effective_chat.id)
    if "spam" in chat_data["tasks"]: chat_data["tasks"]["spam"].cancel()

    async def spam_loop():
        while True:
            try: await context.bot.send_message(chat_id=update.effective_chat.id, text=text)
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
        await update.message.reply_text("🛑 Spam stopped.")

async def cmd_togglereact(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id): return
    chat_data = get_chat_data(update.effective_chat.id)
    chat_data["togglereact"] = not chat_data["togglereact"]
    state = "ENABLED 🟢" if chat_data["togglereact"] else "DISABLED 🔴"
    await update.message.reply_text(f"🎭 **Auto-Reaction (🤣) [Owner/Admins Only]:** `{state}`", parse_mode="Markdown")

async def cmd_stopall(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id): return
    chat_data = get_chat_data(update.effective_chat.id)
    for task in list(chat_data["tasks"].values()): task.cancel()
    chat_data["tasks"].clear()
    chat_data["togglereact"] = False
    await update.message.reply_text("🚨 MASTER KILL SWITCH EXECUTED!")

async def cmd_ping(update: Update, context: ContextTypes.DEFAULT_TYPE):
    start = time.time()
    msg = await update.message.reply_text("📡 Pinging...")
    latency = round((time.time() - start) * 1000, 2)
    await msg.edit_text(f"📶 Latency: `{latency}ms`", parse_mode="Markdown")

async def cmd_getid(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    chat = update.effective_chat
    reply = update.message.reply_to_message
    text = f"👤 **Your ID:** `{user.id}`\n💬 **Chat ID:** `{chat.id}`"
    if reply and reply.from_user:
        text += f"\n🎯 **Replied User ID:** `{reply.from_user.id}`"
    await update.message.reply_text(text, parse_mode="Markdown")

async def cmd_roasthi(update: Update, context: ContextTypes.DEFAULT_TYPE):
    target_name = " ".join(update.message.text.split()[1:])
    roast_text = random.choice(ROASTS_HI)
    await update.message.reply_text(f"🔥 {target_name} {roast_text}" if target_name else f"🔥 {roast_text}")

# --- Global Message & Auto-Reaction Router ---

async def global_message_router(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.from_user: return
    user_id = update.message.from_user.id
    chat_id = update.effective_chat.id
    chat_data = get_chat_data(chat_id)
    text = update.message.text.strip() if update.message.text else ""

    # Don't react to bot's own messages or commands
    if not update.message.from_user.is_bot and not text.startswith("+"):
        # Real Telegram Emoji Reaction (Only for Owner & Authorized Admins)
        if chat_data.get("togglereact", False) and is_admin(user_id):
            try:
                await context.bot.set_message_reaction(
                    chat_id=chat_id,
                    message_id=update.message.message_id,
                    reaction=[ReactionTypeEmoji(emoji='🤣')]
                )
            except Exception as e:
                logging.error(f"Error setting reaction: {e}")

    # 2. Command Execution Router
    if text.startswith("+"):
        cmd = text.split()[0][1:].lower()
        routes = {
            "start": lambda u, c: u.message.reply_text(get_menu_text(1), reply_markup=get_menu_keyboard(1), parse_mode="Markdown"),
            "menu": lambda u, c: u.message.reply_text(get_menu_text(1), reply_markup=get_menu_keyboard(1), parse_mode="Markdown"),
            "gcnc": cmd_gcnc, "stopgcnc": cmd_stopgcnc,
            "target": cmd_target, "stoptarget": cmd_stoptarget,
            "spam": cmd_spam, "stopspam": cmd_stopspam,
            "togglereact": cmd_togglereact, "stopall": cmd_stopall,
            "ping": cmd_ping, "getid": cmd_getid, "roasthi": cmd_roasthi
        }
        if cmd in routes:
            await routes[cmd](update, context)

def main():
    TOKEN = os.environ.get("BOT_TOKEN")
    if not TOKEN:
        print("BOT_TOKEN missing!")
        return

    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CallbackQueryHandler(menu_callback_handler))
    app.add_handler(MessageHandler(filters.ALL, global_message_router))

    print("Krishslayin ✝️ Core Online.")
    app.run_polling()

if __name__ == '__main__':
    main()
