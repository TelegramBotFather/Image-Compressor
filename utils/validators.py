from typing import Tuple
import re
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

def validate_api_key_format(api_key: str) -> Tuple[bool, str]:
    """
    Validate the format of the TinyPNG API key.

    Args:
        api_key (str): The API key to validate.

    Returns:
        Tuple[bool, str]: Validation result and message.
    """
    if not api_key:
        return False, "API key cannot be empty"
    
    # TinyPNG API keys are typically 32 characters long consisting of letters, numbers, underscores, and hyphens.
    if not re.fullmatch(r'^[a-zA-Z0-9_-]{32}$', api_key):
        return False, "Invalid API key format"
    
    return True, "Valid API key format"

def validate_image_url(url: str) -> bool:
    """
    Validate if the provided URL points to a supported image format.

    Args:
        url (str): The URL to validate.

    Returns:
        bool: True if valid, False otherwise.
    """
    image_extensions = ('.jpg', '.jpeg', '.png', '.webp')
    url_pattern = re.compile(
        r'^(https?:\/\/)?'  # http:// or https://
        r'(([A-Za-z0-9-]+\.)+[A-Za-z]{2,6})'  # domain...
        r'(\/\S+\.(jpg|jpeg|png|webp))$',  # ...and image path
        re.IGNORECASE
    )
    
    if not url_pattern.match(url):
        return False
        
    return True

def validate_file_name(filename: str) -> bool:
    """
    Validate the file name to prevent directory traversal and other security issues.

    Args:
        filename (str): The file name to validate.

    Returns:
        bool: True if valid, False otherwise.
    """
    # Allow only alphanumeric characters, underscores, hyphens, dots, and spaces
    return bool(re.fullmatch(r'^[\w\-. ]+$', filename))