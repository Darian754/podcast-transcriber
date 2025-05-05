from pathlib import Path
from typing import Optional
from pydantic import BaseSettings, Field

class Settings(BaseSettings):
    """Application settings using environment variables"""
    
    ASSEMBLYAI_API_KEY: str = Field(..., env="ASSEMBLY_AI_KEY")
    RSS_FEED_URL: str = "https://lexfridman.com/feed/podcast/"     #selected RSS feed
    DOWNLOAD_DIR: Path = Path("./downloads").resolve()
    TRANSCRIPTS_DIR: Path = Path.home() / "Desktop/transcripts"
    MAX_EPISODES: int = 5
    SEGMENT_START_MS: int = 60000  # 1 minute
    SEGMENT_END_MS: int = 180000   # 3 minutes
    
    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()
