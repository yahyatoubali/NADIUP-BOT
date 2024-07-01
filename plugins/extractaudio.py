#  @yahyatoubali

import asyncio
import os
import time
import subprocess

from pyrogram import Client, filters, enums
from pyrogram.types import Message

from plugins.config import Config
from plugins.script import Translation
from plugins.functions.display_progress import progress_for_pyrogram, humanbytes

@Client.on_message(filters.command("extractaudio") & filters.private)
async def extract_audio(bot: Client, message: Message):
    if message.reply_to_message and message.reply_to_message.video:
        await message.reply_chat_action(enums.ChatAction.TYPING)

        # Download the video
        download_location = await bot.download_media(
            message=message.reply_to_message.video,
            file_name=Config.DOWNLOAD_LOCATION + "/",
            progress=progress_for_pyrogram,
            progress_args=(
                Translation.DOWNLOAD_START,
                message,
                time.time()
            )
        )
        if download_location is None:
            return await message.edit_text(Translation.DOWNLOAD_FAILED)

        # Extract audio using ffmpeg
        output_file = os.path.splitext(download_location)[0] + ".mp3"
        command = [
            "ffmpeg", "-i", download_location, "-vn", "-acodec", "copy", output_file
        ]
        try:
            await asyncio.create_subprocess_exec(*command, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE)
        except Exception as e:
            return await message.edit_text(f"**Error extracting audio:** {e}")

        # Send extracted audio to user
        start_time = time.time()
        await message.reply_audio(
            audio=output_file,
            caption=f"**Extracted Audio from Video**",
            progress=progress_for_pyrogram,
            progress_args=(
                Translation.UPLOAD_START,
                message,
                start_time
            )
        )

        # Clean up files
        os.remove(download_location)
        os.remove(output_file)
    else:
        await message.reply_text("Please reply to a video to extract
