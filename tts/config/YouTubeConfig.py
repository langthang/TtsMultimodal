import os
from typing import Optional
from dotenv import load_dotenv

class YouTubeConfig:
    """Configuration class for YouTube settings."""
    
    _instance = None

    def __new__(cls):
        """Implement singleton pattern."""
        if cls._instance is None:
            cls._instance = super(YouTubeConfig, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        """Initialize YouTube configuration."""
        if self._initialized:
            return
            
        # Load environment variables
        load_dotenv()
        
        # YouTube OAuth credentials
        self.client_secrets_file: str = self._get_env('YOUTUBE_CLIENT_SECRETS_FILE')
        
        # Default video settings
        self.default_privacy_status: str = self._get_env('YOUTUBE_DEFAULT_PRIVACY', 'private')
        self.default_category_id: str = self._get_env('YOUTUBE_DEFAULT_CATEGORY', '27')  # Education
        self.default_tags: list = self._parse_tags(self._get_env('YOUTUBE_DEFAULT_TAGS', ''))
        
        self._initialized = True

    def _get_env(self, key: str, default: Optional[str] = None) -> str:
        """
        Get environment variable with optional default value.
        
        Args:
            key: Environment variable key
            default: Default value if key not found
            
        Returns:
            Value of environment variable or default
        """
        value = os.getenv(key, default)
        if value is None:
            raise ValueError(f"Environment variable {key} not set and no default provided")
        return value

    def _parse_tags(self, tags_str: str) -> list:
        """
        Parse comma-separated tags string into list.
        
        Args:
            tags_str: Comma-separated string of tags
            
        Returns:
            List of tags
        """
        if not tags_str:
            return []
        return [tag.strip() for tag in tags_str.split(',') if tag.strip()]

    @property
    def is_initialized(self) -> bool:
        """Check if configuration is initialized."""
        return self._initialized 