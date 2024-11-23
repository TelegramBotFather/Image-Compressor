from typing import Optional, Tuple, List
import os
from datetime import datetime, timedelta
import logging
from PIL import Image
import aiohttp
import aiofiles
from config import MAX_FILE_SIZE, SUPPORTED_FORMATS, USER_DATA_EXPIRY_HOURS, RATE_LIMIT_CLEANUP_HOURS
from database.mongodb import db

logger = logging.getLogger(__name__)

async def clean_temp_files(file_paths: List[str]) -> None:
    """Clean up temporary files."""
    for path in file_paths:
        try:
            if path and os.path.exists(path):
                os.remove(path)
                logger.info(f"Deleted temporary file: {path}")
        except Exception as e:
            logger.error(f"Error deleting file {path}: {str(e)}")

def format_size(size_bytes: int) -> str:
    """Format file size to human readable format."""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024:
            return f"{size_bytes:.2f} {unit}"
        size_bytes /= 1024
    return f"{size_bytes:.2f} TB"

async def cleanup_old_data():
    """Clean up old data from the database periodically."""
    try:
        # Calculate cutoff times
        usage_cutoff = datetime.utcnow() - timedelta(hours=USER_DATA_EXPIRY_HOURS)
        rate_limit_cutoff = datetime.utcnow() - timedelta(hours=RATE_LIMIT_CLEANUP_HOURS)

        # Clean up old usage stats
        result = await db.usage_stats.delete_many({
            "timestamp": {"$lt": usage_cutoff}
        })
        logger.info(f"Cleaned up {result.deleted_count} old usage stats")

        # Clean up old rate limit records
        result = await db.rate_limits.delete_many({
            "timestamp": {"$lt": rate_limit_cutoff}
        })
        logger.info(f"Cleaned up {result.deleted_count} old rate limit records")

        # Clean up old logs
        result = await db.logs.delete_many({
            "timestamp": {"$lt": usage_cutoff}
        })
        logger.info(f"Cleaned up {result.deleted_count} old logs")

        # Clean up temporary files in temp directory
        temp_dir = "temp"
        file_paths = []
        for filename in os.listdir(temp_dir):
            if filename != ".gitkeep":  # Skip .gitkeep file
                file_path = os.path.join(temp_dir, filename)
                file_paths.append(file_path)
        
        if file_paths:
            await clean_temp_files(file_paths)

    except Exception as e:
        logger.error(f"Error during cleanup: {str(e)}")

def get_image_info(file_path: str) -> Optional[Tuple[str, int, int]]:
    """
    Get image format and dimensions.
    
    Args:
        file_path (str): Path to image file
        
    Returns:
        Optional[Tuple[str, int, int]]: Format, width, height or None if error
    """
    try:
        with Image.open(file_path) as img:
            return img.format.lower(), img.width, img.height
    except Exception as e:
        logger.error(f"Error getting image info: {str(e)}")
        return None