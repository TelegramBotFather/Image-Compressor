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
        """Handle incoming files and photos."""
        temp_path = None
        compressed_path = None
        status_msg = None
        
        try:
            user_id = message.from_user.id
            
            # Handle photo
            if message.photo:
                status_msg = await message.reply_text(Messages.PROCESSING)
                temp_path = await message.download()
                
            # Handle document
            elif message.document:
                if message.document.file_size > MAX_FILE_SIZE:
                    await message.reply_text(ERROR_MESSAGES["file_too_large"])
                    return
                    
                file_ext = os.path.splitext(message.document.file_name)[1].lower()
                if file_ext not in SUPPORTED_FORMATS:
                    await message.reply_text(ERROR_MESSAGES["invalid_format"])
                    return
                
                status_msg = await message.reply_text(Messages.PROCESSING)
                temp_path = await message.download()
            
            else:
                await message.reply_text(ERROR_MESSAGES["invalid_image"])
                return

            # Process image
            success, info = await get_image_info(temp_path)
            if not success:
                await status_msg.edit_text(ERROR_MESSAGES["invalid_image"])
                return

            # Compress image
            success, compressed_path, error = await self.api_handler.compress_image(
                temp_path,
                user_id
            )

            if not success:
                await status_msg.edit_text(error or ERROR_MESSAGES["general_error"])
                return

            # Send result
            await status_msg.delete()
            await self.client.send_document(
                message.chat.id,
                compressed_path,
                caption=Messages.get_compression_result(
                    os.path.getsize(temp_path),
                    os.path.getsize(compressed_path)
                ),
                reply_markup=Keyboards.main_menu()
            )

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