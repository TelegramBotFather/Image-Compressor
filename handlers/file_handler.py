from pyrogram import Client
from pyrogram.types import Message
from utils.helpers import get_image_info, clean_temp_files
from api_management.api_handler import APIHandler
from components.messages import Messages
from components.keyboards import Keyboards
from config import MAX_FILE_SIZE, SUPPORTED_FORMATS, ERROR_MESSAGES
import os
import logging

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

            # Get file ID
            file_id = message.photo.file_id if message.photo else message.document.file_id
            if not file_id:
                await message.reply_text(ERROR_MESSAGES["invalid_image"])
                return

            # Rest of your code...

        except Exception as e:
            logger.error(f"Error handling file: {str(e)}")
            if status_msg:
                await status_msg.edit_text(ERROR_MESSAGES["general_error"])
            else:
                await message.reply_text(ERROR_MESSAGES["general_error"])
                
        finally:
            # Clean up temporary files
            paths_to_clean = []
            if temp_path and os.path.exists(temp_path):
                paths_to_clean.append(temp_path)
            if compressed_path and os.path.exists(compressed_path):
                paths_to_clean.append(compressed_path)
            await clean_temp_files(paths_to_clean)