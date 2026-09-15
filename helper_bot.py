import os
import time
import random
import asyncio
import logging

try:
    from gtts import gTTS
except ImportError:
    gTTS = None

from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# Global Configuration
OWNER_ID = int(os.environ.get("OWNER_ID", "123456789"))
AUTHORIZED_ADMINS = set([OWNER_ID])
GBANNED_USERS = set()
CHAT_TASKS = {}
REACTION_EMOJI = "🤣"

# Raw Text Line Arrays
AUTOREPLY_LINES = [
    r"""बड़े दुःख के साथ हँसना पढ़ रहा है😂  𝐓ᴜ तेरी माँ रंडी 🤍😅🔥""",
    r"""𝙏𝙚𝙧𝙞 𝙢𝙖𝙖 𝙠𝙚 𝙗𝙝𝙤𝙨𝙙𝙚 𝙢𝙚 𝙡𝙖𝙩 𝙥𝙙𝙚𝙣𝙜𝙚 𝙗𝙝𝙤𝙩 𝙩𝙚𝙯 👻 😂👯😂👯😂👯 😂👯😂👯😂👯 😂👯😂👯😂👯""",
    r"""𝙏𝙀𝙍𝙄 𝙈𝘼 𝑑𝙄𝘿🇭🇻𝘼 𝙋𝙀𝙉𝙎𝙄𝙊𝙉 𝙆𝙃𝘼𝙉𝙀 𝙒𝘼𝙇𝙄 𝙍𝙉𝘿𝙄 🤣""",
    r"""तेरी maa की chut में ऐसा HACK lgaunga 
Light की speed में बच्चे देगी""",
    r"""𝑩𝑯𝑨𝑮 𝑹𝑨𝑵𝑫𝒀𝑲𝑬 𝑻𝑬𝑹𝑰 𝑴𝑨 𝑪𝑯𝑼𝑫𝑹𝑰 𝑯𝑨𝑰 ᯓ🏃🏻‍♀️‍➡️ᯓ🏃🏻‍♀️‍➡️ᯓ🏃🏻‍♀️‍➡️ᯓ🏃🏻‍♀️‍➡️ᯓ🏃🏻‍♀️‍➡️ᯓ🏃🏻‍♀️‍➡️ᯓ🏃🏻‍♀️‍➡️ᯓ🏃🏻‍♀️‍➡️ᯓ🏃🏻‍♀️‍➡️ᯓ🏃🏻‍♀️‍➡️ᯓ🏃🏻‍♀️‍➡️""",
    r"""𝘽𝙃𝘼𝙂𝘼 𝘽𝙃𝘼𝙂𝘼 𝙆𝙀 𝙈𝘼𝙍𝙐𝙉𝙂𝘼 🤣🩷🙌🏾""",
    r"""𝐆ʀᴇᴇਬ𝐢 और दर्दनाक 𝐂ʜᴜᴅᴀ𝐢 
तो तेरी मां ने देखी है 👀😝🤣"""
]

TARGET_LINES = [
    r"""˚∧＿∧   +        — ͟͞͞🥛
(  •‿• )つ  — ͟͞͞ 🥛         — ͟͞͞🥛 +
(つ  <                — ͟͞͞🥛
｜_つ      +  — ͟͞͞🥛         — ͟͞͞🥛 ˚
`し´Special attack: teri  mummy ka dudh 😂😂 kilas randi ke""",
    r"""𝙉𝙀𝙆𝘼𝘼𝘼𝙇 𝙈𝘼𝘿𝘼𝘼𝙍𝘾𝙃𝘿👍🏼👍🏼👍🏼👍🏼👍🏼""",
    r"""🚓🚜🚌🚙🚃
     🚙🌍🌎🌏🌎🚕
  🇩🇪🇪🇸🌍🚔
🚘🌏🇷🇺🇬🇧🇮🇹🇪🇸🌏🚘
🚔🌍🇰🇷🇯🇵🇺🇸🇬🇧🌍🚖
  🚖🌎🇮🇹🇫🇷🇰🇷🌍🚘
     🚍🌏🌍🌎🌏🚔""",
    r"""तेरी बहन का भोसड़ा 😂🤸🏻‍♂️😂🤸🏻‍♂️😂🤸🏻‍♂️😂𝘾𝙃𝙐𝙋 𝙍𝙉𝘿𝙄𝙆𝙀""",
    r"""ᴍᴀᴀғɪ ᴍᴀɴɢʟᴇ ᴋʏᴀ ᴘᴀᴛᴀ ʙᴀᴅʙᴏʏ ᴍᴀᴀғ ᴋʀᴅ ᴛᴜᴊᴇ"""
]

