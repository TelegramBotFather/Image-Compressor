from typing import Optional, Tuple, List
import os
from datetime import datetime
import logging
from PIL import Image
import aiohttp
import aiofiles
from config import MAX_FILE_SIZE, SUPPORTED_FORMATS

logger = logging.getLogger(__name__)

async def get_image_info(file_path: str) -> Tuple[bool, dict]:
    """Get image information."""
    try:
        with Image.open(file_path) as img:
            info = {
                'format': img.format.lower(),
                'size': os.path.getsize(file_path),
                'dimensions': img.size
            }
            return True, info
    except Exception as e:
        logger.error(f"Error getting image info: {str(e)}")
        return False, {}

async def download_image(url: str, save_path: str) -> Tuple[bool, Optional[str]]:
    """Download image from URL."""
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                if response.status != 200:
                    return False, "Failed to download image"

                content_length = response.headers.get('Content-Length')
                if content_length and int(content_length) > MAX_FILE_SIZE:
                    return False, "File too large"

                async with aiofiles.open(save_path, mode='wb') as f:
                    async for chunk in response.content.iter_chunked(8192):
                        await f.write(chunk)

        return True, None
    except Exception as e:
        logger.error(f"Error downloading image: {str(e)}")
        return False, str(e)

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