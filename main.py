import os
import time
import random
import asyncio
import logging
from gtts import gTTS
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

# Raw Text Line Arrays (No Prefix Line Numbers)
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
    "🚓🚜🚌🚙🚃\n     🚙🌍🌎🌏🌎🚕\n  🇩🇪🇪🇸🌍🚔\n🚘🌏🇷🇺🇬🇧🇮🇹🇪🇸🌏🚘\n🚔🌍🇰🇷🇯🇵🇺🇸🇬🇧🌍🚖\n  🚖🌎🇮🇹🇫🇷🇰🇷🌍🚘\n         "🚖🚨🚒🚒🚒🚑🚑🚒\n"
]

REACTION_EMOJIS = ["❤️", "👍", "🔥", "🥰", "👏", "😁", "🤔", "😱", "🎉", "🤣", "💩", "🌭"]

# Chat Specific Feature States
CHAT_CONFIG = {}

def get_chat_config(chat_id: int):
    if chat_id not in CHAT_CONFIG:
        CHAT_CONFIG[chat_id] = {
            "autoreply": False,
            "react_mode": None,  # Options: None, "admin", "all"
            "target_user_id": None,
            "speed": 1.0,
            "reply_type": "text",
            "bg_task": None
        }
    return CHAT_CONFIG[chat_id]

# Core Message Processor
async def handle_incoming_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.from_user:
        return

    sender = update.message.from_user
    sender_id = sender.id
    chat_id = update.message.chat_id

    # Global Ban Enforcement
    if sender_id in GBANNED_USERS:
        try:
            await update.message.delete()
        except Exception:
            pass
        return

    cfg = get_chat_config(chat_id)

    # Reaction Logic Trigger
    if cfg["react_mode"] is not None:
        should_react = False
        
        if cfg["react_mode"] == "all":
            # React to EVERYONE in the group
            should_react = True
        elif cfg["react_mode"] == "admin":
            # React ONLY to Owner and Authorized Admins
            if sender_id == OWNER_ID or sender_id in AUTHORIZED_ADMINS:
                should_react = True

        if should_react:
            try:
                selected_emoji = random.choice(REACTION_EMOJIS)
                await update.message.set_reaction(reaction=selected_emoji)
            except Exception:
                pass

    # Auto Reply Logic Trigger
    if cfg["autoreply"] and sender_id not in AUTHORIZED_ADMINS:
        random_reply = random.choice(AUTOREPLY_LINES)
        await update.message.reply_text(random_reply)

# Target Spam Engine Task
async def target_spam_worker(chat_id: int, context: ContextTypes.DEFAULT_TYPE):
    while True:
        cfg = get_chat_config(chat_id)
        target_id = cfg.get("target_user_id")
        
        if not target_id:
            break
            
        line = random.choice(TARGET_LINES)
        reply_mode = cfg.get("reply_type", "text")
        
        try:
            if reply_mode == "audio":
                tts = gTTS(text=line, lang='hi')
                filename = f"tts_{chat_id}_{int(time.time())}.mp3"
                tts.save(filename)
                with open(filename, 'rb') as audio:
                    await context.bot.send_audio(chat_id=chat_id, audio=audio)
                if os.path.exists(filename):
                    os.remove(filename)
            else:
                await context.bot.send_message(chat_id=chat_id, text=line)
        except Exception as err:
            logging.error(f"Target execution error: {err}")

        await asyncio.sleep(cfg.get("speed", 1.0))

