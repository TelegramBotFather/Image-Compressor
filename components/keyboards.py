from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from typing import List, Optional

class Keyboards:
    """Class to manage all keyboard markups for the bot."""
    
    @staticmethod
    def main_menu() -> InlineKeyboardMarkup:
        """Main menu keyboard."""
        buttons = [
            [InlineKeyboardButton("📊 My Stats", callback_data="stats")],
            [InlineKeyboardButton("🔑 API Key", callback_data="settings_api")],
            [InlineKeyboardButton("📞 Support", callback_data="support")]
        ]
        return InlineKeyboardMarkup(buttons)

    @staticmethod
    def settings_menu(has_api_key: bool = False) -> InlineKeyboardMarkup:
        """Simple settings menu keyboard."""
        buttons = [
            [InlineKeyboardButton("🔑 API Key", callback_data="settings_api")],
            [InlineKeyboardButton("« Back", callback_data="start")]
        ]
        return InlineKeyboardMarkup(buttons)

    @staticmethod
    def api_key_settings(has_api_key: bool) -> InlineKeyboardMarkup:
        """API key settings keyboard."""
        buttons = [
            [
                InlineKeyboardButton(
                    "Remove Key" if has_api_key else "Add Key",
                    callback_data="api_key_toggle"
                )
            ],
            [InlineKeyboardButton("🏠 Back to Menu", callback_data="start")]
        ]
        return InlineKeyboardMarkup(buttons)

    @staticmethod
    def confirmation_keyboard(action: str) -> InlineKeyboardMarkup:
        """Generic confirmation keyboard."""
        return InlineKeyboardMarkup([
            [
                InlineKeyboardButton("✅ Yes", callback_data=f"confirm_{action}"),
                InlineKeyboardButton("❌ No", callback_data="cancel")
            ]
        ])


    @staticmethod
    def admin_menu() -> InlineKeyboardMarkup:
        """Admin menu keyboard."""
        return InlineKeyboardMarkup([
            [
                InlineKeyboardButton("📊 Statistics", callback_data="admin_stats"),
                InlineKeyboardButton("👥 Users", callback_data="admin_users")
            ],
            [
                InlineKeyboardButton("📢 Broadcast", callback_data="admin_broadcast")
            ],
            [
                InlineKeyboardButton("🔙 Back to Main Menu", callback_data="start")
            ]
        ])

    @staticmethod
    def user_management_menu():
        """User management menu."""
        return InlineKeyboardMarkup([
            [
                InlineKeyboardButton("🚫 Banned Users", callback_data="admin_banned_users"),
                InlineKeyboardButton("📊 User Stats", callback_data="admin_user_stats")
            ],
            [
                InlineKeyboardButton("🔙 Back to Admin Menu", callback_data="admin_back")
            ]
        ])

    @staticmethod
    def admin_settings_menu():
        """Admin settings menu."""
        return InlineKeyboardMarkup([
            [
                InlineKeyboardButton("🔑 API Settings", callback_data="admin_api_settings"),
                InlineKeyboardButton("⚙️ Bot Settings", callback_data="admin_bot_settings")
            ],
            [
                InlineKeyboardButton("🔙 Back to Admin Menu", callback_data="admin_back")
            ]
        ])

    @staticmethod
    def stats_menu() -> InlineKeyboardMarkup:
        """Stats menu keyboard."""
        return InlineKeyboardMarkup([
            [InlineKeyboardButton("🏠 Back to Menu", callback_data="start")]
        ])

