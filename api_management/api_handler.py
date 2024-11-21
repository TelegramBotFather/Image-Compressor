from typing import Optional, Tuple
import tinify
from log_handlers.api_logger import APILogger
from datetime import datetime
from database.user_db import update_user_stats
from config import TINIFY_API_KEY
from database.mongodb import db
import os
from pyrogram.types import Message
from components.keyboards import Keyboards
import logging

logger = logging.getLogger(__name__)

class APIHandler:
    """Handler for interacting with the TinyPNG API."""

    def __init__(self):
        self.api_logger = APILogger()
        self.default_api_key = os.getenv("TINIFY_API_KEY")
        self._api_cache = {}

    async def get_api_key(self, user_id: int) -> str:
        """
        Retrieve the user's API key or return the default key if none is set.

        Args:
            user_id (int): The Telegram user ID.

        Returns:
            str: The API key to be used.
        """
        try:
            if user_id in self._api_cache:
                return self._api_cache[user_id]
            
            user_key = await self._get_user_api_key(user_id)
            if user_key:
                self._api_cache[user_id] = user_key
                return user_key
            
            return self.default_api_key
        except Exception as e:
            logger.error(f"Error getting API key: {str(e)}")
            return self.default_api_key

    async def compress_image(
        self,
        file_path: str,
        user_id: int,
        target_format: Optional[str] = None
    ) -> Tuple[bool, str, dict]:
        try:
            # Get user's API key if exists
            api_key = await self.api_settings.get_user_api_key(user_id)
            if api_key:
                tinify.key = api_key
            
            # Compress image
            source = tinify.from_file(file_path)
            if target_format:
                source = source.convert(format=target_format)
            
            # Save compressed image
            output_path = f"temp/compressed_{os.path.basename(file_path)}"
            source.to_file(output_path)
            
            # Get compression stats
            stats = {
                "original_size": os.path.getsize(file_path),
                "compressed_size": os.path.getsize(output_path)
            }
            
            return True, output_path, stats
            
        except Exception as e:
            logger.error(f"Compression error: {str(e)}")
            return False, str(e), {}

    async def _get_user_api_key(self, user_id: int) -> Optional[str]:
        """
        Retrieve user's custom API key from database.

        Args:
            user_id (int): The Telegram user ID.

        Returns:
            Optional[str]: The user's custom API key.
        """
        try:
            result = await db.api_keys.find_one({"user_id": user_id})
            return result["api_key"] if result else None
        except Exception as e:
            logger.error(f"Error retrieving API key: {str(e)}")
            return None