# Command Handlers
async def command_router(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text:
        return

    sender_id = update.message.from_user.id
    chat_id = update.message.chat_id
    raw_text = update.message.text.strip()
    args = raw_text.split()
    cmd = args[0].lower()

    cfg = get_chat_config(chat_id)

    # 1. +togglereactall (Reacts to EVERY message in the group)
    if cmd == "+togglereactall":
        if sender_id not in AUTHORIZED_ADMINS:
            return
        
        if cfg["react_mode"] == "all":
            cfg["react_mode"] = None
            await update.message.reply_text("❌ **Auto-Reaction for ALL users has been Disabled.**", parse_mode="Markdown")
        else:
            cfg["react_mode"] = "all"
            await update.message.reply_text("✅ **Auto-Reaction for ALL users in this chat has been Enabled!**", parse_mode="Markdown")

    # 2. +togglereact (Reacts ONLY to Owner & Bot Admins)
    elif cmd == "+togglereact":
        if sender_id not in AUTHORIZED_ADMINS:
            return
        
        if cfg["react_mode"] == "admin":
            cfg["react_mode"] = None
            await update.message.reply_text("❌ **Admin Auto-Reaction has been Disabled.**", parse_mode="Markdown")
        else:
            cfg["react_mode"] = "admin"
            await update.message.reply_text("✅ **Auto-Reaction ENABLED for Owner and Bot Admins!**", parse_mode="Markdown")

    # 3. +toggle
    elif cmd == "+toggle":
        if sender_id not in AUTHORIZED_ADMINS:
            return
        cfg["autoreply"] = not cfg["autoreply"]
        status = "Enabled" if cfg["autoreply"] else "Disabled"
        await update.message.reply_text(f"Auto-Reply status: **{status}**", parse_mode="Markdown")

    # 4. +target
    elif cmd == "+target":
        if sender_id not in AUTHORIZED_ADMINS:
            return
        target_user = None
        if update.message.reply_to_message:
            target_user = update.message.reply_to_message.from_user.id
        elif len(args) > 1 and args[1].isdigit():
            target_user = int(args[1])

        if target_user:
            cfg["target_user_id"] = target_user
            if cfg["bg_task"] and not cfg["bg_task"].done():
                cfg["bg_task"].cancel()
            cfg["bg_task"] = asyncio.create_task(target_spam_worker(chat_id, context))
            await update.message.reply_text(f"Targeting initiated for ID: `{target_user}`", parse_mode="Markdown")
        else:
            await update.message.reply_text("Reply to a message or provide User ID to set target.")

    # 5. +untarget
    elif cmd == "+untarget":
        if sender_id not in AUTHORIZED_ADMINS:
            return
        cfg["target_user_id"] = None
        if cfg["bg_task"] and not cfg["bg_task"].done():
            cfg["bg_task"].cancel()
        await update.message.reply_text("Targeting stopped for this chat.")

    # 6. +speed
    elif cmd == "+speed":
        if sender_id not in AUTHORIZED_ADMINS:
            return
        if len(args) > 1:
            try:
                new_speed = float(args[1])
                cfg["speed"] = max(0.1, new_speed)
                await update.message.reply_text(f"Spam delay set to **{cfg['speed']}s**", parse_mode="Markdown")
            except ValueError:
                await update.message.reply_text("Invalid numerical input.")

    # 7. +replytype
    elif cmd == "+replytype":
        if sender_id not in AUTHORIZED_ADMINS:
            return
        if len(args) > 1 and args[1].lower() in ["text", "audio"]:
            cfg["reply_type"] = args[1].lower()
            await update.message.reply_text(f"Reply type set to **{cfg['reply_type']}**", parse_mode="Markdown")

    # 8. +addadmin
    elif cmd == "+addadmin":
        if sender_id != OWNER_ID:
            return
        target = None
        if update.message.reply_to_message:
            target = update.message.reply_to_message.from_user.id
        elif len(args) > 1 and args[1].isdigit():
            target = int(args[1])
        if target:
            AUTHORIZED_ADMINS.add(target)
            await update.message.reply_text(f"User `{target}` granted admin rights.", parse_mode="Markdown")

    # 9. +removeadmin
    elif cmd == "+removeadmin":
        if sender_id != OWNER_ID:
            return
        target = None
        if update.message.reply_to_message:
            target = update.message.reply_to_message.from_user.id
        elif len(args) > 1 and args[1].isdigit():
            target = int(args[1])
        if target and target != OWNER_ID:
            AUTHORIZED_ADMINS.discard(target)
            await update.message.reply_text(f"Admin rights revoked for User `{target}`.", parse_mode="Markdown")

    # 10. +gban
    elif cmd == "+gban":
        if sender_id not in AUTHORIZED_ADMINS:
            return
        target = None
        if update.message.reply_to_message:
            target = update.message.reply_to_message.from_user.id
        elif len(args) > 1 and args[1].isdigit():
            target = int(args[1])
        if target and target != OWNER_ID:
            GBANNED_USERS.add(target)
            await update.message.reply_text(f"User `{target}` added to Global Ban list.", parse_mode="Markdown")

    # 11. +ungban
    elif cmd == "+ungban":
        if sender_id not in AUTHORIZED_ADMINS:
            return
        target = None
        if update.message.reply_to_message:
            target = update.message.reply_to_message.from_user.id
        elif len(args) > 1 and args[1].isdigit():
            target = int(args[1])
        if target:
            GBANNED_USERS.discard(target)
            await update.message.reply_text(f"User `{target}` removed from Global Ban list.", parse_mode="Markdown")

    # 12. +panel
    elif cmd == "+panel":
        if sender_id not in AUTHORIZED_ADMINS:
            return
        keyboard = [
            [InlineKeyboardButton("Toggle AutoReply", callback_data="btn_toggle")],
            [InlineKeyboardButton("React ALL", callback_data="btn_react_all"), InlineKeyboardButton("React Admins Only", callback_data="btn_react_admin")],
            [InlineKeyboardButton("Stop Target", callback_data="btn_untarget")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text("⚙️ **Bot Operations Dashboard**", reply_markup=reply_markup, parse_mode="Markdown")

# Inline Panel Button Callback Processing
async def panel_callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    sender_id = query.from_user.id
    chat_id = query.message.chat_id

    if sender_id not in AUTHORIZED_ADMINS:
        return

    cfg = get_chat_config(chat_id)
    data = query.data

    if data == "btn_toggle":
        cfg["autoreply"] = not cfg["autoreply"]
        await query.edit_message_text(f"AutoReply Status Changed: **{cfg['autoreply']}**", parse_mode="Markdown")
    elif data == "btn_react_all":
        cfg["react_mode"] = "all" if cfg["react_mode"] != "all" else None
        await query.edit_message_text(f"Reaction Mode: **{cfg['react_mode']}**", parse_mode="Markdown")
    elif data == "btn_react_admin":
        cfg["react_mode"] = "admin" if cfg["react_mode"] != "admin" else None
        await query.edit_message_text(f"Reaction Mode: **{cfg['react_mode']}**", parse_mode="Markdown")
    elif data == "btn_untarget":
        cfg["target_user_id"] = None
        if cfg["bg_task"] and not cfg["bg_task"].done():
            cfg["bg_task"].cancel()
        await query.edit_message_text("Targeting operations terminated.")

def main():
    BOT_TOKEN = os.environ.get("BOT_TOKEN", "YOUR_BOT_TOKEN_HERE")
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    # Register Handlers
    app.add_handler(MessageHandler(filters.COMMAND, command_router))
    app.add_handler(CallbackQueryHandler(panel_callback_handler))
    app.add_handler(MessageHandler(filters.ALL & ~filters.COMMAND, handle_incoming_message))

    print("Bot is up and running...")
    app.run_polling()

if __name__ == '__main__':
    main()
