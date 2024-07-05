#  @yahyatoubali
import logging
logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

import asyncio
import json
import math
import os
import shutil
import time
from datetime import datetime
import aiohttp  # Import aiohttp for asynchronous downloads

from pyrogram import Client, enums
from plugins.config import Config
from plugins.script import Translation
from plugins.thumbnail import *
logging.getLogger("pyrogram").setLevel(logging.WARNING)
from pyrogram.types import InputMediaPhoto
from plugins.functions.display_progress import progress_for_pyrogram, humanbytes
from plugins.database.database import db
from PIL import Image
from plugins.functions.ran_text import random_char
import tempfile
import subprocess

async def youtube_dl_call_back(bot: Client, update: CallbackQuery):
    cb_data = update.data
    tg_send_type, youtube_dl_format, youtube_dl_ext, ranom = cb_data.split("|")
    random1 = random_char(5)

    save_ytdl_json_path = os.path.join(Config.DOWNLOAD_LOCATION, f"{update.from_user.id}{ranom}.json")

    try:
        with open(save_ytdl_json_path, "r", encoding="utf8") as f:
            response_json = json.load(f)
    except FileNotFoundError as e:
        logger.error(f"JSON file not found: {e}")
        await update.message.delete()
        return False

    youtube_dl_url = update.message.reply_to_message.text
    custom_file_name = f"{response_json.get('title')}_{youtube_dl_format}.{youtube_dl_ext}"
    youtube_dl_username = None
    youtube_dl_password = None

    # Define download_directory here, before the if block
    tmp_directory_for_each_user = os.path.join(Config.DOWNLOAD_LOCATION, f"{update.from_user.id}{random1}")
    os.makedirs(tmp_directory_for_each_user, exist_ok=True)
    download_directory = os.path.join(tmp_directory_for_each_user, custom_file_name)

    if "|" in youtube_dl_url:
        url_parts = youtube_dl_url.split("|")
        if len(url_parts) == 2:
            youtube_dl_url, custom_file_name = url_parts
        elif len(url_parts) == 4:
            youtube_dl_url, custom_file_name, youtube_dl_username, youtube_dl_password = url_parts
        else:
            for entity in update.message.reply_to_message.entities:
                if entity.type == "text_link":
                    youtube_dl_url = entity.url
                elif entity.type == "url":
                    o = entity.offset
                    l = entity.length
                    youtube_dl_url = youtube_dl_url[o:o + l]

        youtube_dl_url = youtube_dl_url.strip()
        custom_file_name = custom_file_name.strip()
        if youtube_dl_username:
            youtube_dl_username = youtube_dl_username.strip()
        if youtube_dl_password:
            youtube_dl_password = youtube_dl_password.strip()

        logger.info(youtube_dl_url)
        logger.info(custom_file_name)
    else:
        for entity in update.message.reply_to_message.entities:
            if entity.type == "text_link":
                youtube_dl_url = entity.url
            elif entity.type == "url":
                o = entity.offset
                l = entity.length
                youtube_dl_url = youtube_dl_url[o:o + l]

    await update.message.edit_caption(
        caption=Translation.DOWNLOAD_START.format(custom_file_name)
    )

    description = Translation.CUSTOM_CAPTION_UL_FILE
    if "fulltitle" in response_json:
        description = response_json["fulltitle"][0:1021]

    # **Extract direct download URL (if present):**
    direct_download_url = response_json.get("url")

    if direct_download_url:
        # Download using the direct URL
        async with aiohttp.ClientSession() as session:
            async with session.get(direct_download_url) as response:
                if response.status == 200:
                    total_size = int(response.headers.get("content-length", 0)) or None
                    with open(download_directory, "wb") as file:
                        async for data in response.content.iter_chunked(1024 * 1024):  # 1MB chunks
                            file.write(data)

                            # Update progress
                            if total_size:
                                downloaded_size = os.path.getsize(download_directory)
                                percentage = (downloaded_size / total_size) * 100
                                if int(percentage) % 5 == 0:
                                    await update.message.edit_caption(
                                        f"Downloading: `{custom_file_name}`\n"
                                        f"Progress: {int(percentage)}%"
                                    )
    else:
        # Download using yt-dlp if direct URL is not found
        command_to_exec = [
            "yt-dlp",
            "-c",
            "--max-filesize", str(Config.TG_MAX_FILE_SIZE),
            "--embed-subs",
            "-f", f"{youtube_dl_format}+bestaudio/best",
            "--hls-prefer-ffmpeg",
            youtube_dl_url,
            "-o", download_directory
        ]

        if tg_send_type == "audio":
            command_to_exec = [
                "yt-dlp",
                "-c",
                "--max-filesize", str(Config.TG_MAX_FILE_SIZE),
                "--bidi-workaround",
                "--extract-audio",
                "--audio-format", youtube_dl_ext,
                "--audio-quality", youtube_dl_format,
                youtube_dl_url,
                "-o", download_directory
            ]

        if Config.HTTP_PROXY:
            command_to_exec.extend(["--proxy", Config.HTTP_PROXY])
        if youtube_dl_username:
            command_to_exec.extend(["--username", youtube_dl_username])
        if youtube_dl_password:
            command_to_exec.extend(["--password", youtube_dl_password])

        command_to_exec.append("--no-warnings")

        logger.info(command_to_exec)
        start = datetime.now()

        process = await asyncio.create_subprocess_exec(
            *command_to_exec,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )

        stdout, stderr = await process.communicate()
        e_response = stderr.decode().strip()
        t_response = stdout.decode().strip()
        logger.info(e_response)
        logger.info(t_response)

        ad_string_to_replace = "**Invalid link !**"
        if e_response and ad_string_to_replace in e_response:
            error_message = e_response.replace(ad_string_to_replace, "")
            await update.message.edit_caption(
                text=error_message
            )
            return False

        if t_response:
            logger.info(t_response)
            try:
                os.remove(save_ytdl_json_path)
            except FileNotFoundError:
                pass

            end_one = datetime.now()
            time_taken_for_download = (end_one - start).seconds

            # ... (Rest of the code for yt-dlp download and processing)

    # ----------------------- Upload Logic -----------------------
    await update.message.edit_caption(
        caption=Translation.UPLOAD_START.format(custom_file_name)
    )
    start_time = time.time()

    if os.path.isfile(download_directory):
        file_size = os.stat(download_directory).st_size
    else:
        download_directory = os.path.splitext(download_directory)[0] + ".mkv"
        if os.path.isfile(download_directory):
            file_size = os.stat(download_directory).st_size
        else:
            logger.error(f"Downloaded file not found: {download_directory}")
            await update.message.edit_caption(
                caption=Translation.DOWNLOAD_FAILED
            )
            return False

    if file_size > Config.TG_MAX_FILE_SIZE:
        await update.message.edit_caption(
            caption=Translation.RCHD_TG_API_LIMIT.format(time_taken_for_download, humanbytes(file_size))
        )
        return False
    else:
        # Upload as stream if file is large (updated to 1.5GB)
        if file_size > 1610612736:
            with open(download_directory, "rb") as f:
                await update.message.reply_document(
                    document=f,
                    caption=description,
                    parse_mode=enums.ParseMode.HTML,
                    progress=progress_for_pyrogram,
                    progress_args=(
                        Translation.UPLOAD_START,
                        update.message,
                        start_time
                    )
                )
        else:
            # Normal upload for smaller files
            if not await db.get_upload_as_doc(update.from_user.id):
                thumbnail = await Gthumb01(bot, update)
                await update.message.reply_document(
                    document=download_directory,
                    thumb=thumbnail,
                    caption=description,
                    progress=progress_for_pyrogram,
                    progress_args=(
                        Translation.UPLOAD_START,
                        update.message,
                        start_time
                    )
                )
            else:
                width, height, duration = await Mdata01(download_directory)
                thumb_image_path = await Gthumb02(bot, update, duration, download_directory)
                await update.message.reply_video(
                    video=download_directory,
                    caption=description,
                    duration=duration,
                    width=width,
                    height=height,
                    supports_streaming=True,
                    thumb=thumb_image_path,
                    progress=progress_for_pyrogram,
                    progress_args=(
                        Translation.UPLOAD_START,
                        update.message,
                        start_time
                    )
                )

        if tg_send_type == "audio":
            duration = await Mdata03(download_directory)
            thumbnail = await Gthumb01(bot, update)
            await update.message.reply_audio(
                audio=download_directory,
                caption=description,
                duration=duration,
                thumb=thumbnail,
                progress=progress_for_pyrogram,
                progress_args=(
                    Translation.UPLOAD_START,
                    update.message,
                    start_time
                )
            )
        elif tg_send_type == "vm":
            width, duration = await Mdata02(download_directory)
            thumbnail = await Gthumb02(bot, update, duration, download_directory)
            await update.message.reply_video_note(
                video_note=download_directory,
                duration=duration,
                length=width,
                thumb=thumbnail,
                progress=progress_for_pyrogram,
                progress_args=(
                    Translation.UPLOAD_START,
                    update.message,
                    start_time
                )
            )
        else:
            logger.info("✅ " + custom_file_name)

        end_two = datetime.now()
        time_taken_for_upload = (end_two - end_one).seconds
        try:
            shutil.rmtree(tmp_directory_for_each_user)
            if thumbnail:  # Delete thumbnail if it exists
                os.remove(thumbnail)
        except Exception as e:
            logger.error(f"Error cleaning up: {e}")

        await update.message.edit_caption(
            caption=Translation.AFTER_SUCCESSFUL_UPLOAD_MSG_WITH_TS.format(time_taken_for_download,
                                                                            time_taken_for_upload)
        )

        logger.info(f"Downloaded in: {time_taken_for_download} seconds")
        logger.info(f"Uploaded in: {time_taken_for_upload} seconds")
