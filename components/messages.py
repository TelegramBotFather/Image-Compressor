from typing import Dict, Any
from datetime import datetime
from components.keyboards import Keyboards
from utils.helpers import format_size
from config import FORMAT_DESCRIPTIONS

class Messages:
    # Welcome messages
    WELCOME = (
        "👋 <b>Welcome to Image Compressor Bot!</b>\n\n"
        "I'm your professional image compression assistant. I can help you:\n"
        "• Compress images while maintaining quality\n"
        "• Convert between different formats (WEBP, JPEG, PNG)\n"
        "• Save storage space and bandwidth\n\n"
        "🔍 <b>Quick Start:</b>\n"
        "1️⃣ Just send me any image\n"
        "2️⃣ Use /convert to change formats\n"
        "3️⃣ Use /settings to customize\n\n"
        "🎯 <b>Pro Tip:</b> Try WEBP format for the best compression!"
    )

    HELP = (
        "ℹ️ <b>Help & Information</b>\n\n"
        "<b>Basic Commands:</b>\n"
        "• /start - Restart the bot\n"
        "• /help - Show this help message\n"
        "• /convert - Change image format\n"
        "• /settings - Bot settings\n"
        "• /stats - View your usage stats\n\n"
        "<b>How to Use:</b>\n"
        "1. Send any image or photo\n"
        "2. Choose compression options\n"
        "3. Receive compressed image\n\n"
        "<b>Supported Formats:</b>\n"
        "• WEBP - Best for web images\n"
        "• JPEG - Best for photos\n"
        "• PNG - Best for transparency\n\n"
        "<b>Size Limits:</b>\n"
        "• Maximum file size: 5MB\n\n"
        "Need more help? Use /support"
    )

    ERROR_PROCESSING = (
        "❌ <b>Processing Error</b>\n\n"
        "Sorry, I couldn't process your image.\n"
        "Please try again or contact support if the issue persists.\n\n"
        "Common solutions:\n"
        "• Check file format\n"
        "• Ensure file size < 5MB\n"
        "• Try a different image"
    )

    PROCESSING = (
        "⚙️ <b>Processing Your Image</b>\n\n"
        "🔄 Optimizing and compressing...\n"
        "Please wait a moment!"
    )

    SUCCESS = "✅ Image processed successfully!"
    RATE_LIMIT = "⚠️ Please wait before sending another image."

    FORMAT_SELECTION = (
        "🔄 <b>Format Selection</b>\n\n"
        "Choose the output format for your image:\n\n"
        f"📱 <b>WEBP</b>\n• {FORMAT_DESCRIPTIONS['webp']}\n\n"
        f"📸 <b>JPEG</b>\n• {FORMAT_DESCRIPTIONS['jpeg']}\n\n"
        f"🎨 <b>PNG</b>\n• {FORMAT_DESCRIPTIONS['png']}\n\n"
        "ℹ️ Your choice will be remembered for future conversions."
    )

    SUPPORT = (
        "💬 <b>Support & Contact</b>\n\n"
        "Need help? Have suggestions? Found a bug?\n\n"
        "📮 <b>Contact Options:</b>\n"
        "• Report issues: @YourSupportChannel\n"
        "• Feature requests: @YourSupportGroup\n"
        "• Updates: @YourUpdateChannel\n\n"
        "⚡️ <b>Quick Links:</b>\n"
        "• FAQ: /help\n"
        "• Settings: /settings\n"
        "• Statistics: /stats\n\n"
        "We typically respond within 24 hours!"
    )

    SETTINGS_MENU = (
        "⚙️ <b>Bot Settings</b>\n\n"
        "<b>Current Configuration:</b>\n"
        "• Default Format: {default_format}\n"
        "• Custom API Key: {api_status}\n"
        "• Notifications: {notifications}\n\n"
        "<b>What would you like to configure?</b>"
    )

    @staticmethod
    def get_stats(stats: dict) -> str:
        return (
            "📊 <b>Your Usage Statistics</b>\n\n"
            "📅 <b>Today's Activity:</b>\n"
            f"├ Files Processed: {stats['today_files']}\n"
            f"├ Data Processed: {format_size(stats['today_size'])}\n"
            f"└ Compression Ratio: {stats.get('today_ratio', '0')}%\n\n"
            "🔄 <b>Total Activity:</b>\n"
            f"├ Total Files: {stats['total_files']}\n"
            f"├ Total Data: {format_size(stats['total_size'])}\n"
            f"└ Average Ratio: {stats.get('avg_ratio', '0')}%\n\n"
            "💡 Keep compressing to improve your stats!"
        )

    @staticmethod
    def get_compression_result(original_size: int, compressed_size: int) -> str:
        reduction = ((original_size - compressed_size) / original_size) * 100
        saved_space = original_size - compressed_size
        
        return (
            "✅ <b>Compression Complete!</b>\n\n"
            f"📁 Original Size: {format_size(original_size)}\n"
            f"📦 Compressed Size: {format_size(compressed_size)}\n"
            f"📊 Size Reduction: {reduction:.1f}%\n"
            f"💾 Space Saved: {format_size(saved_space)}\n\n"
            "🎯 <b>Want to try different formats?</b>\n"
            "Use /convert to explore other options!"
        )
