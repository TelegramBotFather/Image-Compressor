from pyrogram import Client
from pyrogram.types import Message
from utils.helpers import get_image_info, clean_temp_files
from api_management.api_handler import APIHandler
from components.messages import Messages
from components.keyboards import Keyboards
from config import MAX_FILE_SIZE, SUPPORTED_FORMATS, ERROR_MESSAGES
import os
import logging
import time
from database.user_db import get_user_settings
from components.messages import Messages
from pyrogram.types import ParseMode

logger = logging.getLogger(__name__)

class FileHandler:
    def __init__(self, client: Client):
        self.client = client
        self.api_handler = APIHandler()

    async def handle(self, client: Client, message: Message) -> None:
        """Handle file messages."""
        status_msg = None
        temp_path = None
        compressed_path = None
        
        try:
            # Check if message has a valid file
            if not message.photo and not message.document:
                await message.reply_text(ERROR_MESSAGES["invalid_image"])
                return

            # Get file ID and user settings
            file_id = message.photo[-1].file_id if message.photo else message.document.file_id
            user_id = message.from_user.id
            user_settings = await get_user_settings(user_id)
            target_format = user_settings.get('default_format', 'jpeg')

            # Send processing message
            status_msg = await message.reply_text(
                Messages.PROCESSING,
                parse_mode=ParseMode.HTML
            )

            # Download file
            temp_path = f"temp/{file_id}_{int(time.time())}"
            await message.download(temp_path)

            # Check file size and format
            success, info = await get_image_info(temp_path)
            if not success:
                await status_msg.edit_text(ERROR_MESSAGES["invalid_image"])
                return

            if info['size'] > MAX_FILE_SIZE:
                await status_msg.edit_text(ERROR_MESSAGES["file_too_large"])
                return

            # Compress image
            success, compressed_path, error_msg = await self.api_handler.compress_image(
                temp_path,
                user_id,
                target_format
            )

            if not success:
                await status_msg.edit_text(error_msg or ERROR_MESSAGES["general_error"])
                return

            # Send compressed image
            await message.reply_document(
                compressed_path,
                caption=f"✅ Compressed and converted to {target_format.upper()}\n"
                       f"Original: {info['size']/1024:.1f}KB\n"
                       f"Compressed: {os.path.getsize(compressed_path)/1024:.1f}KB"
            )
            await status_msg.delete()

        except Exception as e:
            logger.error(f"Error handling file: {str(e)}")
            if status_msg:
                await status_msg.edit_text(ERROR_MESSAGES["general_error"])
        
        finally:
            # Clean up temporary files
            paths_to_clean = [p for p in [temp_path, compressed_path] if p and os.path.exists(p)]
            await clean_temp_files(paths_to_clean)