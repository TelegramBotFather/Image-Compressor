from pyrogram import Client
from pyrogram.types import Message
from components.keyboards import Keyboards
from api_management.api_handler import APIHandler
from log_handlers.channel_logger import ChannelLogger
from utils import (
    download_image, 
    clean_temp_files
)
from utils.decorators import rate_limit
from config import ERROR_MESSAGES
import logging
import os

logger = logging.getLogger(__name__)

class URLHandler:
    def __init__(self, client: Client):
        self.client = client
        self.api_handler = APIHandler()
        self.channel_logger = ChannelLogger(client)

    @rate_limit
    async def handle(self, client: Client, message: Message) -> None:
        temp_path = None
        compressed_path = None
        try:
            url = message.text.strip()
            if not validators.url(url):
                await message.reply_text(ERROR_MESSAGES["invalid_url"])
                return

            # Download image
            status_msg = await message.reply_text("⏳ Downloading image...")
            temp_path = f"temp/{message.from_user.id}_{message.message_id}.jpg"
            success, error = await download_image(url, temp_path)
            
            if not success:
                await status_msg.edit_text(f"❌ Download failed: {error}")
                return

            await status_msg.edit_text("🔄 Processing image...")

            # Compress image
            compressed_path = await self.api_handler.compress_image(
                temp_path,
                message.from_user.id
            )

            # Send result
            await status_msg.delete()
            await self.client.send_document(
                message.chat.id,
                compressed_path,
                caption=f"Original URL: {url}\n"
                        f"Size: {os.path.getsize(compressed_path)/1024:.1f}KB"
            )

        except Exception as e:
            logger.error(f"Error handling URL: {str(e)}")
            await message.reply_text(ERROR_MESSAGES["general_error"])
        finally:
            # Ensure variables are defined before cleanup
            paths_to_clean = []
            if temp_path and os.path.exists(temp_path):
                paths_to_clean.append(temp_path)
            if compressed_path and os.path.exists(compressed_path):
                paths_to_clean.append(compressed_path)
            await clean_temp_files(paths_to_clean)