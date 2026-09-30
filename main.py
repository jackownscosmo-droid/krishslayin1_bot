# -*- coding: utf-8 -*-
import os
import time
import random
import asyncio
import logging
import sys

# Windows aur kuch terminals mein output force UTF-8 karne ke liye
if sys.stdout.encoding.lower() != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')

try:
    from gTTS import gTTS
except ImportError:
    gTTS = None

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ChatPermissions
from telegram.ext import (
    ApplicationBuilder, MessageHandler, 
    CallbackQueryHandler, ChatMemberHandler, filters, ContextTypes
)

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# Global Configuration
OWNER_ID = int(os.environ.get("OWNER_ID", "8821066459"))
MAIN_BOT_USERNAME = os.environ.get("MAIN_BOT_USERNAME", "krishslayin1_bot").lower().replace("@", "")
LOG_CHANNEL_ID = os.environ.get("LOG_CHANNEL_ID", None)

AUTHORIZED_ADMINS = set([8821066459, OWNER_ID])
GBANNED_USERS = set()
CHAT_TASKS = {}

# Global Cluster Instances Storage
BOT_INSTANCES = []

# Global Reaction State across all bot instances
GLOBAL_CHAT_REACT_MODE = {}
REACTION_EMOJI = "🤣"

# --- Catch Lines Array (NAME TAG IN FRONT) ---
CATCH_LINES = [
    "{name} 𝘽𝙃𝘼𝙂𝘼 𝘽𝙃𝘼𝙂𝘼 𝙆𝙀 𝙈𝘼𝙍𝙐𝙉𝙂𝘼 🤣🩷🙌🏾",
    "{name} 𝙃𝙊𝙎𝙃 𝙈𝙀 𝘼𝘼 𝙍𝙉𝘿𝙄𝙆𝙀",
    "{name} 𝐀𝐫𝐞𝐞𝐞𝐞 𝐓𝐞𝐫𝐢 𝐦𝐚𝐚𝐚 𝐫𝐧𝐝𝐢 😂😂😂😂👉🏻☝🏻🤸🏻🧑🏻‍🦯🏃🏻🧑🏻‍‍🦯⛹🏻🧑🏻‍🦯🧘🏻🧑🏻‍🦯🛌🏻🧘🏻",
    "{name} 🖋️ ये ले pen इससे अपने सर पे रंडीका बच्चा लिख दे",
    "{name} 𝙥𝙖𝙥𝙖 𝙗𝙤𝙡 𝙘𝙝𝙤𝙧 𝙙𝙪𝙣𝙜𝙖𝙖𝙖𝙖 𝙧𝙣𝙙𝙮 𝙠𝙚 𝙗𝙘𝙝𝙚",
    "{name} Tera maiya chod ke bhaiya nikaal dnege maderchodⓘ यह संदेश हटा दिया गया था क्योंकि तेरी माँ रेंडी",
    "{name} Çhµþ †êrï må kå ßhð§Ðå",
    "{name} 𝙘𝙝𝙪𝙥 𝙜𝙧𝙞𝙗 𝙠𝙞𝙣𝙣𝙚𝙧 𝙧𝙣𝙙𝙮😆😆🔥",
    "{name} तेरी मां की चूतड़ फाड़ दूंगा 𝐁ʜड़वे 𝐂ᴜᴅ अब 😁💪🏿🔥😁💪🏿🔥😁💪🏿🔥😁💪🏿🔥",
    "{name} 𝐓ᴏᴍᴍʏ 𝐒ʜᴜ 𝐒ʜᴜ 🐕🔥🐕🔥",
    "{name} 𝐁𝐀𝐇𝐀𝐑 𝐀𝐀 𝐑𝐔𝐍𝐃𝐘𝐊𝐄 𝐋𝐀𝐃𝐊𝐄 🐦‍‍🔥⛓️‍💥",
    "{name} तेरी मां को इतना chodunga की स्टोरी लगाके जस्टिस मांगेगा"
]

# --- 15 Lines Target Array ---
TARGET_15_LINES = [
    "Clap करो रंडीबाले ne joke mara h 😂👋🏻😂👋🏻😂👋🏻😂👋🏻😂👋🏻😂👋🏻",
    "चलेगी toh teri लंगड़ी maa 😁🔥😂👋🏻😂😂🔥🔥",
    "तेरी maa rundy 😜🙀⚡तेरी maa rundy 😜🙀⚡",
    "Oye message mat kar warna ᴛᴇʀɪ ᴍᴀᴀ ᴄʜᴏᴅ dunga🤣🤣",
    "अच्छा teri maa के बूब्स पे green veins h इसलिए tu itna खिलसता h 😂👏🏻",
    "𝐄ɴᴛʀʏ 𝐋ᴇʟɪ 𝐓ᴏ 𝐀sᴍᴀɴ 𝐊ɪ 𝐔ᴄʜᴀɪᴏ 𝐏ᴇ 𝐓ᴇʀɪ 𝐌ᴀ 𝐂ʜᴜᴅᴇɢɪ / 🌘🕊️",
    "Teri Maa Ko Football ⚽ bnake uske 𝗕𝗛😈𝗦แด pe laat 🦶🏻 marunga 🤩🔥",
    "Tri maa ke bosde pr jcb se khudai krwa duga rndyke😂😂🤟💥💥🤟",
    "Le धमाकेदार mukka kha रन्डी ke चाइल्ड 👊🏻👊🏻👊🏻🤣🤣",
    "चाल चल teri chudai डॉन hogyi !! Ab teri लंगड़ी maa दौड़ेगी 😂👋🏻",
    "subha ho ya sham chudte rhena hai tera kaam😂🔥😂🔥😂🔥",
    "randy pane me to teri ma aval darje ki hakdaar he😁👍😁👍😁👍😁👍",
    "𝘿𝙃𝘼𝙏 ʳⁿᵈⁱᵏᵉʸ 🤦🏿‍♂️💢𝘿𝙃𝘼𝙏 ʳⁿᵈⁱᵏᵉʸ 🤦🏿‍♂️💢",
    "ᗷᑌᖇ ᗪᗴᗪO Tᑌᕼᗩᖇ ᗰᗩIYᗩ Kᗴ 😂💔🤤🫦👅🤡",
    "𝐓ᴇʀɪ 𝐌ᴀᴀ 𝐂ʜᴜᴅᴋᴇ 𝐁ʜᴀᴀɢ 𝐑ᴀʜɪ -> 🏃🏻‍♀️🔥🏃🏻‍♀️🔥"
]

AUTOREPLY_LINES = [
    r"""बड़े दुःख के साथ हँसना पढ़ रहा है😂  𝐓ᴜ तेरी माँ रंडी 🤍😅🔥""",
    r"""𝙏𝙚𝙧𝙞 𝙢𝙖𝙖 𝙠𝙚 𝙝𝙤𝙨𝙙𝙚 𝙢𝙚 𝙡𝙖𝙩 𝙥𝙙𝙚𝙣𝙜𝙚 𝙗𝙝𝙤𝙩 𝙩𝙚𝙯 👻 😂👯😂👯😂👯""",
    r"""𝙏𝙀𝙍𝙄 𝙈𝘼 𝑑𝙄𝘿🇭🇻𝘼 𝙋𝙀𝙉𝙎𝙄𝙊𝙉 𝙃𝘼𝙉𝙀 𝙒𝘼𝙇𝙄 𝙍𝙉𝘿𝙄 🤣""",
    r"""तेरी maa की chut में ऐसा HACK lgaunga Light की speed में बच्चे देगी""",
    r"""𝑩𝑯𝑨𝑮 𝑹𝑨𝑵𝑫𝒀𝑲𝑬 𝑻𝑬𝑹𝑰 𝑴𝑨 𝑪𝑯𝑼𝑫𝑹𝑰 𝑯𝑨𝑰 ᯓ🏃🏻‍♀️‍➡️ᯓ🏃🏻‍♀️‍➡️ᯓ🏃🏻‍♀️‍➡️""",
    r"""𝘽𝙃𝘼𝙂𝘼 𝘽𝙃𝘼𝙂𝘼 𝙆𝙀 𝙈𝘼𝙍𝙐𝙉𝙂𝘼 🤣🩷🙌🏾"""
]

TARGET_LINES = [
    r"""˚∧＿∧   +        — ͟͞͞🥛 (  •‿• )つ  Special attack: teri mummy ka dudh 😂😂""",
    r"""𝙉𝙀𝙆𝘼𝘼𝘼𝙇 𝙈𝘼𝘿𝘼𝘼𝙍𝘾𝙃𝘿👍🏼👍🏼👍🏼👍🏼👍🏼""",
    r"""तेरी बहन का भोसड़ा 😂🤸🏻‍♂️😂🤸🏻‍♂️ 𝘾𝙃𝙐𝙋 𝙍𝙉𝘿𝙄𝙆𝙀"""
]

