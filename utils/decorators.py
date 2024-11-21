from functools import wraps
from typing import Callable, Any
from pyrogram.types import Message
from pyrogram import Client
from datetime import datetime
from config import ADMIN_IDS, RATE_LIMIT_SECONDS
import logging

logger = logging.getLogger(__name__)

def admin_only(func: Callable) -> Callable:
    """Decorator to restrict command to admin only."""
    @wraps(func)
    async def wrapper(client: Client, message: Message, *args: Any, **kwargs: Any) -> Any:
        if message.from_user.id not in ADMIN_IDS:
            await message.reply_text("⚠️ This command is restricted to admin(s) only!")
            logger.warning(f"Unauthorized access attempt by user_id: {message.from_user.id}")
            return
        return await func(client, message, *args, **kwargs)
    return wrapper

def rate_limit(func: Callable) -> Callable:
    """Rate limiting decorator."""
    last_called = {}
    
    @wraps(func)
    async def wrapper(client: Client, message: Message, *args: Any, **kwargs: Any) -> Any:
        if not isinstance(message, Message):
            return await func(client, message, *args, **kwargs)
            
        user_id = message.from_user.id
        current_time = datetime.now()
        
        if user_id in last_called:
            time_passed = (current_time - last_called[user_id]).total_seconds()
            if time_passed < RATE_LIMIT_SECONDS:
                await message.reply_text(
                    f"⚠️ Please wait {int(RATE_LIMIT_SECONDS - time_passed)} seconds."
                )
                logger.info(f"Rate limit hit for user {user_id}")
                return
        
        last_called[user_id] = current_time
        return await func(client, message, *args, **kwargs)
    return wrapper

def handle_errors(func: Callable) -> Callable:
    """Error handling decorator."""
    @wraps(func)
    async def wrapper(client: Client, message: Message, *args: Any, **kwargs: Any) -> Any:
        try:
            return await func(client, message, *args, **kwargs)
        except Exception as e:
            logger.error(f"Error in {func.__name__}: {str(e)}", exc_info=True)
            await message.reply_text("❌ An error occurred. Please try again.")
    return wrapper