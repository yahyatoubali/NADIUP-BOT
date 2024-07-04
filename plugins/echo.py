# ©️ Yahya Toubali | @yahyatoubali | NT_BOT_CHANNEL

import logging
logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

import requests
import urllib.parse
import filetype
import os
import time
import shutil
import tldextract
import asyncio
import json
import math
import certifi
import os

os.environ['REQUESTS_CA_BUNDLE'] = certifi.where()

# Import necessary functions from other modules
from plugins.config import Config
from plugins.script import Translation
from plugins.torrent import torrent_download  # For torrent handling
from plugins.functions.forcesub import handle_force_subscribe
from plugins.functions.display_progress import humanbytes
from plugins.functions.help_uploadbot import DownLoadFile
from plugins.functions.display_progress import progress_for_pyrogram, humanbytes, TimeFormatter
from hachoir.metadata import extractMetadata
from hachoir.parser import createParser
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.errors import UserNotParticipant
from plugins.functions.ran_text import random_char
from plugins.database.add import add_user_to_database
from plugins.directlink import process_file  # Import process_file
from pyrogram.types import Thumbnail, Message

from pyrogram import Client, filters, enums, types

@Client.on_message(filters.private)
async def handle_user_input(bot: Client, update: Message):
    """Handles different types of user input intelligently."""

    if not update.from_user:
        return await update.reply_text("Sorry, I couldn't process your request. Please try again.")

    await add_user_to_database(bot, update)

    # Handle different input types
    if update.text:
        # 1. Handle Magnet Links
        if update.text.startswith("magnet:"):
            await torrent_download(bot, update)
            return

        # 2. Handle Direct Links (Regular URLs)
        elif update.text.startswith(("http://", "https://")):
            await process_direct_link(bot, update)
            return

    elif update.document:
        # Handle file uploads
        file_name = update.document.file_name.lower()

        # Exclude .sh files 
        if file_name.endswith(".sh"):
            await update.reply_text("Sorry, I cannot process .sh files. Please try a different file type.")
            return
        else:
            # Handle torrent files
            if file_name.endswith((".torrent", ".magnet")):
                await torrent_download(bot, update)
                return
            # Handle other files (ask for direct link)
            await ask_for_direct_link(bot, update)

    elif update.forward_from:
        # Handle forwarded files
        if update.forward_from.is_bot:
            return  # Ignore forwarded files from bots
        if update.forward_from.id == Config.OWNER_ID:
            return  # Ignore forwarded files from the bot's owner
        await process_file(bot, update)  # Call process_file to handle forwarded files

    else:
        await update.reply_text("I don't understand this input type. Please provide a URL, a magnet link, or a file.")


