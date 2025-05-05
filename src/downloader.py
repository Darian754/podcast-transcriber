import requests
from bs4 import BeautifulSoup
from pathlib import Path
from typing import Generator, Optional
import re
from config.settings import settings
from requests.exceptions import RequestException

class PodcastDownloader:
    """Handles podcast discovery and downloading from RSS feeds"""
    
    def __init__(self):
        self.download_dir = settings.DOWNLOAD_DIR
        self.download_dir.mkdir(parents=True, exist_ok=True)
        
    def _sanitize_filename(self, title: str) -> str:
        """Remove invalid characters from podcast titles"""
        return re.sub(r'[^\w\- ]', '', title).strip().replace(' ', '_')
    
    def find_episodes(self, search_term: str = "robot") -> Generator[dict, None, None]:
        """Discover episodes matching search criteria"""
        
        try:
            response = requests.get(settings.RSS_FEED_URL, timeout=10)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'xml')
            
            for item in soup.find_all('item'):
                if re.search(search_term, item.find('description').text, re.IGNORECASE):
                    yield {
                        'title': item.find('title').text,
                        'url': item.find('enclosure')['url']
                    }
                    
        except RequestException as e:
            raise PodcastDownloadError(f"RSS feed fetch failed: {str(e)}")

    def download_episode(self, url: str, title: str) -> Optional[Path]:
        """Download individual podcast episode"""
        
        filename = self.download_dir / f"{self._sanitize_filename(title)}.mp3"
        
        try:
            with requests.get(url, stream=True, timeout=15) as response:
                response.raise_for_status()
                with open(filename, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        f.write(chunk)
            return filename
            
        except RequestException as e:
            print(f"Download failed: {str(e)}")
            return None

class PodcastDownloadError(Exception):
    """Custom exception for download-related errors"""
    pass
