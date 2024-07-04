#  @yahyatoubali

import asyncio
import libtorrent as lt
import time
import os
import shutil
import logging

from pyrogram import Client, filters, enums
from pyrogram.types import Message

from plugins.config import Config
from plugins.script import Translation
from plugins.functions.display_progress import progress_for_pyrogram, humanbytes, TimeFormatter
from plugins.thumbnail import Gthumb01, Gthumb02, Mdata01, Mdata02, Mdata03  # Assuming you have the thumbnail functions

# Create a logger instance
logger = logging.getLogger(__name__)

# Dictionary to store user's active torrents
user_torrents = {}

@Client.on_message((filters.command("torrent") | filters.regex(pattern="^magnet:.*")) & filters.private) 
async def torrent_download(bot: Client, message: Message):
    try:
        # Get torrent content 
        if message.document:
            torrent_file_path = await bot.download_media(
                message=message.document,
                file_name=Config.DOWNLOAD_LOCATION + "/"
            )
        elif message.text and message.text.startswith("magnet:"):
            torrent_file_path = message.text
        else:
            await message.reply_text("Please provide a torrent file or magnet link.")
            return

        # --- Updated Section to define torrent_file_path ---
        # Initialize libtorrent session and add torrent
        ses = lt.session({'listen_interfaces': '0.0.0.0:6881'})
        if torrent_file_path.startswith("magnet:"):
            params = {
                'save_path': Config.DOWNLOAD_LOCATION,
                'storage_mode': lt.storage_mode_t.storage_mode_sparse,
            }
            handle = lt.add_magnet_uri(ses, torrent_file_path, params)
        else:
            info = lt.torrent_info(torrent_file_path)
            params = {
                'save_path': Config.DOWNLOAD_LOCATION,
                'storage_mode': lt.storage_mode_t.storage_mode_sparse,
                'ti': info,
            }
            handle = ses.add_torrent(params)

        logger.info(f"Torrent added: {handle.name()}")

        user_torrents[message.from_user.id] = handle  # Store handle

        # Start download and update progress
        await message.reply_text(f"Downloading torrent: `{handle.name()}`")
        start_time = time.time()
        previous_update_time = time.time()
        while not handle.is_seed():
            s = handle.status()

            if time.time() - previous_update_time >= 5:
                try:
                    current_progress = s.progress * 100
                    downloaded_bytes = s.total_done
                    total_size = s.total_wanted
                    download_speed = s.download_rate

                    await progress_for_pyrogram(
                        current_progress,
                        100,  # Percentage
                        f"Downloading: `{handle.name()}`",
                        message,
                        start_time
                    )

                    previous_update_time = time.time()

                except Exception as e:
                    logger.error(f"Error updating progress: {e}")

            await asyncio.sleep(1)

        end_time = time.time()
        total_time_taken = end_time - start_time

        # Send files after download completion
        await message.reply_text(
            f"Torrent downloaded successfully! Time taken: {TimeFormatter(total_time_taken * 1000)}"
        )
        # Get files from the 'info' object
        info = handle.get_torrent_info()
        for i in range(info.num_files()):
            file_path = os.path.join(Config.DOWNLOAD_LOCATION, info.files().at(i).path)

            # Check file type and upload accordingly
            if file_path.lower().endswith((".mp4", ".mkv", ".avi", ".mov", ".webm")):  # Add more video extensions
                # Upload video as stream
                start_time = time.time()
                width, height, duration = await Mdata01(file_path)
                thumb_image_path = await Gthumb02(bot, message, duration, file_path)
                await message.reply_video(
                    video=file_path,
                    caption=f"File: `{info.files().at(i).path}`",
                    duration=duration,
                    width=width,
                    height=height,
                    supports_streaming=True,
                    parse_mode=enums.ParseMode.HTML,
                    thumb=thumb_image_path,
                    progress=progress_for_pyrogram,
                    progress_args=(
                        Translation.UPLOAD_START,
                        message,
                        start_time
                    )
                )
                try:
                    os.remove(file_path)
                    os.remove(thumb_image_path)
                except Exception as e:
                    logger.warning(f"Error during cleanup: {e}")
            else:
                # Upload as a document
                start_time = time.time()
                # Add progress bar for document upload
                await message.reply_document(
                    document=file_path,
                    caption=f"File: `{info.files().at(i).path}`",
                    parse_mode=enums.ParseMode.HTML,
                    progress=progress_for_pyrogram,
                    progress_args=(
                        Translation.UPLOAD_START,
                        message,
                        start_time
                    )
                )
                try:
                    os.remove(file_path)
                except Exception as e:
                    logger.warning(f"Error during cleanup: {e}")

        # Clean up torrent files 
        try:
            os.remove(torrent_file_path)
            shutil.rmtree(os.path.join(Config.DOWNLOAD_LOCATION, handle.name()))
        except Exception as e:
            logger.warning(f"Error during cleanup: {e}")

    except Exception as e:
        await message.reply_text(f"Error downloading torrent: {e}")
        logger.error(f"Error in torrent_download: {e}")


@Client.on_message(filters.command("pausetorrent") & filters.private)
async def pause_torrent(bot: Client, message: Message):
    user_id = message.from_user.id
    if user_id in user_torrents:
        handle = user_torrents[user_id]
        handle.pause()
        await message.reply_text(f"Torrent paused: `{handle.name()}`")
    else:
        await message.reply_text("You don't have any active torrents.")

@Client.on_message(filters.command("resumetorrent") & filters.private)
async def resume_torrent(bot: Client, message: Message):
    user_id = message.from_user.id
    if user_id in user_torrents:
        handle = user_torrents[user_id]
        handle.resume()
        await message.reply_text(f"Torrent resumed: `{handle.name()}`")
    else:
        await message.reply_text("You don't have any active torrents.")
