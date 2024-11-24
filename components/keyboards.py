from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from typing import List, Optional

class Keyboards:
    """Class to manage all keyboard markups for the bot."""
    
    @staticmethod
    def main_menu() -> InlineKeyboardMarkup:
        """Main menu keyboard."""
        buttons = [
            [InlineKeyboardButton("📊 My Stats", callback_data="stats")],
            [InlineKeyboardButton("⚙️ Settings", callback_data="settings")],
            [InlineKeyboardButton("📞 Support", callback_data="support")],
            [InlineKeyboardButton("❓ Help", callback_data="help")]
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
        """Simple API key settings keyboard."""
        buttons = [
            [
                InlineKeyboardButton(
                    "Remove Key" if has_api_key else "Add Key",
                    callback_data="api_key_toggle"
                )
            ],
            [InlineKeyboardButton("« Back", callback_data="settings")]
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
    def help_menu() -> InlineKeyboardMarkup:
        """Help menu keyboard."""
        return InlineKeyboardMarkup([
            [
                InlineKeyboardButton(
                    "📱 Contact Support",
                    url="https://t.me/YourSupportUsername"
                )
            ],
            [
                InlineKeyboardButton(
                    "📖 Commands List",
                    callback_data="help_commands"
                )
            ],
            [
                InlineKeyboardButton("🏠 Back to Menu", callback_data="start")
            ]
        ])

    @staticmethod
    def admin_panel() -> InlineKeyboardMarkup:
        """Admin panel keyboard."""
        return InlineKeyboardMarkup([
            [
                InlineKeyboardButton("📊 Statistics", callback_data="admin_stats"),
                InlineKeyboardButton("📢 Broadcast", callback_data="admin_broadcast")
            ],
            [
                InlineKeyboardButton("👥 Users", callback_data="admin_users"),
                InlineKeyboardButton("⚙️ Settings", callback_data="admin_settings")
            ],
            [
                InlineKeyboardButton("🏠 Main Menu", callback_data="start")
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