FLOOD_LINES = [
    r"""𝙏𝙚𝙧𝙞 𝙢𝙖𝙖 𝙠𝙚 𝙗𝙝𝙤𝙨𝙙𝙚 𝙢𝙚 𝙡𝙖𝙩 𝙥𝙙𝙚𝙣𝙜𝙚 𝙗𝙝𝙤𝙩 𝙩𝙚𝙯 👻 😂👯😂👯""",
    r"""तेरो ma ko चोदने k बाद उसको ऐसे चंद सितारए नजर आएंगे""",
    r"""😝 Beta 🥶 लंड 🔥 पकड़ 😡 muh 😜 pe 😁 रगड़ 😂"""
]

ROASTS_HI = [
    "Teri shakal dekh ke Telegram ka server bhi crash ho jaye!",
    "Itna dimaag agar sahi jagah lagaya hota toh aaj NASA me hota!"
]

ROASTS_ENG = [
    "You bring everyone so much joy... when you leave the room!",
    "Your brain is like the 404 error page—permanently missing content."
]

VALID_COMMANDS = {
    "start", "menu", "panel", "gcnc", "vgcnc", "stopgcnc",
    "target", "vtarget", "stoptarget", "spam", "stopspam",
    "flood", "vflood", "stopflood", "gcpfp", "stopgcpfp",
    "voiceflood", "stopvoiceflood", "mute", "unmute", "mutelist",
    "stripmedia", "stopstripmedia", "pfpstripper", "autoreply",
    "vautoreply", "stopautoreply", "reptts", "stopreptts",
    "clean", "togglereactall", "togglereact", "stopall",
    "scan", "ping", "getid", "status", "omg", "tts", 
    "ttshi", "ttsen", "ttsjap", "ttsgerman", 
    "roasthi", "roasteng", "cluster", "broadcast",
    "slayinpowergifted", "slayinpowertaken", "slayinfor",
    "gban", "ungban", "ht", "leave", "leavekrishslayin", "catch", "stopcatch",
    "lock", "unlock", "promote1", "promote2", "demote", "kick", "adminlist"
}

MAIN_BOT_ONLY_COMMANDS = VALID_COMMANDS

def get_chat_data(chat_id):
    if chat_id not in CHAT_TASKS:
        CHAT_TASKS[chat_id] = {
            "tasks": {},
            "muted": set(),
            "stripmedia": set(),
            "pfpstripper": False,
            "autoreply": {},
            "reptts": set(),
            "vtarget_trap": {},
            "catch_trap": {},
            "media_locked": False,
            "admin_levels": {},  # {user_id: 1 or 2}
            "kick_tracker": {}   # {user_id: [timestamps]}
        }
    return CHAT_TASKS[chat_id]

def is_admin(user_id):
    return user_id in AUTHORIZED_ADMINS or user_id == OWNER_ID

async def send_auto_delete_msg(context: ContextTypes.DEFAULT_TYPE, chat_id: int, text: str, delay: int = 120, parse_mode: str = None):
    try:
        msg = await context.bot.send_message(chat_id=chat_id, text=text, parse_mode=parse_mode)
        async def auto_delete():
            await asyncio.sleep(delay)
            try:
                await msg.delete()
            except Exception:
                pass
        asyncio.create_task(auto_delete())
        return msg
    except Exception as e:
        logging.error(f"Failed to send auto-delete message: {e}")

async def is_level1_or_manual_admin(chat_id: int, user_id: int, context: ContextTypes.DEFAULT_TYPE) -> bool:
    if user_id == OWNER_ID:
        return True
    chat_data = get_chat_data(chat_id)
    level = chat_data["admin_levels"].get(user_id)
    if level == 1:
        return True
    if level == 2:
        return False
    # Check if manually assigned admin in Telegram
    try:
        member = await context.bot.get_chat_member(chat_id=chat_id, user_id=user_id)
        if member.status == "creator" or (member.status == "administrator" and member.can_promote_members):
            return True
        if member.status == "administrator" and user_id not in chat_data["admin_levels"]:
            return True
    except Exception:
        pass
    return False

async def get_active_bots_in_chat(chat_id):
    active_bots = []
    for bot in BOT_INSTANCES:
        try:
            me = await bot.get_me()
            member = await bot.get_chat_member(chat_id=chat_id, user_id=me.id)
            if member.status in ['member', 'administrator', 'creator']:
                active_bots.append(bot)
        except Exception:
            pass
    return active_bots if active_bots else BOT_INSTANCES

async def send_log(context: ContextTypes.DEFAULT_TYPE, text: str):
    if LOG_CHANNEL_ID:
        try:
            await context.bot.send_message(chat_id=int(LOG_CHANNEL_ID), text=text, parse_mode="Markdown")
        except Exception as e:
            logging.error(f"Failed to send log: {e}")

async def hard_stop_all(chat_id: int, context: ContextTypes.DEFAULT_TYPE, user_id: int):
    chat_data = get_chat_data(chat_id)
    
    for task_name, task in list(chat_data["tasks"].items()):
        task.cancel()
    chat_data["tasks"].clear()

    chat_data["muted"].clear()
    chat_data["stripmedia"].clear()
    chat_data["autoreply"].clear()
    chat_data["reptts"].clear()
    chat_data["vtarget_trap"].clear()
    chat_data["catch_trap"].clear()
    chat_data["pfpstripper"] = False
    chat_data["media_locked"] = False
    GLOBAL_CHAT_REACT_MODE[chat_id] = None

    await send_log(context, f"🚨 *ABSOLUTE KILL SWITCH TRIGGERED*\nChat: `{chat_id}`\nAdmin/User: `{user_id}`")

# --- UI Helpers ---

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
            "• +gcnc [spd] [name] — Coordinated title loop\n"
            "• +vgcnc [spd] [Title 1 | Title 2] — Title rotator\n"
            "• +stopgcnc — Halt active title loop\n"
            "• +target [user] — Mention loop\n"
            "• +vtarget [@user] [@bots...] — Advanced 15-reply target trap\n"
            "• +stoptarget — Disarm targeting loops\n"
            "• +catch [user] [count] — Dynamic bot swipe trap on new messages\n"
            "• +stopcatch — Disarm catch trap\n"
            "• +spam [text] — Multi-bot high-speed spam\n"
            "• +stopspam — EMERGENCY KILL-SWITCH (STOPS EVERYTHING)\n"
            "• +flood [user] — Mention flood\n"
            "• +vflood [user] [text] — Custom mention flood\n"
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
            "• +lock — Auto-delete all photos/videos instantly (Everyone)\n"
            "• +unlock — Unlock media sending in chat\n"
            "• +promote1 — Level 1 Admin 🥇\n"
            "• +promote2 — Level 2 Admin 🥈\n"
            "• +demote — Strip admin rights\n"
            "• +kick — Kick member\n"
            "• +adminlist — List active group admins\n"
            "• +panel — Interactive inline dashboard\n"
            "• +ht — Honeytrap (Shadow-mute with fake unmute button)\n"
            "• +mute [user] — Shadow-mute target\n"
            "• +unmute [user] — Unmute target\n"
            "• +mutelist — View muted users\n"
            "• +stripmedia [user] — Auto-delete media\n"
            "• +stopstripmedia — Disable media stripper\n"
            "• +pfpstripper on/off — Delete group PFP changes\n"
            "• +autoreply [user] — Auto-reply trap\n"
            "• +vautoreply [user] [msg] — Custom reply trap\n"
            "• +stopautoreply — Disarm auto-reply\n"
            "• +reptts [user] — Voice trap\n"
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
            "• +ping — Matrix latency test for all bots\n"
            "• +getid — Fetch numeric ID\n"
            "• +status — Cluster state\n"
            "• +omg — Extract view-once media to PM\n"
            "• +tts [text] — Voice Note TTS (default HI)\n"
            "• +ttshi/ttsen/ttsjap/ttsgerman [text] — Custom Language Voice Notes\n"
            "• +roasthi [user] — Hindi roast\n"
            "• +roasteng [user] — English roast"
        )
    elif page == 5:
        admin_list = "\n".join([f"• {uid}" for uid in AUTHORIZED_ADMINS])
        return (
            "👑 OWNER CONTROLS\n"
            "────────────────────────────\n"
            "• +leave [@bot_username] — Remove specific bot from chat\n"
            "• +leavekrishslayin — Mass leave all cluster bots\n"
            "• +cluster — Node telemetry\n"
            "• +broadcast [text] — Network broadcast\n"
            "• +slayinpowergifted [id] — Add admin\n"
            "• +slayinpowertaken [id] — Revoke admin\n"
            "• +slayinfor — List admins\n"
            "• +gban [user] — Global ban\n"
            "• +ungban [user] — Global unban\n\n"
            f"⚡ Active Admins:\n{admin_list}"
        )

# --- Callbacks ---

