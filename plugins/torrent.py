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

# Create a logger instance
logger = logging.getLogger(__name__)

# Dictionary to store user's active torrents
user_torrents = {}

@Client.on_message(filters.command("torrent") & filters.private)
async def torrent_download(bot: Client, message: Message):
    if message.reply_to_message:
        if message.reply_to_message.document or message.reply_to_message.text:
            try:
                # Get torrent content
                if message.reply_to_message.document:
                    torrent_file_path = await bot.download_media(
                        message=message.reply_to_message.document,
                        file_name=Config.DOWNLOAD_LOCATION + "/"
                    )
                elif message.reply_to_message.text and message.reply_to_message.text.startswith("magnet:"):
                    torrent_file_path = message.reply_to_message.text
                else:
                    await message.reply_text("Please reply to a torrent file or magnet link.")
                    return

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
                for f in handle.files():
                    file_path = os.path.join(Config.DOWNLOAD_LOCATION, f.path())
                    await bot.send_document(
                        message.chat.id,
                        document=file_path,
                        caption=f"File: `{f.path()}`",
                        disable_notification=True
                    )

                # Clean up torrent files (adjust as needed)
                try:
                    os.remove(torrent_file_path)
                    shutil.rmtree(os.path.join(Config.DOWNLOAD_LOCATION, handle.name()))

                except Exception as e:
                    logger.warning(f"Error during cleanup: {e}")

            except Exception as e:
                await message.reply_text(f"Error downloading torrent: {e}")
                logger.error(f"Error in torrent_download: {e}")
    else:
        await message.reply_text("Please reply to a torrent file or magnet link.")


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
