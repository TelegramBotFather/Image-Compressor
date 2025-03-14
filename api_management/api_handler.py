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
        tinify.key = self.default_api_key  # Initialize the API key
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
        input_path: str,
        user_id: int,
        output_path: str
    ) -> dict:
        """
        Compress an image using TinyPNG API.
        
        Args:
            input_path (str): Path to input image
            user_id (int): User ID for API key lookup
            output_path (str): Path to save compressed image
        
        Returns:
            dict: Compression results
        """
        try:
            # Verify input file exists
            if not os.path.exists(input_path):
                return {"success": False, "error": "Input file not found"}

            # Get API key
            api_key = await self.get_api_key(user_id)
            tinify.key = api_key or self.default_api_key

            if not tinify.key:
                return {"success": False, "error": "No API key available"}

            # Compress image
            source = tinify.from_file(input_path)
            source.to_file(output_path)

            if not os.path.exists(output_path):
                return {"success": False, "error": "Failed to save compressed image"}

            return {
                "success": True,
                "original_size": os.path.getsize(input_path),
                "compressed_size": os.path.getsize(output_path)
            }

        except Exception as e:
            logger.error(f"Compression error: {str(e)}", exc_info=True)
            return {"success": False, "error": str(e)}

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