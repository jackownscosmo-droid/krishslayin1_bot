import os
import time
import random
import asyncio
import logging

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder, MessageHandler, 
    CallbackQueryHandler, filters, ContextTypes
)

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

OWNER_ID = int(os.environ.get("OWNER_ID", "8821066459"))
AUTHORIZED_ADMINS = set([8821066459, OWNER_ID])
CHAT_TASKS = {}
BOT_INSTANCES = []

# Aapki di hui exact 15 Lines
VTARGET_CUSTOM_LINES = [
    "Teri ma randi kyu hai 😂😂🔥🔥🔥🔥😂😂",
    "East ➡️ or west ⬅️ teri ma babita is best🥵⚒🔥🥵⚒🔥",
    "𝘿𝙃𝘼𝙏 ʳⁿᵈⁱᵏᵉʸ 🤦🏿‍♂️💢 𝘿𝙃𝘼𝙏 ʳⁿᵈⁱᵏᵉʸ 🤦🏿‍♂️💢𝘿𝙃𝘼𝙏 ʳⁿᵈⁱᵏᵉʸ 🤦🏿‍♂️💢",
    "ᗷᑌᖇ ᗪᗴᗪO Tᑌᕼᗩᖇ ᗰᗩIYᗩ Kᗴ 😂💔🤤🫦👅🤡",
    "𝐓ᴇʀɪ 𝐌ᴀᴀ 𝐂ʜᴜᴅᴋᴇ 𝐁ʜᴀᴀɢ 𝐑ᴀʜɪ -> 🏃🏻‍♀️🔥🤸🏻‍♀️🔥🏃🏻‍♀️🔥🤸🏻‍♀️🔥",
    "🔺पिल्लै Tᴜᴊʜᴇ ᴍᴀʀᴇɴɢᴇ ʏᴀʜɪ ᴅᴇʟʜɪ ᴍᴀʏᴜʀ ᴠɪʜᴀʀ ᴍᴇ ᴊᴀʙ ᴍᴀʀᴇɴɢᴇ ᴅᴇᴋʜ ʟᴇɴᴀ 🔥>💀",
    "Tri maa ke bosde pr jcb se khudai krwa duga rndyke😂😂🤟💥💥🤟",
    "अच्छा teri maa के बूब्स पे green veins h इसलिए tu itna खिलसता h 😂👏🏻",
    "Clap करो रंडीबाले ne joke mara h \n😂👋🏻😂👋🏻😂👋🏻😂👋🏻😂👋🏻😂👋🏻",
    "चलेगी toh teri लंगड़ी maa \n😁🔥😂👋🏻",
    "𝐄ɴᴛʀʏ 𝐋ᴇʟɪ 𝐓ᴏ 𝐀sᴍᴀɴ 𝐊ɪ 𝐔ᴄʜᴀɪᴏ 𝐏ᴇ 𝐓ᴇʀɪ 𝐌ᴀ 𝐂ʜᴜᴅᴇɢɪ / 🌘🕊️",
    "subha ho ya sham chudte rhena hai tera kaam😂🔥😂🔥😂🔥",
    "teri ma ke bhosde سے flight✈take off land teri bhen ke bhosde pe krunga",
    "randy pane me to teri ma aval darje ki hakdaar he😁👍😁👍😁👍😁👍",
    "Le धमाकेदार mukka kha रन्डी ke चाइल्ड 👊🏻👊🏻👊🏻🤣🤣"
]

def get_chat_data(chat_id):
    if chat_id not in CHAT_TASKS:
        CHAT_TASKS[chat_id] = {"tasks": {}}
    return CHAT_TASKS[chat_id]

def is_admin(user_id):
    return user_id in AUTHORIZED_ADMINS or user_id == OWNER_ID

# Target Loop Execution Logic
async def cmd_vtarget(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id): 
        return
    
    text = update.message.text.strip()
    args = text.split()[1:]
    
    if len(args) < 1:
        return await context.bot.send_message(
            chat_id=update.effective_chat.id, 
            text="⚠️ Usage: Reply to message OR pass user: +vtarget @username [@bot_username]"
        )

    # Targeted User Extract logic
    reply_msg = update.message.reply_to_message
    target_user = args[0] if args[0].startswith("@") else None
    
    if not target_user and reply_msg and reply_msg.from_user:
        target_user = f"@{reply_msg.from_user.username}" if reply_msg.from_user.username else reply_msg.from_user.first_name

    if not target_user:
        target_user = args[0]

    # Selected Bot Check logic
    bot_me = await context.bot.get_me()
    current_bot_tag = f"@{bot_me.username.lower()}"
    
    # Text me tag kiye gaye bots dhoondhna
    mentioned_bots = [arg.lower() for arg in args if arg.startswith("@") and "bot" in arg.lower()]
    
    # Agar koi bot mention hai aur ye wala bot usme NAHI hai, toh stop ho jao
    if mentioned_bots and current_bot_tag not in mentioned_bots:
        return

    chat_id = update.effective_chat.id
    chat_data = get_chat_data(chat_id)
    
    if "target" in chat_data["tasks"]: 
        chat_data["tasks"]["target"].cancel()

    # Dynamic Swipe-Reply Loop
    async def vtarget_loop():
        while True:
            random_line = random.choice(VTARGET_CUSTOM_LINES)
            msg_text = f"{target_user} {random_line}"
            
            try:
                # Targeted Message pe swipe/reply apply karna
                reply_to_id = reply_msg.message_id if reply_msg else update.message.message_id
                await context.bot.send_message(
                    chat_id=chat_id, 
                    text=msg_text,
                    reply_to_message_id=reply_to_id
                )
            except Exception:
                pass
            
            await asyncio.sleep(0.3)  # Speed Adjuster

    task = asyncio.create_task(vtarget_loop())
    chat_data["tasks"]["target"] = task

async def cmd_stoptarget(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_data = get_chat_data(update.effective_chat.id)
    if "target" in chat_data["tasks"]:
        chat_data["tasks"]["target"].cancel()
        del chat_data["tasks"]["target"]
        await context.bot.send_message(chat_id=update.effective_chat.id, text="🛑 Targeting Loop Disarmed!")

async def global_router(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text: return
    text = update.message.text.strip()
    
    if text.startswith("+vtarget"):
        await cmd_vtarget(update, context)
    elif text.startswith("+stoptarget") or text.startswith("+stopall"):
        await cmd_stoptarget(update, context)

async def start_bot(token: str):
    app = ApplicationBuilder().token(token).build()
    app.add_handler(MessageHandler(filters.ALL, global_router))
    await app.initialize()
    await app.start()
    BOT_INSTANCES.append(app.bot)
    await app.updater.start_polling()
    await asyncio.Event().wait()

async def main():
    tokens = [v.strip() for k, v in os.environ.items() if k.startswith("BOT_TOKEN") and v.strip()]
    if not tokens: return print("No BOT_TOKEN found.")
    tasks = [asyncio.create_task(start_bot(t)) for t in tokens]
    await asyncio.gather(*tasks)

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        pass
