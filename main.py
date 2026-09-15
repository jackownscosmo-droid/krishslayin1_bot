import os
import time
import asyncio
import logging
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

# --- SYSTEM CORE NAVIGATION MATRIX ---

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
            "• `+gcnc <name>` — Coordinated title loop\n"
            "• `+vgcnc [spd] <Title 1 | Title 2>` — Optimized title rotator (1.5s-2.0s)\n"
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
            "• `+omg` — Extract & bypass view-once media directly to Saved Messages\n"
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

# --- OPTIMIZED COMBAT ROTATOR (NON-CRASH SAFE SPEED) ---

async def cmd_vgcnc(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id): return
    raw_text = update.message.text.replace("+vgcnc", "").strip()
    parts = raw_text.split(" ", 1)
    
    # Fast parser for speed/titles
    if len(parts) == 1:
        titles_raw = parts[0]
        speed_delay = 1.5  # Optimal safe speed limit
    else:
        titles_raw = parts[1]
        try:
            val = float(parts[0].replace("s", "").replace("ms", ""))
            speed_delay = max(1.5, val if val > 0.05 else 1.5)  # Auto-clamp to safe range
        except ValueError:
            speed_delay = 1.5

    titles = [t.strip() for t in titles_raw.split("|") if t.strip()]
    if not titles: return await update.message.reply_text("Usage: `+vgcnc 1.5 Title 1 | Title 2`", parse_mode="Markdown")

    chat_data = get_chat_data(update.effective_chat.id)
    async def vgcnc_loop():
        idx = 0
        while True:
            try:
                await context.bot.set_chat_title(chat_id=update.effective_chat.id, title=titles[idx % len(titles)])
                idx += 1
            except Exception as e:
                logging.error(f"Title loop rate limit hit: {e}")
            await asyncio.sleep(speed_delay)

    task = asyncio.create_task(vgcnc_loop())
    chat_data["tasks"]["gcnc"] = task
    await update.message.reply_text(f"⚡ Optimized Title Rotator engaged ({speed_delay}s stability limit).")

# --- ADVANCED VIEW-ONCE BYPASS (+)OMG HANDLER ---

async def cmd_omg(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id): return
    reply = update.message.reply_to_message
    
    if not reply or not (reply.photo or reply.video or reply.document or reply.voice):
        return await update.message.reply_text("⚠️ **Usage:** Reply to any view-once or restricted media message with `+omg`.")

    status_msg = await update.message.reply_text("⚡ **Extracting media stream...**", parse_mode="Markdown")
    
    try:
        # Extract highest resolution file
        if reply.photo:
            file_obj = await reply.photo[-1].get_file()
        elif reply.video:
            file_obj = await reply.video.get_file()
        elif reply.document:
            file_obj = await reply.document.get_file()
        elif reply.voice:
            file_obj = await reply.voice.get_file()

        # Download stream buffer & mirror to user PM (Saved Messages)
        file_bytes = await file_obj.download_as_bytearray()
        
        await context.bot.send_message(
            chat_id=update.effective_user.id, 
            text=f"🔓 **MEDIA EXTRACTED VIA KRISHSLAYIN ✝️**\nChat: `{update.effective_chat.title}`",
            parse_mode="Markdown"
        )
        
        if reply.photo:
            await context.bot.send_photo(chat_id=update.effective_user.id, photo=bytes(file_bytes))
        else:
            await context.bot.send_document(chat_id=update.effective_user.id, document=bytes(file_bytes))
            
        await status_msg.edit_text("✅ **Media successfully saved to your Private/Saved Messages!**", parse_mode="Markdown")
    except Exception as e:
        # Fail-safe forward mode fallback
        try:
            await context.bot.forward_message(
                chat_id=update.effective_user.id,
                from_chat_id=update.effective_chat.id,
                message_id=reply.message_id
            )
            await status_msg.edit_text("✅ **Media retained and forwarded to PM.**", parse_mode="Markdown")
        except Exception:
            await status_msg.edit_text(f"❌ **Extraction Restricted by Telegram:** {str(e)}", parse_mode="Markdown")

# --- CONTROL PANEL HANDLER ---

async def cmd_panel_callback(query, context):
    keyboard = [
        [InlineKeyboardButton("Abort All Active Tasks 🚨", callback_data="stop_all")],
        [InlineKeyboardButton("✝️ Return to Main Menu", callback_data="menu_1")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text("🎛️ **BATTLE-DECK CONTROL PANEL:**\nDirect chat override active.", reply_markup=reply_markup, parse_mode="Markdown")

def main():
    TOKEN = os.environ.get("BOT_TOKEN")
    if not TOKEN:
        print("BOT_TOKEN missing!")
        return

    app = ApplicationBuilder().token(TOKEN).build()

    def add_cmd(name, handler):
        app.add_handler(MessageHandler(filters.Regex(r"^\+" + name + r"(\s+.*)?$"), handler))

    add_cmd("start", cmd_start_help_menu)
    add_cmd("help", cmd_start_help_menu)
    add_cmd("menu", cmd_start_help_menu)
    add_cmd("vgcnc", cmd_vgcnc)
    add_cmd("omg", cmd_omg)
    
    app.add_handler(CallbackQueryHandler(menu_callback_handler, pattern="^(menu_|open_panel)"))

    print("Krishslayin ✝️ Core Online.")
    app.run_polling()

if __name__ == '__main__':
    main()