FLOOD_LINES = [
    r"""𝙏𝙚𝙧𝙞 𝙢𝙖𝙖 𝙠𝙚 𝙗𝙝𝙤𝙨𝙙𝙚 𝙢𝙚 𝙡𝙖𝙩 𝙥𝙙𝙚𝙣𝙜𝙚 𝙗𝙝𝙤𝙩 𝙩𝙚𝙯 👻 😂👯😂👯😂👯 😂👯😂👯😂👯 😂👯😂👯😂👯""",
    r"""⋆͙̈ ° ♪ °••° ⋆⋆͙̈ ° ♪ °••° ⋆⋆͙̈ ° ♪ °••° ⋆⋆͙̈ ° ♪ °••° ⋆⋆͙̈ ° ♪ °••° ⋆⋆͙̈ ° ♪ °••° ⋆⋆͙̈ ° ♪ °••° ⋆⋆͙̈ ° ♪ °••° ⋆⋆͙̈ ° ♪ °••° ⋆⋆͙̈ ° ♪ °••° ⋆⋆͙̈ ° ♪ °••° ⋆⋆͙̈ ° ♪ °••° ⋆""",
    r"""तेरो ma ko चोदने k बाद उसको ऐसे चंद सितारए नजर आएंगे""",
    r"""😝 Beta 🥶 लंड 🔥 पकड़ 😡 muh 😜 pe 😁 रगड़ 😂""",
    r"""𝐁ᴀᴀ𝐏 𝐊ᴏ 𝐑ᴇ𝐏ʟ𝐘 𝐁ᴀᴅ𝐈 𝐓ᴇ𝐙 𝐃ᴇʀ𝐀 𝐇ᴀɪ 😁😁🌷""",
    r"""𝙀𝙆 𝘽𝘼𝙍 𝘿𝙄𝙈𝘼𝙂 𝙂𝙃𝘼𝙍𝘼𝙈 𝙃𝙊𝙂𝙀𝙔𝘼 𝙉𝘼 𝘽𝙀𝙏𝘼"""
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

def get_chat_data(chat_id):
    if chat_id not in CHAT_TASKS:
        CHAT_TASKS[chat_id] = {
            "tasks": {},
            "muted": set(),
            "stripmedia": set(),
            "pfpstripper": False,
            "autoreply": {},
            "reptts": set(),
            "react_mode": None
        }
    return CHAT_TASKS[chat_id]

def is_admin(user_id):
    return user_id in AUTHORIZED_ADMINS or user_id == OWNER_ID

# --- Helper Commands Execution ---

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

async def cmd_vgcnc(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id): return
    raw_text = update.message.text.replace("+vgcnc", "").strip()
    parts = raw_text.split(" ", 1)
    titles_raw = parts[1] if len(parts) > 1 else parts[0]
    titles = [t.strip() for t in titles_raw.split("|") if t.strip()]
    if not titles: return

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

async def cmd_stopgcnc(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_data = get_chat_data(update.effective_chat.id)
    if "gcnc" in chat_data["tasks"]:
        chat_data["tasks"]["gcnc"].cancel()
        del chat_data["tasks"]["gcnc"]

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

async def cmd_vtarget(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id): return
    args = update.message.text.split()[1:]
    if len(args) < 2: return
    user, custom_text = args[0], " ".join(args[1:])
    chat_data = get_chat_data(update.effective_chat.id)
    if "target" in chat_data["tasks"]: chat_data["tasks"]["target"].cancel()

    async def vtarget_loop():
        while True:
            await context.bot.send_message(chat_id=update.effective_chat.id, text=f"{user} {custom_text}")
            await asyncio.sleep(1.5)
    task = asyncio.create_task(vtarget_loop())
    chat_data["tasks"]["target"] = task

async def cmd_stoptarget(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_data = get_chat_data(update.effective_chat.id)
    if "target" in chat_data["tasks"]:
        chat_data["tasks"]["target"].cancel()
        del chat_data["tasks"]["target"]

async def cmd_spam(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id): return
    text = " ".join(update.message.text.split()[1:])
    if not text: return
    chat_data = get_chat_data(update.effective_chat.id)
    if "spam" in chat_data["tasks"]: chat_data["tasks"]["spam"].cancel()

    async def spam_loop():
        while True:
            await context.bot.send_message(chat_id=update.effective_chat.id, text=text)
            await asyncio.sleep(0.4)
    task = asyncio.create_task(spam_loop())
    chat_data["tasks"]["spam"] = task

async def cmd_stopspam(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_data = get_chat_data(update.effective_chat.id)
    if "spam" in chat_data["tasks"]:
        chat_data["tasks"]["spam"].cancel()
        del chat_data["tasks"]["spam"]

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

async def cmd_vflood(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id): return
    args = update.message.text.split()[1:]
    if len(args) < 2: return
    user, text = args[0], " ".join(args[1:])
    chat_data = get_chat_data(update.effective_chat.id)
    if "flood" in chat_data["tasks"]: chat_data["tasks"]["flood"].cancel()

    async def vflood_loop():
        while True:
            await context.bot.send_message(chat_id=update.effective_chat.id, text=f"🌊 {user} {text}")
            await asyncio.sleep(0.3)
    task = asyncio.create_task(vflood_loop())
    chat_data["tasks"]["flood"] = task

async def cmd_stopflood(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_data = get_chat_data(update.effective_chat.id)
    if "flood" in chat_data["tasks"]:
        chat_data["tasks"]["flood"].cancel()
        del chat_data["tasks"]["flood"]

async def cmd_gcpfp(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id): return
    reply = update.message.reply_to_message
    if not reply or not reply.photo: return
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

async def cmd_stopgcpfp(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_data = get_chat_data(update.effective_chat.id)
    if "gcpfp" in chat_data["tasks"]:
        chat_data["tasks"]["gcpfp"].cancel()
        del chat_data["tasks"]["gcpfp"]

async def cmd_voiceflood(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id): return
    reply = update.message.reply_to_message
    if not reply or not (reply.voice or reply.audio): return
    file_id = (reply.voice or reply.audio).file_id
    chat_data = get_chat_data(update.effective_chat.id)
    if "voiceflood" in chat_data["tasks"]: chat_data["tasks"]["voiceflood"].cancel()

    async def voice_loop():
        while True:
            await context.bot.send_voice(chat_id=update.effective_chat.id, voice=file_id)
            await asyncio.sleep(1)
    task = asyncio.create_task(voice_loop())
    chat_data["tasks"]["voiceflood"] = task

async def cmd_stopvoiceflood(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_data = get_chat_data(update.effective_chat.id)
    if "voiceflood" in chat_data["tasks"]:
        chat_data["tasks"]["voiceflood"].cancel()
        del chat_data["tasks"]["voiceflood"]

async def cmd_mute(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id): return
    reply = update.message.reply_to_message
    args = update.message.text.split()[1:]
    target_id = reply.from_user.id if reply else (int(args[0]) if args and args[0].isdigit() else None)
    if target_id: get_chat_data(update.effective_chat.id)["muted"].add(target_id)

async def cmd_unmute(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id): return
    reply = update.message.reply_to_message
    args = update.message.text.split()[1:]
    target_id = reply.from_user.id if reply else (int(args[0]) if args and args[0].isdigit() else None)
    if target_id: get_chat_data(update.effective_chat.id)["muted"].discard(target_id)

async def cmd_stripmedia(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id): return
    reply = update.message.reply_to_message
    args = update.message.text.split()[1:]
    target_id = reply.from_user.id if reply else (int(args[0]) if args and args[0].isdigit() else None)
    if target_id: get_chat_data(update.effective_chat.id)["stripmedia"].add(target_id)

async def cmd_stopstripmedia(update: Update, context: ContextTypes.DEFAULT_TYPE):
    get_chat_data(update.effective_chat.id)["stripmedia"].clear()

async def cmd_pfpstripper(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id): return
    args = update.message.text.split()[1:]
    state = args[0].lower() == "on" if args else False
    get_chat_data(update.effective_chat.id)["pfpstripper"] = state

async def cmd_autoreply(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id): return
    reply = update.message.reply_to_message
    args = update.message.text.split()[1:]
    target_id = None
    target_username = None

    if reply and reply.from_user: target_id = reply.from_user.id
    elif args:
        if args[0].isdigit(): target_id = int(args[0])
        elif args[0].startswith("@"): target_username = args[0].lower().replace("@", "")

    if target_id or target_username:
        target_key = target_id if target_id else target_username
        get_chat_data(update.effective_chat.id)["autoreply"][target_key] = "RANDOM_LINES"

async def cmd_vautoreply(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id): return
    args = update.message.text.split()[1:]
    if len(args) < 2: return
    target_input = args[0]
    msg = " ".join(args[1:])
    target_key = int(target_input) if target_input.isdigit() else target_input.lower().replace("@", "")
    get_chat_data(update.effective_chat.id)["autoreply"][target_key] = msg

async def cmd_stopautoreply(update: Update, context: ContextTypes.DEFAULT_TYPE):
    get_chat_data(update.effective_chat.id)["autoreply"].clear()

async def cmd_reptts(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id): return
    reply = update.message.reply_to_message
    args = update.message.text.split()[1:]
    target_id = reply.from_user.id if reply else (int(args[0]) if args and args[0].isdigit() else None)
    if target_id: get_chat_data(update.effective_chat.id)["reptts"].add(target_id)

async def cmd_stopreptts(update: Update, context: ContextTypes.DEFAULT_TYPE):
    get_chat_data(update.effective_chat.id)["reptts"].clear()

async def cmd_clean(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id): return
    args = update.message.text.split()[1:]
    count = int(args[0]) if args and args[0].isdigit() else 10
    msg_id = update.message.message_id
    for i in range(count + 1):
        try: await context.bot.delete_message(chat_id=update.effective_chat.id, message_id=msg_id - i)
        except Exception: pass

async def cmd_togglereactall(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id): return
    chat_data = get_chat_data(update.effective_chat.id)
    chat_data["react_mode"] = None if chat_data["react_mode"] == "all" else "all"

async def cmd_togglereact(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id): return
    chat_data = get_chat_data(update.effective_chat.id)
    chat_data["react_mode"] = None if chat_data["react_mode"] == "admin" else "admin"

async def cmd_stopall(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id): return
    chat_data = get_chat_data(update.effective_chat.id)
    for task in list(chat_data["tasks"].values()): task.cancel()
    chat_data["tasks"].clear()
    chat_data["react_mode"] = None

async def cmd_omg(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id): return
    reply = update.message.reply_to_message
    if not reply or not (reply.photo or reply.video or reply.document or reply.voice): return
    try:
        if reply.photo: file_obj = await reply.photo[-1].get_file()
        elif reply.video: file_obj = await reply.video.get_file()
        elif reply.document: file_obj = await reply.document.get_file()
        elif reply.voice: file_obj = await reply.voice.get_file()

        file_bytes = await file_obj.download_as_bytearray()
        if reply.photo:
            await context.bot.send_photo(chat_id=update.effective_user.id, photo=bytes(file_bytes))
        else:
            await context.bot.send_document(chat_id=update.effective_user.id, document=bytes(file_bytes))
    except Exception: pass

async def cmd_tts(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = " ".join(update.message.text.split()[1:])
    if not text or gTTS is None: return
    try:
        tts = gTTS(text=text, lang="hi")
        tts.save("tts_helper.mp3")
        await context.bot.send_voice(chat_id=update.effective_chat.id, voice=open("tts_helper.mp3", "rb"))
    except Exception: pass

async def cmd_roasthi(update: Update, context: ContextTypes.DEFAULT_TYPE):
    args = update.message.text.split()[1:]
    target_name = None
    if update.message.reply_to_message and update.message.reply_to_message.from_user:
        target_name = f"@{update.message.reply_to_message.from_user.username}" if update.message.reply_to_message.from_user.username else update.message.reply_to_message.from_user.first_name
    elif args: target_name = " ".join(args)
    roast_text = random.choice(ROASTS_HI)
    text = f"🔥 {target_name} {roast_text}" if target_name else f"🔥 {roast_text}"
    await context.bot.send_message(chat_id=update.effective_chat.id, text=text)

async def cmd_roasteng(update: Update, context: ContextTypes.DEFAULT_TYPE):
    args = update.message.text.split()[1:]
    target_name = None
    if update.message.reply_to_message and update.message.reply_to_message.from_user:
        target_name = f"@{update.message.reply_to_message.from_user.username}" if update.message.reply_to_message.from_user.username else update.message.reply_to_message.from_user.first_name
    elif args: target_name = " ".join(args)
    roast_text = random.choice(ROASTS_ENG)
    text = f"🔥 {target_name} {roast_text}" if target_name else f"🔥 {roast_text}"
    await context.bot.send_message(chat_id=update.effective_chat.id, text=text)

async def cmd_slayinpowergifted(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != OWNER_ID: return
    args = update.message.text.split()[1:]
    target_id = int(args[0]) if args and args[0].isdigit() else (update.message.reply_to_message.from_user.id if update.message.reply_to_message else None)
    if target_id: AUTHORIZED_ADMINS.add(target_id)

async def cmd_slayinpowertaken(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != OWNER_ID: return
    args = update.message.text.split()[1:]
    target_id = int(args[0]) if args and args[0].isdigit() else (update.message.reply_to_message.from_user.id if update.message.reply_to_message else None)
    if target_id and target_id != OWNER_ID: AUTHORIZED_ADMINS.discard(target_id)

async def cmd_gban(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != OWNER_ID: return
    reply = update.message.reply_to_message
    args = update.message.text.split()[1:]
    target_id = reply.from_user.id if reply else (int(args[0]) if args and args[0].isdigit() else None)
    if target_id: GBANNED_USERS.add(target_id)

async def cmd_ungban(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != OWNER_ID: return
    reply = update.message.reply_to_message
    args = update.message.text.split()[1:]
    target_id = reply.from_user.id if reply else (int(args[0]) if args and args[0].isdigit() else None)
    if target_id: GBANNED_USERS.discard(target_id)

# --- Helper Router ---

async def helper_router(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.from_user: return
    user_id = update.message.from_user.id
    username = update.message.from_user.username.lower() if update.message.from_user.username else ""
    chat_id = update.effective_chat.id
    chat_data = get_chat_data(chat_id)
    text = update.message.text.strip() if update.message.text else ""

    # PFP Stripper Traps
    if chat_data.get("pfpstripper") and update.message.new_chat_photo:
        try: return await context.bot.delete_message(chat_id=chat_id, message_id=update.message.message_id)
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
            tts.save("reptts_helper.mp3")
            await context.bot.send_voice(chat_id=chat_id, voice=open("reptts_helper.mp3", "rb"))
        except Exception: pass

    # Fixed Reaction Execution (Sare Helper Bots 🤣 se react karenge)
    react_mode = chat_data.get("react_mode")
    if react_mode is not None and not text.startswith("+"):
        should_react = False
        if react_mode == "all": should_react = True
        elif react_mode == "admin" and is_admin(user_id): should_react = True

        if should_react:
            try:
                await context.bot.set_message_reaction(
                    chat_id=chat_id, 
                    message_id=update.message.message_id, 
                    reaction=[REACTION_EMOJI]
                )
            except Exception: pass

    # Command Execution Router
    if text.startswith("+"):
        cmd = text.split()[0][1:].lower()
        
        # Menu aur Start ko strictly ignore karna hai
        if cmd in ["menu", "start", "panel"]:
            return

        routes = {
            "gcnc": cmd_gcnc, "vgcnc": cmd_vgcnc, "stopgcnc": cmd_stopgcnc,
            "target": cmd_target, "vtarget": cmd_vtarget, "stoptarget": cmd_stoptarget,
            "spam": cmd_spam, "stopspam": cmd_stopspam,
            "flood": cmd_flood, "vflood": cmd_vflood, "stopflood": cmd_stopflood,
            "gcpfp": cmd_gcpfp, "stopgcpfp": cmd_stopgcpfp,
            "voiceflood": cmd_voiceflood, "stopvoiceflood": cmd_stopvoiceflood,
            "mute": cmd_mute, "unmute": cmd_unmute,
            "stripmedia": cmd_stripmedia, "stopstripmedia": cmd_stopstripmedia,
            "pfpstripper": cmd_pfpstripper,
            "autoreply": cmd_autoreply, "vautoreply": cmd_vautoreply, "stopautoreply": cmd_stopautoreply,
            "reptts": cmd_reptts, "stopreptts": cmd_stopreptts,
            "clean": cmd_clean, "togglereactall": cmd_togglereactall, "togglereact": cmd_togglereact, "stopall": cmd_stopall,
            "omg": cmd_omg, "tts": cmd_tts,
            "roasthi": cmd_roasthi, "roasteng": cmd_roasteng,
            "slayinpowergifted": cmd_slayinpowergifted, "slayinpowertaken": cmd_slayinpowertaken,
            "gban": cmd_gban, "ungban": cmd_ungban
        }
        if cmd in routes:
            await routes[cmd](update, context)

def main():
    TOKEN = os.environ.get("BOT_TOKEN")
    if not TOKEN: return
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(MessageHandler(filters.ALL, helper_router))
    app.run_polling()

if __name__ == '__main__':
    main()
