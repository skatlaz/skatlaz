"""
Utility functions for Skatlaz AI
"""

import os
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional

# Configure logging
def setup_logger(name: str = "skatlaz") -> logging.Logger:
    """Setup logger for the application"""
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    
    # Create logs directory
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    
    # File handler
    log_file = log_dir / f"{datetime.now().strftime('%Y%m%d')}.log"
    file_handler = logging.FileHandler(log_file, encoding='utf-8')
    file_handler.setLevel(logging.INFO)
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.WARNING)
    
    # Formatter
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)
    
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    return logger

# Global logger
logger = setup_logger()

def load_config(config_path: str = None) -> dict:
    """Load configuration from file"""
    config = {}
    
    # Default config path
    if not config_path:
        config_path = os.path.expanduser("~/.skatlaz_config.json")
    
    # Load from file if exists
    if os.path.exists(config_path):
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
        except Exception as e:
            logger.error(f"Error loading config: {e}")
    
    # Environment variables override
    config["openai_api_key"] = os.getenv("OPENAI_API_KEY", config.get("openai_api_key", ""))
    config["anthropic_api_key"] = os.getenv("ANTHROPIC_API_KEY", config.get("anthropic_api_key", ""))
    config["deepseek_api_key"] = os.getenv("DEEPSEEK_API_KEY", config.get("deepseek_api_key", ""))
    config["huggingface_api_key"] = os.getenv("HUGGINGFACE_API_KEY", config.get("huggingface_api_key", ""))
    config["weather_api_key"] = os.getenv("WEATHER_API_KEY", config.get("weather_api_key", ""))
    config["google_maps_key"] = os.getenv("GOOGLE_MAPS_KEY", config.get("google_maps_key", ""))
    config["gemini_api_key"] = os.getenv("GEMINI_API_KEY", config.get("gemini_api_key", ""))
    
    return config

# Global config
config = load_config()

def save_config(config_data: dict, config_path: str = None) -> bool:
    """Save configuration to file"""
    if not config_path:
        config_path = os.path.expanduser("~/.skatlaz_config.json")
    
    try:
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(config_data, f, indent=2, ensure_ascii=False)
        logger.info(f"Config saved to {config_path}")
        return True
    except Exception as e:
        logger.error(f"Error saving config: {e}")
        return False

def sanitize_text(text: str, max_length: int = 1000) -> str:
    """Sanitize text for safe display"""
    if not text:
        return ""
    if len(text) > max_length:
        text = text[:max_length] + "..."
    return text

def format_time(seconds: float) -> str:
    """Format time in seconds to readable string"""
    if seconds < 60:
        return f"{seconds:.1f} seconds"
    elif seconds < 3600:
        minutes = seconds / 60
        return f"{minutes:.1f} minutes"
    else:
        hours = seconds / 3600
        return f"{hours:.1f} hours"

def create_directory(path: str) -> bool:
    """Create directory if it doesn't exist"""
    try:
        Path(path).mkdir(parents=True, exist_ok=True)
        return True
    except Exception as e:
        logger.error(f"Error creating directory {path}: {e}")
        return False

def extract_code_from_response(response: str) -> Optional[str]:
    """Extract code blocks from response"""
    import re
    code_pattern = r'```(\w+)?\n(.*?)```'
    matches = re.findall(code_pattern, response, re.DOTALL)
    
    if matches:
        # Return the last code block (usually the main code)
        return matches[-1][1].strip()
    return None

def truncate_prompt(prompt: str, max_length: int = 255) -> str:
    """Truncate prompt to max length"""
    if len(prompt) > max_length:
        return prompt[:max_length]
    return prompt

def is_valid_url(url: str) -> bool:
    """Check if string is a valid URL"""
    import re
    url_pattern = re.compile(
        r'^https?://'  # http:// or https://
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'  # domain...
        r'localhost|'  # localhost...
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
        r'(?::\d+)?'  # optional port
        r'(?:/?|[/?]\S+)$', re.IGNORECASE)
    return url_pattern.match(url) is not None

def get_file_extension(filename: str) -> str:
    """Get file extension from filename"""
    return Path(filename).suffix.lower()

def read_file(filepath: str) -> Optional[str]:
    """Read file content"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        logger.error(f"Error reading file {filepath}: {e}")
        return None

def write_file(filepath: str, content: str) -> bool:
    """Write content to file"""
    try:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        return True
    except Exception as e:
        logger.error(f"Error writing file {filepath}: {e}")
        return False

class Config:
    """Configuration manager class"""
    
    def __init__(self, config_path: str = None):
        self.config_path = config_path or os.path.expanduser("~/.skatlaz_config.json")
        self.data = load_config(self.config_path)
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value"""
        return self.data.get(key, default)
    
    def set(self, key: str, value: Any) -> None:
        """Set configuration value"""
        self.data[key] = value
        save_config(self.data, self.config_path)
    
    def get_api_key(self, provider: str) -> Optional[str]:
        """Get API key for specific provider"""
        key_map = {
            "openai": "openai_api_key",
            "anthropic": "anthropic_api_key",
            "deepseek": "deepseek_api_key",
            "huggingface": "huggingface_api_key",
            "weather": "weather_api_key",
            "google_maps": "google_maps_key",
            "gemini": "gemini_api_key"
        }
        return self.get(key_map.get(provider, f"{provider}_api_key"))
    
    def has_api_key(self, provider: str) -> bool:
        """Check if API key exists for provider"""
        key = self.get_api_key(provider)
        return bool(key and key.strip())

# Create global config instance
config = Config()

# Export commonly used functions
__all__ = [
    'logger',
    'config',
    'load_config',
    'save_config',
    'sanitize_text',
    'format_time',
    'create_directory',
    'extract_code_from_response',
    'truncate_prompt',
    'is_valid_url',
    'get_file_extension',
    'read_file',
    'write_file',
    'Config'
]
