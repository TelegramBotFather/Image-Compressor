from typing import Optional
from pyrogram import Client
from pyrogram.types import Message, CallbackQuery
from pyrogram.enums import ParseMode
from database.api_db import save_api_key, get_user_api_key, remove_api_key
from components.keyboards import Keyboards
from utils.validators import validate_api_key_format
import logging

logger = logging.getLogger(__name__)

class APISettings:
    def __init__(self, client: Client):
        self.client = client
        self._waiting_for_api = set()  # Users currently setting API key

    async def show_api_settings(self, message: Message) -> None:
        """Show API settings menu."""
        try:
            user_id = message.from_user.id
            has_custom_api = bool(await get_user_api_key(user_id))
            
            text = (
                "🔑 <b>API Key Settings</b>\n\n"
                f"Status: {'✅ Custom API Key Set' if has_custom_api else '❌ No Custom API Key'}\n\n"
                "With a custom API key:\n"
                "• Higher daily limits\n"
                "• Priority processing\n"
                "• Usage statistics\n\n"
                "Get your API key from tinypng.com"
            )
            
            await message.reply_text(
                text,
                reply_markup=Keyboards.api_key_settings(has_custom_api),
                parse_mode=ParseMode.HTML
            )
        except Exception as e:
            logger.error(f"Error showing API settings: {str(e)}")
            await message.reply_text("❌ An error occurred")

    async def handle_api_key_input(self, message: Message) -> None:
        """Handle API key input from user."""
        try:
            user_id = message.from_user.id
            if user_id not in self._waiting_for_api:
                return

            # Remove user from waiting list
            self._waiting_for_api.remove(user_id)
            
            # Validate API key
            api_key = message.text.strip()
            is_valid, msg = validate_api_key_format(api_key)
            
            if not is_valid:
                await message.reply_text(
                    f"❌ Invalid API key: {msg}\n\nPlease try again with a valid key.",
                    reply_markup=Keyboards.settings_menu()
                )
                return

            # Save API key
            if await save_api_key(user_id, api_key):
                await message.reply_text(
                    "✅ API key saved successfully!\n\n"
                    "You can now use your custom API key for compression.",
                    reply_markup=Keyboards.settings_menu(True)
                )
            else:
                await message.reply_text(
                    "❌ Failed to save API key. Please try again.",
                    reply_markup=Keyboards.settings_menu()
                )

        except Exception as e:
            logger.error(f"Error handling API key input: {str(e)}")
            await message.reply_text("❌ An error occurred")

    async def start_api_key_input(self, message: Message) -> None:
        """Start API key input process."""
        try:
            user_id = message.from_user.id
            self._waiting_for_api.add(user_id)
            
            await message.reply_text(
                "📝 Please send your TinyPNG API key.\n\n"
                "You can get it from: https://tinypng.com/developers\n\n"
                "Send /cancel to cancel this operation.",
                reply_markup=Keyboards.cancel_button()
            )
        except Exception as e:
            logger.error(f"Error starting API key input: {str(e)}")
            await message.reply_text("❌ An error occurred")

    async def remove_api_key(self, message: Message) -> None:
        """Remove user's custom API key."""
        try:
            user_id = message.from_user.id
            if await remove_api_key(user_id):
                await message.reply_text(
                    "✅ Custom API key removed successfully.\n"
                    "Bot will now use the default API key.",
                    reply_markup=Keyboards.settings_menu(False)
                )
            else:
                await message.reply_text(
                    "❌ Failed to remove API key. Please try again.",
                    reply_markup=Keyboards.settings_menu(True)
                )
        except Exception as e:
            logger.error(f"Error removing API key: {str(e)}")
            await message.reply_text("❌ An error occurred")

    def is_waiting_for_api(self, user_id: int) -> bool:
        """Check if user is in API key input mode."""
        return user_id in self._waiting_for_api

    def add_waiting_user(self, user_id: int) -> None:
        """Add user to API key input waiting list."""
        self._waiting_for_api.add(user_id)

    def remove_waiting_user(self, user_id: int) -> None:
        """Remove user from API key input waiting list."""
        self._waiting_for_api.discard(user_id)