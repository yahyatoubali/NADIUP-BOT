import os
import time
import psutil
import shutil
import string
import asyncio
import logging
from pyrogram import Client, filters
from asyncio import TimeoutError
from pyrogram.errors import MessageNotModified, PeerIdInvalid, ChannelPrivate
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message, CallbackQuery, ForceReply
from plugins.config import Config
from plugins.script import Translation
from plugins.database.add import add_user_to_database
from plugins.functions.forcesub import handle_force_subscribe

# Initialize logging
#logging.basicConfig(level=logging.INFO)

@Client.on_message(filters.command(["start"]) & filters.private)
async def start(bot, update):
    if not update.from_user:
        return await update.reply_text("I don't know about you sar :(")
    await add_user_to_database(bot, update)
    
#    chat_id = Config.LOG_CHANNEL
#    logging.info(f"LOG_CHANNEL: {chat_id}")
    
#    try:
        # Attempt to resolve the peer to check if the ID is valid
#        resolved_peer = await bot.resolve_peer(chat_id)
#        logging.info(f"Resolved peer ID: {resolved_peer}")
        
#        # Proceed to send the message
#        await bot.send_message(
#            chat_id=chat_id,
#            text=f"#NEW_USER: \n\nNew User [{update.from_user.first_name}](tg://user?id={update.from_user.id}) started @{Config.BOT_USERNAME} !!"
#        )
#        logging.info(f"Message sent successfully to chat ID: {chat_id}")
#    except PeerIdInvalid:
#        logging.error(f"Invalid Peer ID: {chat_id}. Please check the chat ID.")
#        await update.reply_text("Error: Invalid chat ID.")
#        return
#    except ChannelPrivate:
#        logging.error(f"Channel is private or bot is not a member: {chat_id}.")
#        await update.reply_text("Error: Channel is private or bot is not a member.")
#        return
#    except KeyError:
#        logging.error(f"ID not found in storage: {chat_id}. Ensure bot is in the channel.")
#        await update.reply_text("Error: ID not found in storage. Ensure bot is in the channel.")
#        return
#    except Exception as e:
#        logging.error(f"Unexpected error: {e}")
#        await update.reply_text("An unexpected error occurred.")
#        return

#    if Config.UPDATES_CHANNEL:
#        fsub = await handle_force_subscribe(bot, update)
#        if fsub == 400:
#            return

    await update.reply_text(
        text=Translation.START_TEXT.format(update.from_user.mention),
        disable_web_page_preview=True,
        reply_markup=Translation.START_BUTTONS
    )
