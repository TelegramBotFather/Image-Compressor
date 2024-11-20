from typing import Dict, Any
from datetime import datetime
from components.keyboards import Keyboards

class Messages:
    # Welcome messages
    WELCOME = """
👋 Welcome to Image Compressor Pro!

I can help you:
🔹 Compress images while maintaining quality
🔹 Convert between formats (JPEG, PNG, WebP)
🔹 Process images from URLs
🔹 Track your compression statistics

Send me an image to start!
"""

    HELP = """
📖 <b>How to use Image Compressor Pro:</b>

1️⃣ <b>Compress Image:</b>
   • Send or forward any image
   • Send an image URL
   • Supported formats: JPEG, PNG, WebP

2️⃣ <b>Convert Format:</b>
   • Use /convert command
   • Choose target format
   • Send your image

3️⃣ <b>Commands:</b>
   /start - Start the bot
   /settings - Configure settings
   /stats - View your statistics
   /convert - Convert image format
   /help - Show this help

4️⃣ <b>Tips:</b>
   • Max file size: 5MB
   • Best quality: PNG
   • Smallest size: WebP
   • Web-friendly: JPEG
"""

    ERROR_PROCESSING = "❌ Error processing image. Please try again."
    PROCESSING = "🔄 Processing your image..."
    SUCCESS = "✅ Image processed successfully!"
    RATE_LIMIT = "⚠️ Please wait before sending another image."

    @staticmethod
    def get_stats_message(stats: Dict[str, Any]) -> str:
        """Format statistics message."""
        return f"""
📊 <b>Your Usage Statistics</b>

Today's Usage:
├ Files: {stats.get('today_files', 0)}
└ Data: {stats.get('today_size', 0)/1024/1024:.2f} MB

Total Usage:
├ Files: {stats.get('total_files', 0)}
└ Data: {stats.get('total_size', 0)/1024/1024:.2f} MB

Last Used: {stats.get('last_used', datetime.now()).strftime('%Y-%m-%d %H:%M:%S')}
"""

    @staticmethod
    def get_compression_result(original_size: int, compressed_size: int) -> str:
        saved = original_size - compressed_size
        saved_percent = (saved / original_size) * 100 if original_size > 0 else 0
        return f"""
✅ Image Compressed Successfully!

📊 Results:
├ Original: {original_size/1024:.1f} KB
├ Compressed: {compressed_size/1024:.1f} KB
└ Saved: {saved/1024:.1f} KB ({saved_percent:.1f}%)
"""
