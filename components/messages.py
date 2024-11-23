from typing import Dict, Any
from datetime import datetime
from components.keyboards import Keyboards
from utils import format_size

class Messages:
    """Class containing all bot messages."""
    
    WELCOME = (
        "👋 <b>Image Compressor Bot</b>\n\n"
        "Send me any image to compress it.\n"
        "Max file size: 5MB"
    )

    HELP = (
        "ℹ️ <b>Quick Help</b>\n\n"
        "1. Send an image\n"
        "2. Get compressed version\n\n"
        "Commands:\n"
        "/start - Start bot\n"
        "/stats - View stats\n"
        "/settings - Bot settings"
    )

    PROCESSING = "⚙️ Compressing..."
    SUCCESS = "✅ Done!"
    RATE_LIMIT = "⚠️ Please wait a moment."

    @staticmethod
    def get_compression_result(original_size: int, compressed_size: int) -> str:
        reduction = ((original_size - compressed_size) / original_size) * 100
        saved_space = original_size - compressed_size
        
        return (
            "✅ <b>Compression Complete!</b>\n\n"
            f"📁 Original Size: {format_size(original_size)}\n"
            f"📦 Compressed Size: {format_size(compressed_size)}\n"
            f"📊 Size Reduction: {reduction:.1f}%\n"
            f"💾 Space Saved: {format_size(saved_space)}"
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
