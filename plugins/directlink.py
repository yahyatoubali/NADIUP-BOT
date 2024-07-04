# plugins/directlink.py (Updated)
#  @yahyatoubali

import asyncio
import os
import requests
import aiofiles
import tempfile

from pyrogram import Client, filters, enums
from pyrogram.types import Message

from plugins.config import Config
from plugins.script import Translation

@Client.on_message(filters.command("directlink") & filters.private)
async def generate_direct_link(bot: Client, message: Message):
    if message.reply_to_message:
        supported_types = ["document", "video", "audio", "photo"] # Add supported types
        for file_type in supported_types:
            if getattr(message.reply_to_message, file_type, None): 
                try:
                    await message.reply_chat_action(enums.ChatAction.TYPING)

                    with tempfile.NamedTemporaryFile(delete=False) as temp_file:
                        download_location = await bot.download_media(
                            message=getattr(message.reply_to_message, file_type),
                            file_name=temp_file.name
                        )

                        if download_location is None:
                            return await message.edit_text(Translation.DOWNLOAD_FAILED)

                        async with aiofiles.open(temp_file.name, 'rb') as file:
                            file_data = await file.read()

                        response = requests.post("https://file.io", files={"file": file_data})

                        if response.status_code == 200:
                            data = response.json()
                            direct_link = data['link']
                            await message.reply_text(
                                f"**Direct Link:** `{direct_link}`\n\n**Note:** This link will expire in 14 days."
                            )
                        else:
                            await message.reply_text(f"Error generating direct link: {response.text}")

                except Exception as e:
                    await message.reply_text(f"Error: {e}")
                return # Stop if a supported file type is found and processed

        await message.reply_text(f"Please reply to a supported file type: {', '.join(supported_types)}") 
    else:
        await message.reply_text(f"Please reply to a supported file type: {', '.join(supported_types)}") 