async def process_direct_link(bot: Client, update: Message):
    """Handles direct URLs (regular HTTP/HTTPS links)."""
    url = update.text
    youtube_dl_username = None
    youtube_dl_password = None
    file_name = None

    print(url)
    if "|" in url:
        url_parts = url.split("|")
        if len(url_parts) == 2:
            url = url_parts[0].strip()
            file_name = url_parts[1].strip()
        elif len(url_parts) == 4:
            url = url_parts[0].strip()
            file_name = url_parts[1].strip()
            youtube_dl_username = url_parts[2].strip()
            youtube_dl_password = url_parts[3].strip()
        else: 
            await update.reply_text("Invalid URL format. Please use: `link | filename.extension` or `link | filename.extension | username | password`")
            return

    # If no filename, extract it from URL
    if not file_name: 
        parsed_url = urllib.parse.urlparse(url)
        file_name = os.path.basename(parsed_url.path) 

    # ----- Rest of Direct Link Processing Logic ------

    if Config.HTTP_PROXY != "":
        command_to_exec = [
            "yt-dlp",
            "--no-warnings",
            "--youtube-skip-hls-manifest",
            "-j",
            url,
            "--proxy", Config.HTTP_PROXY
        ]
    else:
        command_to_exec = [
            "yt-dlp",
            "--no-warnings",
            "--youtube-skip-hls-manifest",
            "-j",
            url
        ]

    if youtube_dl_username is not None:
        command_to_exec.append("--username")
        command_to_exec.append(youtube_dl_username)
    if youtube_dl_password is not None:
        command_to_exec.append("--password")
        command_to_exec.append(youtube_dl_password)

    logger.info(command_to_exec)

    chk = await bot.send_message(
        chat_id=update.chat.id,
        text=Translation.CHECK_LINK,
        disable_web_page_preview=True,
        reply_to_message_id=update.id,
        parse_mode=enums.ParseMode.HTML
    )

    try:
        process = await asyncio.create_subprocess_exec(
            *command_to_exec,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        # Wait for the subprocess to finish
        stdout, stderr = await process.communicate()

        e_response = stderr.decode().strip()
        logger.info(e_response)
        t_response = stdout.decode().strip()

        if e_response and "nonnumeric port" not in e_response:
            error_message = e_response.replace("please report this issue on https://yt-dl.org/bug . Make sure you are using the latest version; see  https://yt-dl.org/update  on how to update. Be sure to call youtube-dl with the --verbose flag and include its complete output.", "")
            if "This video is only available for registered users." in error_message:
                error_message += Translation.SET_CUSTOM_USERNAME_PASSWORD
            await chk.delete()
            time.sleep(1)
            await bot.send_message(
                chat_id=update.chat.id,
                text=Translation.NO_VOID_FORMAT_FOUND.format(str(error_message)),
                reply_to_message_id=update.id,
                parse_mode=enums.ParseMode.HTML,
                disable_web_page_preview=True
            )
            return False

        if t_response:
            x_reponse = t_response
            if "\n" in x_reponse:
                x_reponse, _ = x_reponse.split("\n")
            response_json = json.loads(x_reponse)
            randem = random_char(5)
            save_ytdl_json_path = Config.DOWNLOAD_LOCATION + \
                "/" + str(update.from_user.id) + f'{randem}' + ".json"
            with open(save_ytdl_json_path, "w", encoding="utf8") as outfile:
                json.dump(response_json, outfile, ensure_ascii=False)
            inline_keyboard = []
            duration = None
            if "duration" in response_json:
                duration = response_json["duration"]
            if "formats" in response_json:
                for formats in response_json["formats"]:
                    format_id = formats.get("format_id")
                    format_string = formats.get("format_note")
                    if format_string is None:
                        format_string = formats.get("format")
                    format_ext = formats.get("ext")
                    approx_file_size = ""
                    if "filesize" in formats:
                        approx_file_size = humanbytes(formats["filesize"])
                    cb_string_video = "{}|{}|{}|{}".format(
                        "video", format_id, format_ext, randem)
                    cb_string_file = "{}|{}|{}|{}".format(
                        "file", format_id, format_ext, randem)
                    if format_string is not None and not "audio only" in format_string:
                        ikeyboard = [
                            InlineKeyboardButton(
                                f"🎬 {format_string} {format_ext} {approx_file_size} ",
                                callback_data=(cb_string_video).encode("UTF-8")
                            )
                        ]
                    else:
                        # Special weird case :
                        ikeyboard = [
                            InlineKeyboardButton(
                                f"🎬 [{format_ext}] ({approx_file_size})",
                                callback_data=(cb_string_video).encode("UTF-8")
                            )
                        ]
                    inline_keyboard.append(ikeyboard)
                if duration is not None:
                    cb_string_64 = "{}|{}|{}|{}".format("audio", "64k", "mp3", randem)
                    cb_string_128 = "{}|{}|{}|{}".format("audio", "128k", "mp3", randem)
                    cb_string = "{}|{}|{}|{}".format("audio", "320k", "mp3", randem)
                    inline_keyboard.append([
                        InlineKeyboardButton(
                            f"🎵 MP3 (64 kbps)", callback_data=cb_string_64.encode("UTF-8")),
                        InlineKeyboardButton(
                            f"🎵 MP3 (128 kbps)", callback_data=cb_string_128.encode("UTF-8"))
                    ])
                    inline_keyboard.append([
                        InlineKeyboardButton(
                            f"🎵 MP3 (320 kbps)", callback_data=cb_string.encode("UTF-8"))
                    ])
                inline_keyboard.append([                 
                    InlineKeyboardButton(
                        "⛔️ Close", callback_data='close')               
                ]) 
            else:
                format_id = response_json["format_id"]
                format_ext = response_json["ext"]
                cb_string_file = "{}|{}|{}|{}".format(
                    "file", format_id, format_ext, randem)
                cb_string_video = "{}|{}|{}|{}".format(
                    "video", format_id, format_ext, randem)
                inline_keyboard.append([
                    InlineKeyboardButton(
                        "🎬 Media",
                        callback_data=(cb_string_video).encode("UTF-8")
                    )
                ])
                inline_keyboard.append([
                    InlineKeyboardButton(
                        "🎥 Video",
                        callback_data=(cb_string_video).encode("UTF-8")
                    )
                ])
            reply_markup = InlineKeyboardMarkup(inline_keyboard)
            await chk.delete()
            await bot.send_message(
                chat_id=update.chat.id,
                text=Translation.FORMAT_SELECTION.format(Thumbnail) + "\n" + Translation.SET_CUSTOM_USERNAME_PASSWORD,
                reply_markup=reply_markup,
                parse_mode=enums.ParseMode.HTML,
                reply_to_message_id=update.id
            )
        else:
            inline_keyboard = []
            cb_string_file = "{}={}={}".format(
                "file", "LFO", "NONE")
            cb_string_video = "{}={}={}".format(
                "video", "OFL", "ENON")
            inline_keyboard.append([
                InlineKeyboardButton(
                    "🎬 Media",
                    callback_data=(cb_string_video).encode("UTF-8")
                )
            ])
            reply_markup = InlineKeyboardMarkup(inline_keyboard)
            await chk.delete()
            await bot.send_message(
                chat_id=update.chat.id,
                text=Translation.FORMAT_SELECTION,
                reply_markup=reply_markup,
                parse_mode=enums.ParseMode.HTML,
                reply_to_message_id=update.id
            )

    except Exception as e: # Correct indentation
        logger.error(f"An error occurred: {e}")
        await chk.delete()
        await bot.send_message(
            chat_id=update.chat.id,
            text=f"**Error:** {e}",
            reply_to_message_id=update.id,
            parse_mode=enums.ParseMode.MARKDOWN
        )
