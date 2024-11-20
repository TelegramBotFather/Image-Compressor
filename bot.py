import os
import asyncio
import logging
from pyrogram import Client, filters
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from dotenv import load_dotenv
import tinify
from utils.helpers import clean_temp_files
from utils.decorators import rate_limit
from commands import (
    start_command,
    admin_dashboard,
    usage_stats,
    convert_command,
    broadcast_command,
    ban_user,
    unban_user,
    banned_users_list,
    settings_command,
    support_command
)
from config import (
    ERROR_MESSAGES,
    RATE_LIMIT_SECONDS,
    LOG_CHANNEL_ID,
    BOT_VERSION
)
from database.mongodb import db
from handlers.file_handler import FileHandler
from handlers.button_handlers import ButtonHandler
from datetime import datetime
from log_handlers.channel_logger import ChannelLogger
from components.keyboards import Keyboards

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Validate environment variables
required_vars = [
    "API_ID", 
    "API_HASH", 
    "BOT_TOKEN", 
    "TINIFY_API_KEY", 
    "MONGO_URI", 
    "ADMIN_ID",
    "LOG_CHANNEL_ID"
]
missing_vars = [var for var in required_vars if not os.getenv(var)]
if missing_vars:
    raise ValueError(f"Missing required environment variables: {', '.join(missing_vars)}")

# Initialize bot
app = Client(
    "image_compressor_bot",
    api_id=os.getenv("API_ID"),
    api_hash=os.getenv("API_HASH"),
    bot_token=os.getenv("BOT_TOKEN")
)

# Initialize handlers
file_handler = FileHandler(app)
button_handler = ButtonHandler(app)

# Initialize TinyPNG
tinify.key = os.getenv("TINIFY_API_KEY")

# Initialize scheduler
scheduler = AsyncIOScheduler()
scheduler.add_job(cleanup_old_data, 'interval', hours=1)

async def start_bot():
    """Initialize bot and verify configurations."""
    try:
        # Initialize MongoDB indexes
        await db.init_indexes()
        
        # Start the bot
        await app.start()
        
        # Verify log channel
        log_channel_id = os.getenv("LOG_CHANNEL_ID")
        if not log_channel_id.startswith("-100"):
            raise ValueError("LOG_CHANNEL_ID must start with -100")
            
        # Send startup message
        await app.send_message(
            int(log_channel_id),
            f"🟢 Bot Started\nVersion: {BOT_VERSION}\n"
            f"Start Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        )
        
        # Start scheduler
        scheduler.start()
        
        logger.info("Bot started successfully!")
        
    except Exception as e:
        logger.error(f"Failed to start bot: {str(e)}")
        raise e

# Register command handlers
app.add_handler(filters.command("start"), start_command)
app.add_handler(filters.command("help"), support_command)
app.add_handler(filters.command("settings"), settings_command)
app.add_handler(filters.command("convert"), convert_command)
app.add_handler(filters.command("broadcast"), broadcast_command)
app.add_handler(filters.command("ban"), ban_user)
app.add_handler(filters.command("unban"), unban_user)
app.add_handler(filters.command("banned_users"), banned_users_list)
app.add_handler(filters.command("admin"), admin_dashboard)
app.add_handler(filters.command("stats"), usage_stats)

# Register message handlers
file_handler = FileHandler(app)
button_handler = ButtonHandler(app)

app.add_handler(filters.photo | filters.document, file_handler.handle)
app.add_handler(filters.callback_query, button_handler.handle)

if __name__ == "__main__":
    try:
        app.run(start_bot)
    except Exception as e:
        logger.error(f"Bot crashed: {str(e)}")