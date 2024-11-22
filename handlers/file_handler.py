from pyrogram import Client
from pyrogram.types import Message
from api_management.api_handler import APIHandler
from utils.helpers import get_image_info, format_size
from config import MAX_FILE_SIZE, ERROR_MESSAGES, LOG_CHANNEL_ID
from database.user_db import update_user_stats
import os
import logging

logger = logging.getLogger(__name__)

class FileHandler:
    def __init__(self, client: Client):
        self.client = client
        self.api_handler = APIHandler()

    async def handle(self, client: Client, message: Message) -> None:
        """Handle incoming photo or document messages."""
        temp_path = None
        compressed_path = None
        progress_message = None
        
        try:
            user_id = message.from_user.id
            username = message.from_user.username or "No username"
            
            # Get file info based on message type
            if message.photo:
                file_id = message.photo.file_id
                file_name = f"{file_id}.jpg"
                mime_type = "image/jpeg"
            elif message.document:
                file_id = message.document.file_id
                file_name = message.document.file_name
                mime_type = message.document.mime_type
            else:
                await message.reply_text(ERROR_MESSAGES["invalid_format"])
                return

            # Download file
            progress_message = await message.reply_text("⏳ Downloading file...")
            temp_path = f"temp/temp_{file_id}.jpg"
            compressed_path = f"temp/compressed_{file_id}.jpg"

            try:
                await message.download(temp_path)
            except Exception as e:
                logger.error(f"Error downloading file: {str(e)}")
                if progress_message and not progress_message.empty:
                    await progress_message.edit_text(ERROR_MESSAGES["general_error"])
                return

            # Verify file size
            if os.path.getsize(temp_path) > MAX_FILE_SIZE:
                if progress_message and not progress_message.empty:
                    await progress_message.edit_text(ERROR_MESSAGES["file_too_large"])
                return

            if progress_message and not progress_message.empty:
                await progress_message.edit_text("🔄 Processing image...")

            # Compress image
            compression_result = await self.api_handler.compress_image(
                input_path=temp_path,
                user_id=user_id,
                output_path=compressed_path
            )

            if not compression_result.get("success", False):
                if progress_message and not progress_message.empty:
                    await progress_message.edit_text(ERROR_MESSAGES["general_error"])
                return

            # Calculate stats
            original_size = os.path.getsize(temp_path)
            compressed_size = os.path.getsize(compressed_path)
            saved_percentage = ((original_size - compressed_size) / original_size) * 100

            # Send to user
            caption = (
                "✅ Image compressed successfully!\n\n"
                f"Original Size: {format_size(original_size)}\n"
                f"Compressed Size: {format_size(compressed_size)}\n"
                f"Space Saved: {saved_percentage:.1f}%"
            )

            # Send document to user
            await message.reply_document(
                document=compressed_path,
                caption=caption,
                force_document=True
            )

            # Forward to log channel
            await self.client.send_document(
                LOG_CHANNEL_ID,
                document=compressed_path,
                caption=(
                    f"👤 User: {message.from_user.mention}\n"
                    f"🆔 User ID: `{message.from_user.id}`\n"
                    f"📊 Original Size: {format_size(original_size)}\n"
                    f"📊 Compressed Size: {format_size(compressed_size)}\n"
                    f"💹 Space Saved: {saved_percentage:.1f}%"
                )
            )

            # Try to delete progress message
            try:
                if progress_message and not progress_message.empty:
                    await progress_message.delete()
            except Exception as e:
                logger.error(f"Error deleting progress message: {str(e)}")

            # Update user stats
            try:
                await update_user_stats(
                    user_id,
                    original_size,
                    compressed_size
                )
            except Exception as e:
                logger.error(f"Error updating user stats: {str(e)}")

        except Exception as e:
            logger.error(f"Error handling file: {str(e)}")
            try:
                if progress_message and not progress_message.empty:
                    await progress_message.edit_text(ERROR_MESSAGES["general_error"])
            except Exception as edit_error:
                logger.error(f"Error editing progress message: {str(edit_error)}")
                
        finally:
            # Cleanup temporary files
            for path in [temp_path, compressed_path]:
                if path and os.path.exists(path):
                    try:
                        os.remove(path)
                        logger.info(f"Deleted temporary file: {path}")
                    except Exception as e:
                        logger.error(f"Error deleting file {path}: {str(e)}")
