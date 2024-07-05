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
import aiohttp  # Import aiohttp for asynchronous downloads
import os

os.environ['REQUESTS_CA_BUNDLE'] = certifi.where()

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
from plugins.thumbnail import *
# from plugins.directlink import process_file #  Removing directlink feature
from pyrogram.types import Thumbnail, Message

from pyrogram import Client, filters, enums, types  # Import filters, enums, and types

@Client.on_message(filters.private)  # Use filters.private for private chats
async def handle_user_input(bot: Client, update: Message):
    """Handles different types of user input."""

    if not update.from_user:
        return await update.reply_text("Sorry, I couldn't process your request. Please try again.")

    await add_user_to_database(bot, update)

    # if Config.UPDATES_CHANNEL:  # Force subscribe will be handled in Phase 2
    #   fsub = await handle_force_subscribe(bot, update)
    #   if fsub == 400:
    #       return

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

    # elif update.forward_from:
    #     # Handle forwarded files (commented out to remove direct link feature)
    #     if update.forward_from.is_bot:
    #         return  # Ignore forwarded files from bots
    #     if update.forward_from.id == Config.OWNER_ID:
    #         return  # Ignore forwarded files from the bot's owner
    #     # await process_file(bot, update)

    else:
        await update.reply_text("I don't understand this input type. Please provide a URL or a magnet link.")


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

    # ----- Direct Link Processing Logic ------
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
            error_message = e_response.replace(
                "please report this issue on https://yt-dl.org/bug . Make sure you are using the latest version; see  https://yt-dl.org/update  on how to update. Be sure to call youtube-dl with the --verbose flag and include its complete output.",
                "")
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

            # **Extract direct download URL:**
            direct_download_url = response_json.get('url')

            if direct_download_url:
                randem = random_char(5)
                # ... (rest of your file saving and upload logic)
                custom_file_name = file_name or response_json.get('title')
                tmp_directory_for_each_user = os.path.join(Config.DOWNLOAD_LOCATION, f"{update.from_user.id}{randem}")
                os.makedirs(tmp_directory_for_each_user, exist_ok=True)
                download_directory = os.path.join(tmp_directory_for_each_user, custom_file_name)

                await update.reply_text(f"Downloading: `{custom_file_name}`")

                # Download the file using aiohttp:
                async with aiohttp.ClientSession() as session:
                    async with session.get(direct_download_url) as response:
                        if response.status == 200:
                            total_size = int(response.headers.get("content-length", 0)) or None
                            with open(download_directory, "wb") as file:
                                async for data in response.content.iter_chunked(1024 * 1024):  # 1MB chunks
                                    file.write(data)

                                    # Update progress every 5%
                                    if total_size:
                                        downloaded_size = os.path.getsize(download_directory)
                                        percentage = (downloaded_size / total_size) * 100
                                        if int(percentage) % 5 == 0:
                                            await update.edit_text(
                                                f"Downloading: `{custom_file_name}`\n"
                                                f"Progress: {int(percentage)}%"
                                            )
                # ----------------------- Upload Logic -----------------------
                await update.reply_text(f"Downloaded to my server!\nNow uploading to Telegram...")
                start_time = time.time()

                if os.path.isfile(download_directory):
                    file_size = os.stat(download_directory).st_size
                else:
                    download_directory = os.path.splitext(download_directory)[0] + ".mkv"
                    if os.path.isfile(download_directory):
                        file_size = os.stat(download_directory).st_size
                    else:
                        await update.reply_text(f"Downloaded file not found: {download_directory}")
                        return

                if file_size > Config.TG_MAX_FILE_SIZE:
                    await update.reply_text(
                        f"File is too large for Telegram! ({humanbytes(file_size)} > {humanbytes(Config.TG_MAX_FILE_SIZE)})"
                    )
                    return

                # Upload as stream if file is large (updated to 1.5GB)
                if file_size > 1610612736:
                    with open(download_directory, "rb") as f:
                        await update.reply_document(
                            document=f,
                            caption=Translation.CUSTOM_CAPTION_UL_FILE,
                            parse_mode=enums.ParseMode.HTML,
                            progress=progress_for_pyrogram,
                            progress_args=(
                                Translation.UPLOAD_START,
                                update,
                                start_time
                            )
                        )
                else:
                    # Normal upload for smaller files
                    if not await db.get_upload_as_doc(update.from_user.id):
                        thumbnail = await Gthumb01(bot, update)
                        await update.reply_document(
                            document=download_directory,
                            thumb=thumbnail,
                            caption=Translation.CUSTOM_CAPTION_UL_FILE,
                            parse_mode=enums.ParseMode.HTML,
                            progress=progress_for_pyrogram,
                            progress_args=(
                                Translation.UPLOAD_START,
                                update,
                                start_time
                            )
                        )
                    else:
                        width, height, duration = await Mdata01(download_directory)
                        thumb_image_path = await Gthumb02(bot, update, duration, download_directory)
                        await update.reply_video(
                            video=download_directory,
                            caption=Translation.CUSTOM_CAPTION_UL_FILE,
                            duration=duration,
                            width=width,
                            height=height,
                            supports_streaming=True,
                            parse_mode=enums.ParseMode.HTML,
                            thumb=thumb_image_path,
                            progress=progress_for_pyrogram,
                            progress_args=(
                                Translation.UPLOAD_START,
                                update,
                                start_time
                            )
                        )

                # Cleanup after upload
                try:
                    shutil.rmtree(tmp_directory_for_each_user)
                    if thumbnail:  # Delete thumbnail if it exists
                        os.remove(thumbnail)
                except Exception as e:
                    logger.error(f"Error cleaning up: {e}")

                # Success message
                end_two = datetime.now()
                time_taken_for_upload = (end_two - end_one).seconds
                await update.reply_text(
                    text=Translation.AFTER_SUCCESSFUL_UPLOAD_MSG_WITH_TS.format(
                        time_taken_for_download, time_taken_for_upload),
                    parse_mode=enums.ParseMode.HTML,
                    disable_web_page_preview=True
                )

            else:
                await update.reply_text("Direct download URL not found in the response.")
                return

        # ... (Rest of your error handling code)

    except Exception as e:  # Correct indentation
        logger.error(f"An error occurred: {e}")
        await chk.delete()
        await bot.send_message(
            chat_id=update.chat.id,
            text=f"**Error:** {e}",
            reply_to_message_id=update.id,
            parse_mode=enums.ParseMode.MARKDOWN
        )