async def menu_callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    data = query.data
    
    if data == "fake_unmute":
        return await query.answer(
            text="🤣 Nice try! You are muted and cannot unmute yourself.", 
            show_alert=True
        )

    await query.answer()
    
    if data == "menu_close":
        return await query.message.delete()
    elif data == "open_panel":
        keyboard = [
            [InlineKeyboardButton("Abort All Active Tasks 🚨", callback_data="stop_all")],
            [InlineKeyboardButton("✝️ Return to Main Menu", callback_data="menu_1")]
        ]
        return await query.edit_message_text("🎛️ BATTLE-DECK CONTROL PANEL:\nDirect chat override active.", reply_markup=InlineKeyboardMarkup(keyboard))
    elif data == "stop_all":
        await hard_stop_all(query.message.chat_id, context, query.from_user.id)
        return await query.edit_message_text("🚨 ALL ACTIVE TASKS & TRAPS TERMINATED 100%.", reply_markup=get_menu_keyboard(1))
    elif data.startswith("menu_"):
        page = int(data.split("_")[1])
        await query.edit_message_text(get_menu_text(page), reply_markup=get_menu_keyboard(page))

# --- Anti-Mass Kick Tracker (2 Min Rule) ---
async def track_member_removals(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.chat_member:
        return
    
    chat_member = update.chat_member
    old_status = chat_member.old_chat_member.status
    new_status = chat_member.new_chat_member.status
    actor = chat_member.from_user
    target = chat_member.new_chat_member.user
    chat_id = update.effective_chat.id

    if old_status in ['member', 'administrator', 'restricted'] and new_status in ['kicked', 'left']:
        if actor.id == target.id:
            return  # User left voluntarily
        
        chat_data = get_chat_data(chat_id)
        now = time.time()
        
        if actor.id not in chat_data["kick_tracker"]:
            chat_data["kick_tracker"][actor.id] = []
            
        chat_data["kick_tracker"][actor.id].append(now)
        # Filter removals within last 120 seconds (2 minutes)
        chat_data["kick_tracker"][actor.id] = [t for t in chat_data["kick_tracker"][actor.id] if now - t <= 120]
        
        removal_count = len(chat_data["kick_tracker"][actor.id])
        
        # Trigger Anti-Nuke if 4 or more removals occur within 2 minutes
        if removal_count >= 4:
            try:
                # 1. Demote admin rights
                await context.bot.promote_chat_member(
                    chat_id=chat_id,
                    user_id=actor.id,
                    can_change_info=False,
                    can_post_messages=False,
                    can_edit_messages=False,
                    can_delete_messages=False,
                    can_invite_users=False,
                    can_restrict_members=False,
                    can_pin_messages=False,
                    can_promote_members=False,
                    can_manage_video_chats=False,
                    is_anonymous=False
                )
            except Exception:
                pass
            
            try:
                # 2. Ban perpetrator from group
                await context.bot.ban_chat_member(chat_id=chat_id, user_id=actor.id)
            except Exception:
                pass

            chat_data["admin_levels"].pop(actor.id, None)
            AUTHORIZED_ADMINS.discard(actor.id)
            chat_data["kick_tracker"][actor.id] = []

            await send_auto_delete_msg(
                context,
                chat_id,
                f"🚨 **ANTI-NUKE TRIGGERED!**\nUser [{actor.first_name}](tg://user?id={actor.id}) removed {removal_count} members in <2 mins.\n\n⚡ Action: Rights Stripped & Removed from Group!",
                delay=120,
                parse_mode="Markdown"
            )
            await send_log(context, f"🚨 *ANTI-NUKE EXECUTED*\nChat: `{chat_id}`\nPerpetrator: `{actor.id}`\nRemovals: `{removal_count}`")

# --- Management & Promotion Commands ---

async def cmd_promote1(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_level1_or_manual_admin(update.effective_chat.id, update.effective_user.id, context):
        return await send_auto_delete_msg(context, update.effective_chat.id, "⚠️ Permission Denied!")

    reply = update.message.reply_to_message
    args = update.message.text.split()[1:]
    
    target_user = reply.from_user if reply else None
    target_id = target_user.id if target_user else (int(args[0]) if args and args[0].isdigit() else None)

    if not target_id:
        return await send_auto_delete_msg(context, update.effective_chat.id, "Usage: +promote1 (Reply to user or pass ID)")

    try:
        if target_user:
            target_name = target_user.first_name
        else:
            member = await context.bot.get_chat_member(update.effective_chat.id, target_id)
            target_name = member.user.first_name if member and member.user else str(target_id)
    except Exception:
        target_name = str(target_id)

    try:
        await context.bot.promote_chat_member(
            chat_id=update.effective_chat.id,
            user_id=target_id,
            can_manage_chat=True,
            can_change_info=False,
            can_delete_messages=True,
            can_restrict_members=False,
            can_invite_users=True,
            can_pin_messages=True,
            can_manage_video_chats=True,
            can_promote_members=True,
            is_anonymous=False,
            can_post_stories=True,
            can_edit_stories=True,
            can_delete_stories=True
        )
        try:
            await context.bot.set_chat_administrator_custom_title(
                chat_id=update.effective_chat.id,
                user_id=target_id,
                custom_title="🥇"
            )
        except Exception:
            pass

        get_chat_data(update.effective_chat.id)["admin_levels"][target_id] = 1
        AUTHORIZED_ADMINS.add(target_id)
        await send_auto_delete_msg(context, update.effective_chat.id, f"{target_name} promoted 🥇 with full assigned rights", delay=120)
    except Exception as e:
        await send_auto_delete_msg(context, update.effective_chat.id, f"❌ Failed to promote: {str(e)}", delay=120)

async def cmd_promote2(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_level1_or_manual_admin(update.effective_chat.id, update.effective_user.id, context):
        return await send_auto_delete_msg(context, update.effective_chat.id, "⚠️ Permission Denied!")

    reply = update.message.reply_to_message
    args = update.message.text.split()[1:]
    
    target_user = reply.from_user if reply else None
    target_id = target_user.id if target_user else (int(args[0]) if args and args[0].isdigit() else None)

    if not target_id:
        return await send_auto_delete_msg(context, update.effective_chat.id, "Usage: +promote2 (Reply to user or pass ID)")

    try:
        if target_user:
            target_name = target_user.first_name
        else:
            member = await context.bot.get_chat_member(update.effective_chat.id, target_id)
            target_name = member.user.first_name if member and member.user else str(target_id)
    except Exception:
        target_name = str(target_id)

    try:
        await context.bot.promote_chat_member(
            chat_id=update.effective_chat.id,
            user_id=target_id,
            can_manage_chat=True,
            can_change_info=False,
            can_delete_messages=True,
            can_restrict_members=False,
            can_invite_users=True,
            can_pin_messages=True,
            can_manage_video_chats=True,
            can_promote_members=False,
            is_anonymous=False,
            can_post_stories=True,
            can_edit_stories=True,
            can_delete_stories=True
        )
        try:
            await context.bot.set_chat_administrator_custom_title(
                chat_id=update.effective_chat.id,
                user_id=target_id,
                custom_title="🥈"
            )
        except Exception:
            pass

        get_chat_data(update.effective_chat.id)["admin_levels"][target_id] = 2
        AUTHORIZED_ADMINS.add(target_id)
        await send_auto_delete_msg(context, update.effective_chat.id, f"{target_name} promoted 🥈 with restricted assigned rights", delay=120)
    except Exception as e:
        await send_auto_delete_msg(context, update.effective_chat.id, f"❌ Failed to promote: {str(e)}", delay=120)

async def cmd_demote(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_level1_or_manual_admin(update.effective_chat.id, update.effective_user.id, context):
        return await send_auto_delete_msg(context, update.effective_chat.id, "⚠️ Permission Denied!")

    reply = update.message.reply_to_message
    args = update.message.text.split()[1:]
    
    target_user = reply.from_user if reply else None
    target_id = target_user.id if target_user else (int(args[0]) if args and args[0].isdigit() else None)

    if not target_id:
        return await send_auto_delete_msg(context, update.effective_chat.id, "Usage: +demote (Reply to user or pass ID)")

    try:
        if target_user:
            target_name = target_user.first_name
        else:
            member = await context.bot.get_chat_member(update.effective_chat.id, target_id)
            target_name = member.user.first_name if member and member.user else str(target_id)
    except Exception:
        target_name = str(target_id)

    try:
        await context.bot.promote_chat_member(
            chat_id=update.effective_chat.id,
            user_id=target_id,
            can_change_info=False, can_post_messages=False, can_edit_messages=False,
            can_delete_messages=False, can_invite_users=False, can_restrict_members=False,
            can_pin_messages=False, can_promote_members=False, can_manage_video_chats=False,
            is_anonymous=False
        )
        get_chat_data(update.effective_chat.id)["admin_levels"].pop(target_id, None)
        if target_id != OWNER_ID:
            AUTHORIZED_ADMINS.discard(target_id)
        await send_auto_delete_msg(context, update.effective_chat.id, f"{target_name} demoted", delay=120)
    except Exception as e:
        await send_auto_delete_msg(context, update.effective_chat.id, f"❌ Failed to demote: {str(e)}", delay=120)

async def cmd_kick(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id): return
    reply = update.message.reply_to_message
    args = update.message.text.split()[1:]
    target_id = reply.from_user.id if reply else (int(args[0]) if args and args[0].isdigit() else None)

    if not target_id:
        return await send_auto_delete_msg(context, update.effective_chat.id, "Usage: +kick (Reply to user or pass ID)")

    chat_data = get_chat_data(update.effective_chat.id)
    executor_level = chat_data["admin_levels"].get(update.effective_user.id)
    target_level = chat_data["admin_levels"].get(target_id)

    if executor_level == 2 and target_level is not None:
        return await send_auto_delete_msg(context, update.effective_chat.id, "🚫 Level 2 Admins 🥈 cannot kick other admins!")

    try:
        await context.bot.ban_chat_member(chat_id=update.effective_chat.id, user_id=target_id)
        await context.bot.unban_chat_member(chat_id=update.effective_chat.id, user_id=target_id)
        await send_auto_delete_msg(context, update.effective_chat.id, f"👢 User {target_id} has been kicked from the chat.", delay=120)
    except Exception as e:
        await send_auto_delete_msg(context, update.effective_chat.id, f"❌ Failed to kick: {str(e)}", delay=120)

async def cmd_adminlist(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        admins = await context.bot.get_chat_administrators(chat_id=update.effective_chat.id)
        chat_data = get_chat_data(update.effective_chat.id)
        
        owner_line = ""
        bot_admin_lines = []

        for a in admins:
            user = a.user
            if a.status == "creator":
                owner_line = f"• {user.first_name} : Owner 👑"
            elif user.id in chat_data["admin_levels"]:
                lvl = chat_data["admin_levels"][user.id]
                tag = "🥇" if lvl == 1 else "🥈"
                bot_admin_lines.append(f"• {user.first_name} : Admin {tag}")

        list_content = ["Admin List 🥈🥇\n", "━━━━━━━━━━━━━━━━━━━━━━"]
        if owner_line:
            list_content.append(owner_line)
        if bot_admin_lines:
            list_content.extend(bot_admin_lines)

        text = "\n".join(list_content)
        await send_auto_delete_msg(context, update.effective_chat.id, text, delay=120)
    except Exception as e:
        await send_auto_delete_msg(context, update.effective_chat.id, f"❌ Failed to fetch adminlist: {str(e)}", delay=120)

# --- Combat Commands ---

async def cmd_gcnc(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id): return
    args = update.message.text.split()[1:]
    speed = 0.3
    name = "KRISHSLAYIN"

    if args:
        try:
            speed = float(args[0])
            name = " ".join(args[1:]) if len(args) > 1 else "KRISHSLAYIN"
        except ValueError:
            name = " ".join(args)

    chat_data = get_chat_data(update.effective_chat.id)
    if "gcnc" in chat_data["tasks"]: chat_data["tasks"]["gcnc"].cancel()

    async def multi_gcnc_loop():
        titles = [f"⚡ {name} ⚡", f"🔥 {name} 🔥", f"👑 {name} 👑"]
        title_idx = 0
        bot_idx = 0
        total_bots = len(BOT_INSTANCES)
        while True:
            current_bot = BOT_INSTANCES[bot_idx % total_bots]
            try:
                await current_bot.set_chat_title(chat_id=update.effective_chat.id, title=titles[title_idx % len(titles)])
                title_idx += 1
            except Exception: pass
            bot_idx += 1
            await asyncio.sleep(speed if speed > 0 else 0.05)

    task = asyncio.create_task(multi_gcnc_loop())
    chat_data["tasks"]["gcnc"] = task
    await send_auto_delete_msg(context, update.effective_chat.id, f"⚔️ All {len(BOT_INSTANCES)} Cluster Bots engaged in GCNC Loop (Speed: {speed}s).", delay=120)

async def cmd_vgcnc(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id): return
    raw_text = update.message.text.replace("+vgcnc", "").strip()
    parts = raw_text.split(" ", 1)
    
    speed = 0.3
    titles_raw = ""

    if len(parts) > 0:
        try:
            speed = float(parts[0])
            titles_raw = parts[1] if len(parts) > 1 else ""
        except ValueError:
            titles_raw = raw_text

    titles = [t.strip() for t in titles_raw.split("|") if t.strip()]
    if not titles: return await send_auto_delete_msg(context, update.effective_chat.id, "Usage: +vgcnc [speed] Title 1 | Title 2", delay=120)

    chat_data = get_chat_data(update.effective_chat.id)
    if "gcnc" in chat_data["tasks"]: chat_data["tasks"]["gcnc"].cancel()

    async def multi_vgcnc_loop():
        title_idx = 0
        bot_idx = 0
        total_bots = len(BOT_INSTANCES)
        while True:
            current_bot = BOT_INSTANCES[bot_idx % total_bots]
            try:
                await current_bot.set_chat_title(chat_id=update.effective_chat.id, title=titles[title_idx % len(titles)])
                title_idx += 1
            except Exception: pass
            bot_idx += 1
            await asyncio.sleep(speed if speed > 0 else 0.05)

    task = asyncio.create_task(multi_vgcnc_loop())
    chat_data["tasks"]["gcnc"] = task
    await send_auto_delete_msg(context, update.effective_chat.id, f"⚡ All {len(BOT_INSTANCES)} Cluster Bots engaged in VGCNC Rotator (Speed: {speed}s).", delay=120)

async def cmd_stopgcnc(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_data = get_chat_data(update.effective_chat.id)
    if "gcnc" in chat_data["tasks"]:
        chat_data["tasks"]["gcnc"].cancel()
        del chat_data["tasks"]["gcnc"]
        await send_auto_delete_msg(context, update.effective_chat.id, "🛑 Title loop disarmed across all cluster bots.", delay=120)

async def cmd_spam(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id): return
    text = " ".join(update.message.text.split()[1:])
    if not text: return await send_auto_delete_msg(context, update.effective_chat.id, "Usage: +spam <text>", delay=120)
    chat_data = get_chat_data(update.effective_chat.id)
    if "spam" in chat_data["tasks"]: chat_data["tasks"]["spam"].cancel()

    async def multi_spam_loop():
        bot_idx = 0
        total_bots = len(BOT_INSTANCES)
        while True:
            current_bot = BOT_INSTANCES[bot_idx % total_bots]
            try: await current_bot.send_message(chat_id=update.effective_chat.id, text=text)
            except Exception: pass
            bot_idx += 1
            await asyncio.sleep(0.12)

    task = asyncio.create_task(multi_spam_loop())
    chat_data["tasks"]["spam"] = task

async def cmd_stopspam(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id): return
    await hard_stop_all(update.effective_chat.id, context, update.effective_user.id)
    await send_auto_delete_msg(
        context, update.effective_chat.id, 
        "🛑 STRICT EMERGENCY STOP: All active tasks, spam, GCNC, traps, and loops have been KILLED instantly!",
        delay=120
    )

async def cmd_target(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id): return
    args = update.message.text.split()[1:]
    user = args[0] if args else "@target"
    chat_data = get_chat_data(update.effective_chat.id)
    if "target" in chat_data["tasks"]: chat_data["tasks"]["target"].cancel()

    async def multi_target_loop():
        bot_idx = 0
        total_bots = len(BOT_INSTANCES)
        while True:
            current_bot = BOT_INSTANCES[bot_idx % total_bots]
            line = random.choice(TARGET_LINES)
            try: await current_bot.send_message(chat_id=update.effective_chat.id, text=f"{user}\n{line}")
            except Exception: pass
            bot_idx += 1
            await asyncio.sleep(0.2)

    task = asyncio.create_task(multi_target_loop())
    chat_data["tasks"]["target"] = task

async def cmd_vtarget(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id): return
    text_lower = update.message.text.lower()
    
    reply = update.message.reply_to_message
    target_id = None
    target_username = None

    if reply and reply.from_user:
        target_id = reply.from_user.id
        target_username = reply.from_user.username.lower() if reply.from_user.username else None
    else:
        args = update.message.text.split()[1:]
        for arg in args:
            is_bot = False
            for b in BOT_INSTANCES:
                me = await b.get_me()
                if arg.replace("@", "").lower() == me.username.lower():
                    is_bot = True
                    break
            if not is_bot:
                target_id = arg.lower().replace("@", "")
                break

    if not target_id:
        return await send_auto_delete_msg(context, update.effective_chat.id, "⚠️ Please specify a target! (Reply or @username)", delay=120)

    my_me = await context.bot.get_me()
    my_username = my_me.username.lower()
    
    tagged_bots = []
    for b in BOT_INSTANCES:
        me = await b.get_me()
        if f"@{me.username.lower()}" in text_lower:
            tagged_bots.append(me.username.lower())
            
    if not tagged_bots:
        tagged_bots = [my_username]

    chat_data = get_chat_data(update.effective_chat.id)
    if "vtarget_trap" not in chat_data:
        chat_data["vtarget_trap"] = {}
        
    chat_data["vtarget_trap"][str(target_id)] = tagged_bots
    if target_username:
        chat_data["vtarget_trap"][target_username] = tagged_bots

    await send_auto_delete_msg(
        context, update.effective_chat.id, 
        f"🎯 Advanced 15-Swipe Trap Activated! {len(tagged_bots)} bot(s) will attack!",
        delay=120
    )

async def cmd_stoptarget(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_data = get_chat_data(update.effective_chat.id)
    stopped = False
    
    if "target" in chat_data["tasks"]:
        chat_data["tasks"]["target"].cancel()
        del chat_data["tasks"]["target"]
        stopped = True
        
    if "vtarget_trap" in chat_data and chat_data["vtarget_trap"]:
        chat_data["vtarget_trap"].clear()
        stopped = True
        
    if stopped:
        await send_auto_delete_msg(context, update.effective_chat.id, "🛑 All Targeting and 15-Swipe Traps disarmed.", delay=120)

async def cmd_catch(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id): return
    args = update.message.text.split()[1:]
    reply = update.message.reply_to_message
    
    target_key = None
    count = 10

    if reply and reply.from_user:
        target_key = str(reply.from_user.id)
    elif args:
        for arg in args:
            if arg.isdigit():
                count = int(arg)
            else:
                target_key = arg.lower().replace("@", "")

    if not target_key:
        return await send_auto_delete_msg(
            context, update.effective_chat.id, 
            "⚠️ Please specify a target! (Reply or +catch @user 10)",
            delay=120
        )

    chat_data = get_chat_data(update.effective_chat.id)
    if "catch_trap" not in chat_data:
        chat_data["catch_trap"] = {}

    chat_data["catch_trap"][target_key] = count
    await send_auto_delete_msg(
        context, update.effective_chat.id, 
        f"🎯 Catch Trap Activated on {target_key}! A random active bot will reply with {count} lines on their next message.",
        delay=120
    )

async def cmd_stopcatch(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_data = get_chat_data(update.effective_chat.id)
    if "catch_trap" in chat_data:
        chat_data["catch_trap"].clear()
    await send_auto_delete_msg(context, update.effective_chat.id, "🛑 Catch trap disarmed.", delay=120)

async def cmd_lock(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_level1_or_manual_admin(update.effective_chat.id, update.effective_user.id, context):
        return await send_auto_delete_msg(context, update.effective_chat.id, "⚠️ Only Level 1 Admins or Main Admins can use +lock!", delay=120)
    chat_data = get_chat_data(update.effective_chat.id)
    chat_data["media_locked"] = True
    await send_auto_delete_msg(
        context, update.effective_chat.id, 
        "🔒 MEDIA LOCK ACTIVATED! All photos/videos will be auto-deleted.",
        delay=120
    )

async def cmd_unlock(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_level1_or_manual_admin(update.effective_chat.id, update.effective_user.id, context):
        return await send_auto_delete_msg(context, update.effective_chat.id, "⚠️ Only Level 1 Admins or Main Admins can use +unlock!", delay=120)
    chat_data = get_chat_data(update.effective_chat.id)
    chat_data["media_locked"] = False
    await send_auto_delete_msg(context, update.effective_chat.id, "🔓 MEDIA LOCK DEACTIVATED!", delay=120)

async def cmd_flood(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id): return
    args = update.message.text.split()[1:]
    user = args[0] if args else "@target"
    chat_data = get_chat_data(update.effective_chat.id)
    if "flood" in chat_data["tasks"]: chat_data["tasks"]["flood"].cancel()

    async def multi_flood_loop():
        bot_idx = 0
        total_bots = len(BOT_INSTANCES)
        while True:
            for line in FLOOD_LINES:
                current_bot = BOT_INSTANCES[bot_idx % total_bots]
                try: await current_bot.send_message(chat_id=update.effective_chat.id, text=f"{user}\n{line}")
                except Exception: pass
                bot_idx += 1
                await asyncio.sleep(0.15)

    task = asyncio.create_task(multi_flood_loop())
    chat_data["tasks"]["flood"] = task

async def cmd_vflood(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id): return
    args = update.message.text.split()[1:]
    if len(args) < 2: return await send_auto_delete_msg(context, update.effective_chat.id, "Usage: +vflood <user> <text>", delay=120)
    user, text = args[0], " ".join(args[1:])
    chat_data = get_chat_data(update.effective_chat.id)
    if "flood" in chat_data["tasks"]: chat_data["tasks"]["flood"].cancel()

    async def multi_vflood_loop():
        bot_idx = 0
        total_bots = len(BOT_INSTANCES)
        while True:
            current_bot = BOT_INSTANCES[bot_idx % total_bots]
            try: await current_bot.send_message(chat_id=update.effective_chat.id, text=f"🌊 {user} {text}")
            except Exception: pass
            bot_idx += 1
            await asyncio.sleep(0.15)

    task = asyncio.create_task(multi_vflood_loop())
    chat_data["tasks"]["flood"] = task

async def cmd_stopflood(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_data = get_chat_data(update.effective_chat.id)
    if "flood" in chat_data["tasks"]:
        chat_data["tasks"]["flood"].cancel()
        del chat_data["tasks"]["flood"]
        await send_auto_delete_msg(context, update.effective_chat.id, "🛑 Flood stopped.", delay=120)

async def cmd_gcpfp(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id): return
    reply = update.message.reply_to_message
    if not reply or not reply.photo: return await send_auto_delete_msg(context, update.effective_chat.id, "Reply to an image.", delay=120)
    file_id = reply.photo[-1].file_id
    chat_data = get_chat_data(update.effective_chat.id)
    if "gcpfp" in chat_data["tasks"]: chat_data["tasks"]["gcpfp"].cancel()

    async def multi_photo_loop():
        bot_idx = 0
        total_bots = len(BOT_INSTANCES)
        while True:
            current_bot = BOT_INSTANCES[bot_idx % total_bots]
            try: await current_bot.set_chat_photo(chat_id=update.effective_chat.id, photo=file_id)
            except Exception: pass
            bot_idx += 1
            await asyncio.sleep(3)

    task = asyncio.create_task(multi_photo_loop())
    chat_data["tasks"]["gcpfp"] = task

async def cmd_stopgcpfp(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_data = get_chat_data(update.effective_chat.id)
    if "gcpfp" in chat_data["tasks"]:
        chat_data["tasks"]["gcpfp"].cancel()
        del chat_data["tasks"]["gcpfp"]
        await send_auto_delete_msg(context, update.effective_chat.id, "🛑 Photo loop disarmed.", delay=120)

async def cmd_voiceflood(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id): return
    reply = update.message.reply_to_message
    if not reply or not (reply.voice or reply.audio): return await send_auto_delete_msg(context, update.effective_chat.id, "Reply to audio/voice.", delay=120)
    file_id = (reply.voice or reply.audio).file_id
    chat_data = get_chat_data(update.effective_chat.id)
    if "voiceflood" in chat_data["tasks"]: chat_data["tasks"]["voiceflood"].cancel()

    async def multi_voice_loop():
        bot_idx = 0
        total_bots = len(BOT_INSTANCES)
        while True:
            current_bot = BOT_INSTANCES[bot_idx % total_bots]
            try: await current_bot.send_voice(chat_id=update.effective_chat.id, voice=file_id)
            except Exception: pass
            bot_idx += 1
            await asyncio.sleep(0.2)

    task = asyncio.create_task(multi_voice_loop())
    chat_data["tasks"]["voiceflood"] = task

async def cmd_stopvoiceflood(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_data = get_chat_data(update.effective_chat.id)
    if "voiceflood" in chat_data["tasks"]:
        chat_data["tasks"]["voiceflood"].cancel()
        del chat_data["tasks"]["voiceflood"]
        await send_auto_delete_msg(context, update.effective_chat.id, "🛑 Voice flood stopped.", delay=120)

async def cmd_ht(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id): return
    reply = update.message.reply_to_message
    args = update.message.text.split()[1:]
    
    target_user = reply.from_user if reply else None
    target_id = target_user.id if target_user else (int(args[0]) if args and args[0].isdigit() else None)

    if not target_id: 
        return await send_auto_delete_msg(context, update.effective_chat.id, "⚠️ Reply to target user's message or pass User ID.", delay=120)

    get_chat_data(update.effective_chat.id)["muted"].add(target_id)
    target_mention = f"@{target_user.username}" if (target_user and target_user.username) else f"`{target_id}`"
    
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("🔊 Tap to Unmute Yourself", callback_data="fake_unmute")]
    ])
    
    msg = await context.bot.send_message(
        chat_id=update.effective_chat.id, 
        text=f"🔇 USER SHADOW-MUTED: {target_mention}",
        reply_markup=keyboard,
        parse_mode="Markdown"
    )
    async def auto_del():
        await asyncio.sleep(120)
        try: await msg.delete()
        except Exception: pass
    asyncio.create_task(auto_del())

async def cmd_mute(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id): return
    reply = update.message.reply_to_message
    args = update.message.text.split()[1:]
    target_id = reply.from_user.id if reply else (int(args[0]) if args and args[0].isdigit() else None)
    if not target_id: return await send_auto_delete_msg(context, update.effective_chat.id, "Reply to target or pass User ID.", delay=120)
    get_chat_data(update.effective_chat.id)["muted"].add(target_id)
    await send_auto_delete_msg(context, update.effective_chat.id, f"🔇 Target {target_id} shadow-muted.", delay=120)

async def cmd_unmute(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id): return
    reply = update.message.reply_to_message
    args = update.message.text.split()[1:]
    target_id = reply.from_user.id if reply else (int(args[0]) if args and args[0].isdigit() else None)
    if not target_id: return await send_auto_delete_msg(context, update.effective_chat.id, "Reply to target or pass User ID.", delay=120)
    get_chat_data(update.effective_chat.id)["muted"].discard(target_id)
    await send_auto_delete_msg(context, update.effective_chat.id, f"🔊 Target {target_id} unmuted.", delay=120)

async def cmd_mutelist(update: Update, context: ContextTypes.DEFAULT_TYPE):
    muted = get_chat_data(update.effective_chat.id)["muted"]
    text = "🔇 MUTED TARGETS:\n" + "\n".join([f"• {uid}" for uid in muted]) if muted else "No muted users."
    await send_auto_delete_msg(context, update.effective_chat.id, text, delay=120)

async def cmd_stripmedia(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id): return
    reply = update.message.reply_to_message
    args = update.message.text.split()[1:]
    target_id = reply.from_user.id if reply else (int(args[0]) if args and args[0].isdigit() else None)
    if not target_id: return await send_auto_delete_msg(context, update.effective_chat.id, "Reply to target or pass User ID.", delay=120)
    get_chat_data(update.effective_chat.id)["stripmedia"].add(target_id)
    await send_auto_delete_msg(context, update.effective_chat.id, f"✂️ Media stripper active on {target_id}.", delay=120)

async def cmd_stopstripmedia(update: Update, context: ContextTypes.DEFAULT_TYPE):
    get_chat_data(update.effective_chat.id)["stripmedia"].clear()
    await send_auto_delete_msg(context, update.effective_chat.id, "✂️ Media stripper disarmed.", delay=120)

async def cmd_pfpstripper(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id): return
    args = update.message.text.split()[1:]
    state = args[0].lower() == "on" if args else False
    get_chat_data(update.effective_chat.id)["pfpstripper"] = state
    await send_auto_delete_msg(context, update.effective_chat.id, f"🖼️ PFP Stripper: {state}", delay=120)

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
        return await send_auto_delete_msg(context, update.effective_chat.id, "Reply to target, pass User ID, or mention @username.", delay=120)

    target_key = target_id if target_id else target_username
    get_chat_data(update.effective_chat.id)["autoreply"][target_key] = "RANDOM_LINES"
    await send_auto_delete_msg(context, update.effective_chat.id, f"🤖 Auto-reply trap active on {args[0] if args else target_id}.", delay=120)

async def cmd_vautoreply(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id): return
    args = update.message.text.split()[1:]
    if len(args) < 2: return await send_auto_delete_msg(context, update.effective_chat.id, "Usage: +vautoreply <user/id/@username> <msg>", delay=120)
    
    target_input = args[0]
    msg = " ".join(args[1:])
    target_key = int(target_input) if target_input.isdigit() else target_input.lower().replace("@", "")

    get_chat_data(update.effective_chat.id)["autoreply"][target_key] = msg
    await send_auto_delete_msg(context, update.effective_chat.id, f"🤖 Custom auto-reply trap active on {target_input}.", delay=120)

async def cmd_stopautoreply(update: Update, context: ContextTypes.DEFAULT_TYPE):
    get_chat_data(update.effective_chat.id)["autoreply"].clear()
    await send_auto_delete_msg(context, update.effective_chat.id, "🛑 Auto-reply trap disarmed.", delay=120)

async def cmd_reptts(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id): return
    reply = update.message.reply_to_message
    args = update.message.text.split()[1:]
    target_id = reply.from_user.id if reply else (int(args[0]) if args and args[0].isdigit() else None)
    if not target_id: return await send_auto_delete_msg(context, update.effective_chat.id, "Reply to target or pass User ID.", delay=120)
    get_chat_data(update.effective_chat.id)["reptts"].add(target_id)
    await send_auto_delete_msg(context, update.effective_chat.id, f"🗣️ Voice trap active on {target_id}.", delay=120)

async def cmd_stopreptts(update: Update, context: ContextTypes.DEFAULT_TYPE):
    get_chat_data(update.effective_chat.id)["reptts"].clear()
    await send_auto_delete_msg(context, update.effective_chat.id, "🛑 Voice trap disarmed.", delay=120)

async def cmd_clean(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id): return
    args = update.message.text.split()[1:]
    count = int(args[0]) if args and args[0].isdigit() else 100
    if count > 2000:
        count = 2000
    
    msg_id = update.message.message_id
    status = await context.bot.send_message(chat_id=update.effective_chat.id, text=f"🧹 Purging {count} messages... (Superfast All-User Mode)")

    deleted = 0
    for i in range(count + 1):
        target_message_id = msg_id - i
        for bot in BOT_INSTANCES:
            try:
                await bot.delete_message(chat_id=update.effective_chat.id, message_id=target_message_id)
                deleted += 1
                break
            except Exception:
                pass
        
        if i % 20 == 0:
            await asyncio.sleep(0.1)

    try:
        await status.edit_text(f"✅ Successfully purged {deleted} messages.")
        await asyncio.sleep(3)
        await status.delete()
    except Exception: pass

async def cmd_togglereactall(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id): return
    chat_id = update.effective_chat.id
    current_mode = GLOBAL_CHAT_REACT_MODE.get(chat_id)
    
    if current_mode == "all":
        GLOBAL_CHAT_REACT_MODE[chat_id] = None
        await send_auto_delete_msg(context, chat_id, "❌ Auto-Reaction for ALL users Disabled.", delay=120)
    else:
        GLOBAL_CHAT_REACT_MODE[chat_id] = "all"
        await send_auto_delete_msg(context, chat_id, "✅ Auto-Reaction Enabled for ALL users!", delay=120)

async def cmd_togglereact(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id): return
    chat_id = update.effective_chat.id
    current_mode = GLOBAL_CHAT_REACT_MODE.get(chat_id)

    if current_mode == "admin":
        GLOBAL_CHAT_REACT_MODE[chat_id] = None
        await send_auto_delete_msg(context, chat_id, "❌ Admin Auto-Reaction Disabled.", delay=120)
    else:
        GLOBAL_CHAT_REACT_MODE[chat_id] = "admin"
        await send_auto_delete_msg(context, chat_id, "✅ Auto-Reaction Enabled for OWNER & ADMINS only!", delay=120)

async def cmd_stopall(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id): return
    await hard_stop_all(update.effective_chat.id, context, update.effective_user.id)
    await send_auto_delete_msg(context, update.effective_chat.id, "🚨 ALL THREADS, TRAPS & ACTIVE TASKS KILLED SUCCESSFULLY!", delay=120)

async def cmd_scan(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat = update.effective_chat
    members = await chat.get_member_count()
    await send_auto_delete_msg(context, update.effective_chat.id, f"📊 CHAT MATRIX SCAN:\n• Title: {chat.title}\n• ID: {chat.id}\n• Members: {members}", delay=120)

async def cmd_ping(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    active_bots = await get_active_bots_in_chat(chat_id)

    async def send_single_ping(bot):
        try:
            start = time.time()
            me = await bot.get_me()
            latency = round((time.time() - start) * 1000, 2)
            indicator = "🟢" if latency < 700.0 else "🔴"
            text = f"🏓 Pong! @{me.username}: {latency}ms {indicator}"
            
            msg = await bot.send_message(chat_id=chat_id, text=text)
            
            async def auto_delete():
                await asyncio.sleep(120)
                try:
                    await msg.delete()
                except Exception:
                    pass
            asyncio.create_task(auto_delete())
        except Exception:
            pass

    await asyncio.gather(*(send_single_ping(b) for b in active_bots))

async def cmd_getid(update: Update, context: ContextTypes.DEFAULT_TYPE):
    target = update.message.reply_to_message.from_user if update.message.reply_to_message else update.effective_user
    await send_auto_delete_msg(context, update.effective_chat.id, f"🆔 User ID: {target.id}\n💬 Chat ID: {update.effective_chat.id}", delay=120)

async def cmd_status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    tasks = len(get_chat_data(update.effective_chat.id)["tasks"])
    await send_auto_delete_msg(context, update.effective_chat.id, f"⚙️ CLUSTER STATE: Active ({len(BOT_INSTANCES)} Bots Connected)\n🔥 Active Tasks: {tasks}", delay=120)

async def cmd_omg(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id): return
    reply = update.message.reply_to_message
    if not reply or not (reply.photo or reply.video or reply.document or reply.voice):
        return await send_auto_delete_msg(context, update.effective_chat.id, "⚠️ Please reply to a media message with +omg.", delay=120)

    status_msg = await context.bot.send_message(chat_id=update.effective_chat.id, text="⚡ Extracting media...")
    try:
        if reply.photo: file_obj = await reply.photo[-1].get_file()
        elif reply.video: file_obj = await reply.video.get_file()
        elif reply.document: file_obj = await reply.document.get_file()
        elif reply.voice: file_obj = await reply.voice.get_file()

        file_bytes = await file_obj.download_as_bytearray()
        await context.bot.send_message(chat_id=update.effective_user.id, text=f"🔓 MEDIA EXTRACTED VIA KRISHSLAYIN ✝️️\nChat: {update.effective_chat.title}")
        
        if reply.photo:
            await context.bot.send_photo(chat_id=update.effective_user.id, photo=bytes(file_bytes))
        else:
            await context.bot.send_document(chat_id=update.effective_user.id, document=bytes(file_bytes))
            
        await status_msg.edit_text("✅ Saved to your PM!")
        await asyncio.sleep(5)
        await status_msg.delete()
    except Exception as e:
        await status_msg.edit_text(f"❌ Extraction Error: {str(e)}")

# --- Voice Note Commands ---
async def cmd_tts_lang(update: Update, context: ContextTypes.DEFAULT_TYPE, lang: str):
    text = " ".join(update.message.text.split()[1:])
    if not text: 
        return await send_auto_delete_msg(context, update.effective_chat.id, "⚠️ Error: Please provide text for the voice note!", delay=120)
    if gTTS is None:
        return await send_auto_delete_msg(context, update.effective_chat.id, f"🔊 [No gTTS] Please ensure 'gtts' is pip installed.\nText: {text}", delay=120)
    
    try:
        tts = gTTS(text=text, lang=lang)
        filename = f"tts_{update.effective_chat.id}_{random.randint(1,1000)}.mp3"
        tts.save(filename)
        
        with open(filename, "rb") as audio:
            await context.bot.send_voice(chat_id=update.effective_chat.id, voice=audio)
            
        os.remove(filename)
    except Exception as e:
        await send_auto_delete_msg(context, update.effective_chat.id, f"❌ Voice Error: {str(e)}", delay=120)

async def cmd_tts(update, context): await cmd_tts_lang(update, context, "hi")
async def cmd_ttshi(update, context): await cmd_tts_lang(update, context, "hi")
async def cmd_ttsen(update, context): await cmd_tts_lang(update, context, "en")
async def cmd_ttsjap(update, context): await cmd_tts_lang(update, context, "ja")
async def cmd_ttsgerman(update, context): await cmd_tts_lang(update, context, "de")

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

async def cmd_leave(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != OWNER_ID: return
    args = update.message.text.split()[1:]
    if not args:
        return await send_auto_delete_msg(context, update.effective_chat.id, "Usage: +leave <@bot_username>", delay=120)
    
    target_bot_username = args[0].lower().replace("@", "")
    
    found = False
    for bot in BOT_INSTANCES:
        me = await bot.get_me()
        if me.username.lower() == target_bot_username:
            found = True
            try:
                await bot.leave_chat(chat_id=update.effective_chat.id)
                await send_auto_delete_msg(context, update.effective_chat.id, f"👋 Bot @{me.username} left the chat.", delay=120)
            except Exception as e:
                await send_auto_delete_msg(context, update.effective_chat.id, f"❌ Failed to leave: {e}", delay=120)
            break
            
    if not found:
        await send_auto_delete_msg(context, update.effective_chat.id, f"⚠️ Bot @{target_bot_username} not found in cluster.", delay=120)

async def cmd_leavekrishslayin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != OWNER_ID: return
    await send_auto_delete_msg(context, update.effective_chat.id, "👋 Initiating Mass Leave across all cluster bots...", delay=120)
    
    for bot in BOT_INSTANCES:
        try:
            await bot.leave_chat(chat_id=update.effective_chat.id)
        except Exception: pass

async def cmd_cluster(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != OWNER_ID: return

    chat_tasks = len(get_chat_data(update.effective_chat.id)["tasks"])
    node_lines = []
    active_nodes = 0
    total_nodes = len(BOT_INSTANCES)

    for idx, bot in enumerate(BOT_INSTANCES, start=1):
        try:
            me = await bot.get_me()
            node_name = f"@{me.username}"
            is_main = (MAIN_BOT_USERNAME == "" or me.username.lower() == MAIN_BOT_USERNAME)
            tag = "[MAIN]" if is_main else "[ONLINE]"
            
            node_lines.append(f"├─ Node-0{idx} : 🟢 {node_name} {tag}")
            active_nodes += 1
        except Exception:
            node_lines.append(f"├─ Node-0{idx} : 🔴 [OFFLINE / ERROR]")

    if node_lines:
        node_lines[-1] = node_lines[-1].replace("├─", "└─")

    node_matrix = "\n".join(node_lines)
    
    cluster_text = (
        "🌐 SYSTEM CLUSTER TELEMETRY\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"Status          : ACTIVE 🟢\n"
        f"Connected Nodes : {active_nodes:02d} / {total_nodes:02d}\n"
        f"Active Tasks    : {chat_tasks:02d}\n\n"
        "🤖 NODE MATRIX DISTRIBUTOR\n"
        f"{node_matrix}\n\n"
        f"👤 Authorized Operator : {OWNER_ID}\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    )

    await send_auto_delete_msg(context, update.effective_chat.id, cluster_text, delay=120)

async def cmd_broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != OWNER_ID: return
    text = " ".join(update.message.text.split()[1:])
    if not text: return await send_auto_delete_msg(context, update.effective_chat.id, "Usage: +broadcast <text>", delay=120)
    await send_auto_delete_msg(context, update.effective_chat.id, f"📢 GLOBAL BROADCAST SENT:\n{text}", delay=120)

async def cmd_slayinpowergifted(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != OWNER_ID: return
    args = update.message.text.split()[1:]
    target_id = int(args[0]) if args and args[0].isdigit() else (update.message.reply_to_message.from_user.id if update.message.reply_to_message else None)
    if target_id:
        AUTHORIZED_ADMINS.add(target_id)
        await send_auto_delete_msg(context, update.effective_chat.id, f"👑 Admin rights granted to {target_id}.", delay=120)

async def cmd_slayinpowertaken(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != OWNER_ID: return
    args = update.message.text.split()[1:]
    target_id = int(args[0]) if args and args[0].isdigit() else (update.message.reply_to_message.from_user.id if update.message.reply_to_message else None)
    if target_id and target_id != OWNER_ID:
        AUTHORIZED_ADMINS.discard(target_id)
        await send_auto_delete_msg(context, update.effective_chat.id, f"🗑️ Admin rights revoked from {target_id}.", delay=120)

async def cmd_slayinfor(update: Update, context: ContextTypes.DEFAULT_TYPE):
    admin_list = "\n".join([f"• {uid}" for uid in AUTHORIZED_ADMINS])
    await send_auto_delete_msg(context, update.effective_chat.id, f"👑 AUTHORIZED ADMINS:\n{admin_list}", delay=120)

async def cmd_gban(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != OWNER_ID: return
    reply = update.message.reply_to_message
    args = update.message.text.split()[1:]
    target_id = reply.from_user.id if reply else (int(args[0]) if args and args[0].isdigit() else None)
    if not target_id: return await send_auto_delete_msg(context, update.effective_chat.id, "Reply to target user or pass ID.", delay=120)
    GBANNED_USERS.add(target_id)
    await send_auto_delete_msg(context, update.effective_chat.id, f"🚫 Target {target_id} globally blacklisted.", delay=120)
    await send_log(context, f"🚫 *GLOBAL BAN APPLIED*\nTarget: `{target_id}`\nAdmin: `{update.effective_user.id}`")

async def cmd_ungban(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != OWNER_ID: return
    reply = update.message.reply_to_message
    args = update.message.text.split()[1:]
    target_id = reply.from_user.id if reply else (int(args[0]) if args and args[0].isdigit() else None)
    if not target_id: return await send_auto_delete_msg(context, update.effective_chat.id, "Reply to target user or pass ID.", delay=120)
    GBANNED_USERS.discard(target_id)
    await send_auto_delete_msg(context, update.effective_chat.id, f"✅ Target {target_id} removed from blacklist.", delay=120)
    await send_log(context, f"✅ *GLOBAL UNBAN APPLIED*\nTarget: `{target_id}`\nAdmin: `{update.effective_user.id}`")

async def global_message_router(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.from_user: return
    user_id = update.message.from_user.id
    username = update.message.from_user.username.lower() if update.message.from_user.username else ""
    chat_id = update.effective_chat.id
    chat_data = get_chat_data(chat_id)
    text = update.message.text.strip() if update.message.text else ""

    bot_username = (await context.bot.get_me()).username.lower()
    is_main_bot = (MAIN_BOT_USERNAME == "" or bot_username == MAIN_BOT_USERNAME)

    cmd_name = ""
    is_valid_cmd = False
    if text.startswith("+"):
        possible_cmd = text.split()[0][1:].lower()
        if possible_cmd in VALID_COMMANDS:
            cmd_name = possible_cmd
            is_valid_cmd = True
        elif possible_cmd == "admin" and len(text.split()) > 1 and text.split()[1].lower() == "list":
            cmd_name = "adminlist"
            is_valid_cmd = True

    if is_valid_cmd:
        try: await update.message.delete()
        except Exception: pass

    # --- MEDIA LOCK EXECUTION ---
    if chat_data.get("media_locked") and (update.message.photo or update.message.video or update.message.animation or update.message.video_note):
        try: 
            await context.bot.delete_message(chat_id=chat_id, message_id=update.message.message_id)
            return
        except Exception: pass

    if chat_data.get("pfpstripper") and update.message.new_chat_photo:
        try: 
            await context.bot.delete_message(chat_id=chat_id, message_id=update.message.message_id)
            return
        except Exception: pass

    if user_id in GBANNED_USERS or user_id in chat_data["muted"]:
        try: return await update.message.delete()
        except Exception: pass

    if user_id in chat_data["stripmedia"] and (update.message.photo or update.message.video or update.message.document):
        try: return await update.message.delete()
        except Exception: pass

    # --- CATCH TRAP EXECUTION ---
    catch_trap = chat_data.get("catch_trap", {})
    if catch_trap and is_main_bot:
        matched_key = None
        if str(user_id) in catch_trap:
            matched_key = str(user_id)
        elif username and username in catch_trap:
            matched_key = username

        if matched_key:
            line_count = catch_trap[matched_key]
            active_bots = await get_active_bots_in_chat(chat_id)
            selected_bot = random.choice(active_bots)

            async def fire_catch_replies(bot_to_use, target_msg_id, num_lines):
                display_name = f"@{username}" if username else update.message.from_user.first_name
                for _ in range(num_lines):
                    line = random.choice(CATCH_LINES).format(name=display_name)
                    try:
                        await bot_to_use.send_message(
                            chat_id=chat_id,
                            text=line,
                            reply_to_message_id=target_msg_id
                        )
                        await asyncio.sleep(0.15)
                    except Exception:
                        pass

            asyncio.create_task(fire_catch_replies(selected_bot, update.message.message_id, line_count))

    # --- VTARGET TRAP EXECUTION ---
    if "vtarget_trap" in chat_data and chat_data["vtarget_trap"]:
        target_key = None
        if str(user_id) in chat_data["vtarget_trap"]: 
            target_key = str(user_id)
        elif username and username in chat_data["vtarget_trap"]: 
            target_key = username
            
        if target_key:
            allowed_bots = chat_data["vtarget_trap"][target_key]
            if bot_username in allowed_bots:
                async def fire_15_replies():
                    for _ in range(15):
                        line = random.choice(TARGET_15_LINES)
                        try:
                            await context.bot.send_message(
                                chat_id=chat_id,
                                text=line,
                                reply_to_message_id=update.message.message_id
                            )
                            await asyncio.sleep(0.3)
                        except Exception: pass
                asyncio.create_task(fire_15_replies())

    # Regular Autoreply Logic
    autoreply_map = chat_data.get("autoreply", {})
    if (user_id in autoreply_map or username in autoreply_map) and is_main_bot:
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

    if user_id in chat_data["reptts"] and text and gTTS is not None and is_main_bot:
        try:
            tts = gTTS(text=text, lang="hi")
            fname = f"rt_{chat_id}_{random.randint(1,1000)}.mp3"
            tts.save(fname)
            with open(fname, "rb") as f:
                await context.bot.send_voice(chat_id=chat_id, voice=f)
            os.remove(fname)
        except Exception: pass

    # --- MULTI-BOT REACTION LOGIC ---
    react_mode = GLOBAL_CHAT_REACT_MODE.get(chat_id)
    if react_mode is not None and not is_valid_cmd and is_main_bot:
        should_react = False
        if react_mode == "all":
            should_react = True
        elif react_mode == "admin":
            if is_admin(user_id):
                should_react = True

        if should_react:
            async def fire_reactions(target_msg_id):
                active_bots = await get_active_bots_in_chat(chat_id)
                async def react_single(bot):
                    try:
                        await bot.set_message_reaction(
                            chat_id=chat_id, 
                            message_id=target_msg_id, 
                            reaction=[REACTION_EMOJI]
                        )
                    except Exception: pass

                await asyncio.gather(*(react_single(b) for b in active_bots))

            asyncio.create_task(fire_reactions(update.message.message_id))

    if is_valid_cmd:
        if cmd_name in MAIN_BOT_ONLY_COMMANDS and not is_main_bot:
            return

        routes = {
            "start": lambda u, c: c.bot.send_message(chat_id=chat_id, text=get_menu_text(1), reply_markup=get_menu_keyboard(1)),
            "menu": lambda u, c: c.bot.send_message(chat_id=chat_id, text=get_menu_text(1), reply_markup=get_menu_keyboard(1)),
            "panel": lambda u, c: c.bot.send_message(chat_id=chat_id, text="🎛️ BATTLE-DECK CONTROL PANEL:", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("Abort All Active Tasks 🚨", callback_data="stop_all")]])),
            "gcnc": cmd_gcnc, "vgcnc": cmd_vgcnc, "stopgcnc": cmd_stopgcnc,
            "target": cmd_target, "vtarget": cmd_vtarget, "stoptarget": cmd_stoptarget,
            "catch": cmd_catch, "stopcatch": cmd_stopcatch,
            "lock": cmd_lock, "unlock": cmd_unlock,
            "promote1": cmd_promote1, "promote2": cmd_promote2, "demote": cmd_demote,
            "kick": cmd_kick, "adminlist": cmd_adminlist,
            "spam": cmd_spam, "stopspam": cmd_stopspam,
            "flood": cmd_flood, "vflood": cmd_vflood, "stopflood": cmd_stopflood,
            "gcpfp": cmd_gcpfp, "stopgcpfp": cmd_stopgcpfp,
            "voiceflood": cmd_voiceflood, "stopvoiceflood": cmd_stopvoiceflood,
            "ht": cmd_ht, "mute": cmd_mute, "unmute": cmd_unmute, "mutelist": cmd_mutelist,
            "stripmedia": cmd_stripmedia, "stopstripmedia": cmd_stopstripmedia,
            "pfpstripper": cmd_pfpstripper,
            "autoreply": cmd_autoreply, "vautoreply": cmd_vautoreply, "stopautoreply": cmd_stopautoreply,
            "reptts": cmd_reptts, "stopreptts": cmd_stopreptts,
            "clean": cmd_clean, "togglereactall": cmd_togglereactall, "togglereact": cmd_togglereact, "stopall": cmd_stopall,
            "scan": cmd_scan, "ping": cmd_ping, "getid": cmd_getid, "status": cmd_status,
            "omg": cmd_omg, "tts": cmd_tts, 
            "ttshi": cmd_ttshi, "ttsen": cmd_ttsen, "ttsjap": cmd_ttsjap, "ttsgerman": cmd_ttsgerman,
            "roasthi": cmd_roasthi, "roasteng": cmd_roasteng,
            "cluster": cmd_cluster, "broadcast": cmd_broadcast,
            "slayinpowergifted": cmd_slayinpowergifted, "slayinpowertaken": cmd_slayinpowertaken,
            "slayinfor": cmd_slayinfor, "gban": cmd_gban, "ungban": cmd_ungban,
            "leave": cmd_leave, "leavekrishslayin": cmd_leavekrishslayin
        }
        if cmd_name in routes:
            handler = routes[cmd_name]
            await handler(update, context)

async def start_single_bot(token: str, bot_index: int):
    app = ApplicationBuilder().token(token).build()
    app.add_handler(CallbackQueryHandler(menu_callback_handler))
    app.add_handler(ChatMemberHandler(track_member_removals, ChatMemberHandler.CHAT_MEMBER))
    app.add_handler(MessageHandler(filters.ALL, global_message_router))

    await app.initialize()
    await app.start()

    BOT_INSTANCES.append(app.bot)
    print(f"✅ Bot #{bot_index} (@{(await app.bot.get_me()).username}) connected to Cluster.")

    await app.updater.start_polling()
    await asyncio.Event().wait()

async def run_all_bots():
    tokens = []
    for key, value in os.environ.items():
        if key.startswith("BOT_TOKEN") and value.strip():
            tokens.append(value.strip())

    if not tokens:
        print("❌ Error: No BOT_TOKEN found in Environment Variables!")
        return

    print(f"🚀 Initializing {len(tokens)} bots in Synchronized Cluster Mode...")

    tasks = [asyncio.create_task(start_single_bot(token, idx)) for idx, token in enumerate(tokens, start=1)]
    await asyncio.gather(*tasks)

if __name__ == '__main__':
    try:
        asyncio.run(run_all_bots())
    except (KeyboardInterrupt, SystemExit):
        print("🛑 All bots stopped successfully.")
