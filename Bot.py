import logging
import re
import time
from telegram import Update, Bot, InlineKeyboardMarkup, InlineKeyboardButton, ParseMode
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext
from pymongo import MongoClient
from telegram.utils.helpers import escape_markdown
import html

from config import TELEGRAM_TOKEN, OWNER_ID, SUDO_ID, MONGO_URI, DB_NAME, SUPPORT_ID, API_ID, API_HASH

client = MongoClient(MONGO_URI)
db = client[DB_NAME]
users_collection = db['users']

updater = Updater(TELEGRAM_TOKEN, use_context=True)
bot = updater.bot

StartTime = time.time()

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

buttons = [
    [InlineKeyboardButton(text="ᴀᴅᴅ ᴍᴇ ʏᴏᴜʀ ɢʀᴏᴜᴩ ʙᴀʙʏ", url=f"http://t.me/EDITGUARDIANPR_OBOT?startgroup=true")],
    [InlineKeyboardButton(text="🥀 𝐔𝐏𝐃𝐀𝐓𝐄 🥀", url="https://t.me/Love_Bot_143"),
     InlineKeyboardButton(text=" 🥀𝐒𝐔𝐏𝐏𝐎𝐑𝐓 🥀", url="https://t.me/Love_familysupport")],
    [InlineKeyboardButton(text="👑 𝐎𝐖𝐍𝐄𝐑 👑", url="https://t.me/ll_WTF_SHEZADA_ll")]
]

PM_START_TEXT = """
*Hello* {}[✨]({}) 👋 I'm your 𝗘𝗱𝗶𝘁 𝗚𝘂𝗮𝗿𝗱𝗶𝗮𝗻 𝗣𝗿𝗼 𝗕𝗼𝘁, here to maintain a secure environment for our discussions.

🚫 𝗘𝗱𝗶𝘁𝗲𝗱 𝗠𝗲𝘀𝘀𝗮𝗴𝗲 𝗗𝗲𝗹𝗲𝘁𝗶𝗼𝗻: 𝗜'𝗹𝗹 𝗿𝗲𝗺𝗼𝗩𝗲 𝗲𝗱𝗶𝘁𝗲𝗱 𝗺𝗲𝘀𝘀𝗮𝗴𝗲𝘀 𝘁𝗼 𝗺𝗮𝗶𝗻𝘁𝗮𝗶𝗻 𝘁𝗿𝗮𝗻𝘀𝗽𝗮𝗿𝗲𝗻𝗰𝘆.
    
🌟 𝗚𝗲𝘁 𝗦𝘁𝗮𝗿𝘁𝗲𝗱:
1. Add me to your group.
2. I'll start protecting instantly.
    
➡️ Click on 𝗔𝗱𝗱 𝗠𝗲 𝗧𝗼 𝗬𝗼𝘂𝗿 𝗚𝗿𝗼𝘂𝗽 to add me and keep our group safe!
"""

IMG = ["https://files.catbox.moe/tk3zkl.jpg"]
PM_START_IMG = "https://files.catbox.moe/tk3zkl.jpg"

def get_readable_time(seconds: int) -> str:
    count = 0
    ping_time = ""
    time_list = []
    time_suffix_list = ["s", "m", "h", "days"]

    while count < 4:
        count += 1
        remainder, result = divmod(seconds, 60) if count < 3 else divmod(seconds, 24)
        if seconds == 0 and remainder == 0:
            break
        time_list.append(int(result))
        seconds = int(remainder)

    for x in range(len(time_list)):
        time_list[x] = str(time_list[x]) + time_suffix_list[x]
    if len(time_list) == 4:
        ping_time += time_list.pop() + ", "

    time_list.reverse()
    ping_time += ":".join(time_list)

    return ping_time

def start(update: Update, context: CallbackContext):
    args = context.args
    uptime = get_readable_time((time.time() - StartTime))
    
    user_id = update.effective_user.id
    chat_id = update.effective_chat.id
    
    if update.effective_chat.type == "private":
        if len(args) >= 1 and args[0].lower() == "help":
            send_help(update.effective_chat.id)
        else:
            first_name = update.effective_user.first_name
            update.effective_message.reply_text(
                PM_START_TEXT.format(escape_markdown(first_name), PM_START_IMG),
                reply_markup=InlineKeyboardMarkup(buttons),
                parse_mode=ParseMode.MARKDOWN,
            )
    else:
        update.effective_message.reply_photo(
            PM_START_IMG,
            reply_markup=InlineKeyboardMarkup(buttons),
            caption="ɪ ᴀᴍ ᴀʟɪᴠᴇ ʙᴀʙʏ!\n<b>ᴜᴘᴛɪᴍᴇ :</b> <code>{}</code>".format(uptime),
            parse_mode=ParseMode.HTML,
        )

def check_edit(update: Update, context: CallbackContext):
    bot: Bot = context.bot
    if update.edited_message:
        edited_message = update.edited_message
        chat_id = edited_message.chat_id
        message_id = edited_message.message_id
        user_id = edited_message.from_user.id
        user_mention = f"<a href='tg://user?id={user_id}'>{html.escape(edited_message.from_user.first_name)}</a>"
        
        if user_id not in SUDO_ID:
            bot.delete_message(chat_id=chat_id, message_id=message_id)
            bot.send_message(chat_id=chat_id, text=f"{user_mention} 𝗝𝘂𝘀𝘁 𝗘𝗱𝗶𝘁 𝗮 𝗠𝗲𝘀𝘀𝗮𝗴𝗲. 𝗜 𝗱𝗲𝗹𝗲𝘁𝗲𝗱 𝗶𝘁.", parse_mode='HTML')

def add_sudo(update: Update, context: CallbackContext):
    user = update.effective_user
    if user.id != OWNER_ID:
        update.message.reply_text("You don't have permission to perform this action.")
        return
    
    if len(context.args) != 1:
        update.message.reply_text("Usage: /addsudo <username or user ID>")
        return
    
    sudo_user = context.args[0]
    try:
        sudo_user_obj = context.bot.get_chat_member(update.effective_chat.id, sudo_user)
        sudo_user_id = sudo_user_obj.user.id
    except Exception as e:
        update.message.reply_text(f"Failed: {e}")
        return
    
    if sudo_user_id not in SUDO_ID:
        SUDO_ID.append(sudo_user_id)
        update.message.reply_text(f"Added {sudo_user_obj.user.username} as sudo user.")
    else:
        update.message.reply_text(f"{sudo_user_obj.user.username} is already a sudo user.")

def send_help(chat_id):
    bot.send_message(
        chat_id,
        text="This is your bot help message.\n\nI delete edited messages to keep conversations clean and transparent.",
    )

def main():
    dispatcher = updater.dispatcher
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(MessageHandler(Filters.update.edited_message, check_edit))
    dispatcher.add_handler(CommandHandler("addsudo", add_sudo))
    
    updater.start_polling()

if __name__ == "__main__":
    main()
