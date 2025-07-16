import os
from typing import Optional, Tuple
from dotenv import load_dotenv

class AppConfig:
    """Application configuration class that manages environment variables and app settings."""
    
    _instance = None

    def __new__(cls):
        """Implement singleton pattern."""
        if cls._instance is None:
            cls._instance = super(AppConfig, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        """Initialize the configuration if not already initialized."""
        if self._initialized:
            return
            
        # Load environment variables from .env file
        load_dotenv()

        # Get project root directory
        self.project_root = self._get_project_root()
        
        # Google Cloud credentials
        self.google_credentials: str = self._get_env('GOOGLE_APPLICATION_CREDENTIALS')
        
        # TTS Configuration
        self.default_language: str = self._get_env('DEFAULT_LANGUAGE', 'English')
        self.default_speaker: str = self._get_env('DEFAULT_SPEAKER', 'neutral')
        
        # Audio Configuration
        self.audio_format: str = self._get_env('AUDIO_FORMAT', 'mp3')
        self.audio_quality: str = self._get_env('AUDIO_QUALITY', 'high')
        self.text_to_audio_codec: str = self._get_env('TEXT_TO_AUDIO_CODEC', 'aac')
        self.merged_audio_codec: str = self._get_env('MERGED_AUDIO_CODEC', 'aac')
        
        # Video Configuration
        self.video_format: str = self._get_env('VIDEO_FORMAT', 'mp4')
        self.video_fps: int = int(self._get_env('VIDEO_FPS', '30'))
        self.merged_video_fps: int = int(self._get_env('MERGED_VIDEO_FPS', '30'))
        self.image_to_video_codec: str = self._get_env('IMAGE_TO_VIDEO_CODEC', 'libx264')
        self.merged_video_codec: str = self._get_env('MERGED_VIDEO_CODEC', 'libx264')
        self.video_batch_size: int = int(self._get_env('VIDEO_BATCH_SIZE', '6'))
        self.use_v2_merge: bool = self._get_env('USE_V2_MERGE', 'false').lower() == 'true'
        self.use_v2_merge_all: bool = self._get_env('USE_V2_MERGE_ALL', 'false').lower() == 'true'
        
        # Background Music Configuration
        self.enable_background_music: bool = self._get_env('ENABLE_BACKGROUND_MUSIC', 'false').lower() == 'true'
        self.background_music_file = self._get_env('BACKGROUND_MUSIC_FILE', "NONE")
        self.background_music_volume = float(self._get_env('BACKGROUND_MUSIC_VOLUME', '0.15'))
        
        # Path Configuration
        self.output_dir: str = self._get_env('OUTPUT_DIR', os.path.join(self.project_root, 'data'))
        self.temp_dir: str = self._get_env('TEMP_DIR', os.path.join(self.project_root, 'temp'))
        self.conversations_background: str = self._get_env('CONVERSATIONS_BACKGROUND', os.path.join(self.project_root, 'data', 'background.jpg'))
        self.new_words_background: str = self._get_env('NEW_WORDS_BACKGROUND', os.path.join(self.project_root, 'data', 'background.jpg'))

        # Slide Generation Configuration
        self.slide_generation_mode_pdf: bool = self._get_env('SLIDE_GENERATION_MODE_PDF', 'false').lower() == 'true'
        self.slide_title_font_size: int = int(self._get_env('SLIDE_TITLE_FONT_SIZE', '26'))
        self.slide_content_font_size: int = int(self._get_env('SLIDE_CONTENT_FONT_SIZE', '24'))
        self.slide_title_font_name: str = self._get_env('SLIDE_TITLE_FONT_NAME', 'Avenir')
        self.slide_content_font_name: str = self._get_env('SLIDE_CONTENT_FONT_NAME', 'Avenir')
        self.slide_content_font_color: Tuple[int, int, int] = self._parse_rgb_color(
            self._get_env('SLIDE_CONTENT_FONT_COLOR', '255,255,255')
        )
        self.slide_title_font_color: Tuple[int, int, int] = self._parse_rgb_color(
            self._get_env('SLIDE_TITLE_FONT_COLOR', '255,255,255')
        )
        self.slide_text_background_color: Tuple[int, int, int] = self._parse_rgb_color(
            self._get_env('SLIDE_TEXT_BACKGROUND_COLOR', '166, 214, 214')
        )
        
        self.enable_slide_title: bool = self._get_env('ENABLE_SLIDE_TITLE', 'true').lower() == 'true'
        self.database_name: str = self._get_env('MONGODB_DATABASE', 'daily-conversation')

        self._initialized = True

    def _get_project_root(self) -> str:
        """Get the absolute path to the project root directory."""
        # Get the directory containing the current file (tts/AppConfig.py)
        current_dir = os.path.dirname(os.path.abspath(__file__))
        # Go up one level to get to the project root
        return os.path.dirname(current_dir)

    def _get_env(self, key: str, default: Optional[str] = None) -> str:
        """
        Get environment variable with optional default value.
        Raises ValueError if no default provided and variable not found.
        """
        value = os.getenv(key, default)
        if value is None:
            raise ValueError(f"Environment variable {key} not set and no default provided")
        return value
    
    def _parse_rgb_color(self, rgb_str: str) -> Tuple[int, int, int]:
        """
        Parse RGB color string in format 'R,G,B' to tuple of integers.
        Each value should be between 0 and 255.
        """
        try:
            r, g, b = map(int, rgb_str.split(','))
            if not all(0 <= x <= 255 for x in (r, g, b)):
                raise ValueError("RGB values must be between 0 and 255")
            return (r, g, b)
        except ValueError as e:
            print(f"Invalid RGB color format: {rgb_str}. Using default white color.")
            return (255, 255, 255)

    @property
    def is_initialized(self) -> bool:
        """Check if the configuration has been initialized."""
        return self._initialized 