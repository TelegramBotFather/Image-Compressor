from pyrogram import Client
from pyrogram.types import Message
from api_management.api_handler import APIHandler
from utils.helpers import get_image_info, format_size
from config import MAX_FILE_SIZE, ERROR_MESSAGES, LOG_CHANNEL_ID
from database.mongodb import db
import os
import logging

logger = logging.getLogger(__name__)

class FileHandler:
    def __init__(self, client: Client):
        self.client = client
        self.api_handler = APIHandler()

    async def handle(self, client: Client, message: Message) -> None:
        temp_path = None
        compressed_path = None
        progress_message = None
        
        try:
            user_id = message.from_user.id
            
            # Get file info based on message type
            if message.photo:
                file_id = message.photo.file_id
                file_name = f"{file_id}.jpg"
            elif message.document:
                file_id = message.document.file_id
                file_name = message.document.file_name
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
                await progress_message.edit_text(ERROR_MESSAGES["general_error"])
                return

            # Get user's format preference
            user_settings = await db.settings.find_one({"user_id": user_id})
            target_format = user_settings.get("current_format") if user_settings else None

            if progress_message:
                await progress_message.edit_text("🔄 Processing image...")

            # Compress image
            compression_result = await self.api_handler.compress_image(
                input_path=temp_path,
                user_id=user_id,
                output_path=compressed_path,
                target_format=target_format
            )

            if not compression_result.get("success", False):
                if progress_message:
                    await progress_message.edit_text(ERROR_MESSAGES["general_error"])
                return

            # Update compressed_path if format changed
            if target_format:
                compressed_path = compressed_path.rsplit('.', 1)[0] + f'.{target_format}'

            # Calculate stats
            original_size = os.path.getsize(temp_path)
            compressed_size = os.path.getsize(compressed_path)
            saved_percentage = ((original_size - compressed_size) / original_size) * 100

            # Prepare caption
            caption = (
                "✅ Image compressed successfully!\n\n"
                f"Original Size: {format_size(original_size)}\n"
                f"Compressed Size: {format_size(compressed_size)}\n"
                f"Space Saved: {saved_percentage:.1f}%"
            )

            if compression_result.get("format"):
                caption += f"\nFormat: {compression_result['format'].upper()}"

            # Send to user
            await message.reply_document(
                document=compressed_path,
                caption=caption,
                force_document=True
            )

            # Send to log channel
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

            if progress_message:
                await progress_message.delete()

        except Exception as e:
            logger.error(f"Error handling file: {str(e)}")
            if progress_message:
                try:
                    await progress_message.edit_text(ERROR_MESSAGES["general_error"])
                except Exception:
                    pass
        finally:
            # Cleanup temporary files
            for path in [temp_path, compressed_path]:
                if path and os.path.exists(path):
                    try:
                        os.remove(path)
                        logger.info(f"Deleted temporary file: {path}")
                    except Exception as e:
                        logger.error(f"Error deleting file {path}: {str(e)}")
