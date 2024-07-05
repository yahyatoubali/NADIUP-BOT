# ©️ Yahya Toubali | @yahyatoubali | NT_BOT_CHANNEL

import logging
logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

import requests
import urllib.parse
import os
import time
import shutil
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
from plugins.functions.display_progress import progress_for_pyrogram, humanbytes, TimeFormatter
from hachoir.metadata import extractMetadata
from hachoir.parser import createParser
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from plugins.functions.ran_text import random_char
from plugins.database.add import add_user_to_database
from plugins.thumbnail import *
from pyrogram.types import Message

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
            await NU_process_direct_link(bot, update)
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

    else:
        await update.reply_text("I don't understand this input type. Please provide a URL or a magnet link.")

# --- New Function with NU prefix ---
async def NU_process_direct_link(bot: Client, update: Message):
    """Processes direct URLs, prioritizing YouTube downloads and merging."""
    url = update.text
    youtube_dl_username = None
    youtube_dl_password = None
    file_name = None

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
            await update.reply_text(
                "Invalid URL format. Please use: `link | filename.extension` or `link | filename.extension | username | password`")
            return

    # If no filename, extract it from URL
    if not file_name:
        parsed_url = urllib.parse.urlparse(url)
        file_name = os.path.basename(parsed_url.path)

    # ----- Direct Link Processing Logic -----

    # --- Prepare yt-dlp Command ---
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
    if Config.HTTP_PROXY != "":
        command_to_exec.append("--proxy")
        command_to_exec.append(Config.HTTP_PROXY)

    logger.info(command_to_exec)

    # --- Send "Processing" Message ---
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
        stdout, stderr = await process.communicate()
        e_response = stderr.decode().strip()
        t_response = stdout.decode().strip()

        # --- Handle yt-dlp Errors ---
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
            # --- Extract Information from yt-dlp JSON Response ---
            x_reponse = t_response
            if "\n" in x_reponse:
                x_reponse, _ = x_reponse.split("\n")
            response_json = json.loads(x_reponse)

            # --- YouTube Download and Merge Logic ---
            is_youtube = response_json.get("extractor_key") == "Youtube"
            if is_youtube:
                randem = random_char(5)
                custom_file_name = file_name or response_json.get('title')
                tmp_directory_for_each_user = os.path.join(Config.DOWNLOAD_LOCATION,
                                                            f"{update.from_user.id}{randem}")
                os.makedirs(tmp_directory_for_each_user, exist_ok=True)

                video_file_path = os.path.join(tmp_directory_for_each_user, f"{custom_file_name}_video.mp4")
                audio_file_path = os.path.join(tmp_directory_for_each_user, f"{custom_file_name}_audio.m4a")
                final_file_path = os.path.join(tmp_directory_for_each_user, f"{custom_file_name}.mkv")

                await update.reply_text(f"Downloading: `{custom_file_name}`")
                start_time = time.time() # Start time for download 
                try:
                    # --- Download Video Stream ---
                    download_command = [
                        "yt-dlp",
                        "-c",
                        "-f", "bestvideo[ext=mp4]",  # Download best MP4 video
                        "--hls-prefer-ffmpeg",
                        "--no-warnings",
                        "-o", video_file_path,
                        url
                    ]
                    if Config.HTTP_PROXY:
                        download_command.extend(["--proxy", Config.HTTP_PROXY])
                    process = await asyncio.create_subprocess_exec(
                        *download_command,
                        stdout=asyncio.subprocess.PIPE,
                        stderr=asyncio.subprocess.PIPE,
                    )
                    _, stderr = await process.communicate()  # Ignore stdout for download
                    if stderr:
                        e_response = stderr.decode().strip()
                        logger.error(f"yt-dlp video download error: {e_response}")
                        await update.reply_text(f"**Error Downloading Video:** `{e_response}`")
                        return False

                    # --- Download Audio Stream ---
                    download_command = [
                        "yt-dlp",
                        "-c",
                        "-f", "bestaudio[ext=m4a]",  # Download best M4A audio
                        "--hls-prefer-ffmpeg",
                        "--no-warnings",
                        "-o", audio_file_path,
                        url
                    ]
                    if Config.HTTP_PROXY:
                        download_command.extend(["--proxy", Config.HTTP_PROXY])
                    process = await asyncio.create_subprocess_exec(
                        *download_command,
                        stdout=asyncio.subprocess.PIPE,
                        stderr=asyncio.subprocess.PIPE,
                    )
                    _, stderr = await process.communicate()  # Ignore stdout for download
                    if stderr:
                        e_response = stderr.decode().strip()
                        logger.error(f"yt-dlp audio download error: {e_response}")
                        await update.reply_text(f"**Error Downloading Audio:** `{e_response}`")
                        return False

                    # --- Merge Video and Audio using FFmpeg ---
                    merge_command = [
                        "ffmpeg",
                        "-i", video_file_path,
                        "-i", audio_file_path,
                        "-c", "copy",  # Copy codecs, avoids re-encoding
                        final_file_path
                    ]
                    process = await asyncio.create_subprocess_exec(
                        *merge_command,
                        stdout=asyncio.subprocess.PIPE,
                        stderr=asyncio.subprocess.PIPE,
                    )
                    _, stderr = await process.communicate()  # Ignore stdout for merge

                    if stderr:
                        e_response = stderr.decode().strip()
                        logger.error(f"FFmpeg merge error: {e_response}")
                        await update.reply_text(f"**Error Merging Video and Audio:** `{e_response}`")
                        return False

                    # --- Upload Merged File to Telegram ---
                    await NU_upload_to_telegram(bot, update, final_file_path, start_time)

                    # --- Cleanup Temporary Files ---
                    try:
                        os.remove(video_file_path)
                        os.remove(audio_file_path)
                    except Exception as e:
                        logger.warning(f"Error during cleanup: {e}")

                except Exception as e:
                    await update.reply_text(f"Error downloading: {e}")
                    logger.error(f"Error in process_direct_link: {e}")
                    return

            else:  # Not YouTube, provide download options
                randem = random_char(5)
                save_ytdl_json_path = os.path.join(Config.DOWNLOAD_LOCATION,
                                                    f"{update.from_user.id}{randem}.json")
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
                                    "🎬 {format_string} {format_ext} {approx_file_size} ".format(
                                        format_string=format_string, format_ext=format_ext,
                                        approx_file_size=approx_file_size),
                                    callback_data=(cb_string_video).encode("UTF-8")
                                )
                            ]
                        else:
                            # Special weird case :
                            ikeyboard = [
                                InlineKeyboardButton(
                                    "🎬 [{format_ext}] ({approx_file_size})".format(format_ext=format_ext,
                                                                                approx_file_size=approx_file_size),
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
                                "🎵 MP3 (64 kbps)", callback_data=cb_string_64.encode("UTF-8")),
                            InlineKeyboardButton(
                                "🎵 MP3 (128 kbps)", callback_data=cb_string_128.encode("UTF-8"))
                        ])
                        inline_keyboard.append([
                            InlineKeyboardButton(
                                "🎵 MP3 (320 kbps)", callback_data=cb_string.encode("UTF-8"))
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
                    text=Translation.FORMAT_SELECTION.format(""),
                    reply_markup=reply_markup,
                    parse_mode=enums.ParseMode.HTML,
                    reply_to_message_id=update.id
                )

        else:
            # --- Handle Cases Where yt-dlp Doesn't Return Valid JSON ---
            await chk.delete()
            await update.reply_text(
                "yt-dlp returned an invalid response. This could be due to changes in the target website. Please try again later or contact the bot developer.")
            return

    except Exception as e:
        await chk.delete()
        await update.reply_text(f"Error processing direct link: {e}")
        logger.error(f"Error in process_direct_link: {e}")

# --- New Function with NU prefix ---
async def NU_upload_to_telegram(bot: Client, update: Message, file_path: str, start_time: float):
    """Uploads the given file to Telegram with progress updates."""
    if os.path.isfile(file_path):
        file_size = os.stat(file_path).st_size
    else:
        await update.reply_text(f"File not found: {file_path}")
        return

    if file_size > Config.TG_MAX_FILE_SIZE:
        await update.reply_text(
            f"File is too large for Telegram! ({humanbytes(file_size)} > {humanbytes(Config.TG_MAX_FILE_SIZE)})"
        )
        return

    # --- Upload as Stream if File is Large (updated to 1.5GB) ---
    if file_size > 1610612736:
        with open(file_path, "rb") as f:
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
        # --- Normal Upload for Smaller Files ---
        if not await db.get_upload_as_doc(update.from_user.id):
            thumbnail = await Gthumb01(bot, update)
            await update.reply_document(
                document=file_path,  # Upload the merged file
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
            width, height, duration = await Mdata01(file_path)
            thumb_image_path = await Gthumb02(bot, update, duration, file_path)
            await update.reply_video(
                video=file_path,  # Upload the merged file
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

    # --- Success Message ---
    end_two = datetime.now()
    time_taken_for_upload = (end_two - end_one).seconds
    await update.reply_text(
        text=Translation.AFTER_SUCCESSFUL_UPLOAD_MSG_WITH_TS.format(
            time_taken_for_download, time_taken_for_upload),
        parse_mode=enums.ParseMode.HTML,
        disable_web_page_preview=True
    )
