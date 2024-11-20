import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Bot Configuration
BOT_VERSION = "1.0.0"
API_ID = os.getenv("API_ID")
API_HASH = os.getenv("API_HASH")
BOT_TOKEN = os.getenv("BOT_TOKEN")
TINIFY_API_KEY = os.getenv("TINIFY_API_KEY")
MONGO_URI = os.getenv("MONGO_URI")
ADMIN_ID = int(os.getenv("ADMIN_ID"))
LOG_CHANNEL_ID = int(os.getenv("LOG_CHANNEL_ID"))
ADMIN_IDS = [int(os.getenv("ADMIN_ID"))]

# Validate log channel
if not LOG_CHANNEL_ID:
    raise ValueError("LOG_CHANNEL_ID is required")

# File Configuration
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB
SUPPORTED_FORMATS = {'.webp', '.jpeg', '.jpg', '.png'}
CONVERSION_FORMATS = ["webp", "jpeg", "png"]
FORMAT_DESCRIPTIONS = {
    "webp": "Best for web images (smallest size)",
    "jpeg": "Best for photos (good quality/size balance)",
    "png": "Best for images with transparency (highest quality)"
}

# Rate Limiting
RATE_LIMIT_SECONDS = 5
USER_DATA_EXPIRY_HOURS = 24
RATE_LIMIT_CLEANUP_HOURS = 1

# Error Messages
ERROR_MESSAGES = {
    "rate_limit": "⚠️ Please wait a few seconds before trying again!",
    "file_too_large": "⚠️ File too large! Maximum size is 5MB",
    "invalid_format": "⚠️ Unsupported file format. Supported formats: JPEG, PNG, WebP",
    "invalid_image": "⚠️ Invalid image file.",
    "invalid_url": "⚠️ Invalid URL format. Please send a valid image URL.",
    "general_error": "❌ An error occurred while processing your request."
}
  