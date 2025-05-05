import requests
import time
from pathlib import Path
from typing import Optional, Dict
from config.settings import settings
from requests.exceptions import RequestException

class PodcastTranscriber:
    """Handles audio file transcription using AssemblyAI API"""
    
    def __init__(self):
        self.transcripts_dir = settings.TRANSCRIPTS_DIR
        self.transcripts_dir.mkdir(parents=True, exist_ok=True)
        self.headers = {"authorization": settings.ASSEMBLYAI_API_KEY}
        
    def _upload_file(self, file_path: Path) -> str:
        """Chunked file upload to AssemblyAI"""
        
        def read_chunks():
            with open(file_path, "rb") as f:
                while chunk := f.read(5242880):
                    yield chunk
        
        try:
            response = requests.post(
                "https://api.assemblyai.com/v2/upload",
                headers=self.headers,
                data=read_chunks()
            )
            response.raise_for_status()
            return response.json()["upload_url"]
            
        except RequestException as e:
            raise TranscriptionError(f"File upload failed: {str(e)}")

    def transcribe_segment(self, file_path: Path) -> Optional[Path]:
        """Transcribe specific audio segment with progress tracking"""
        
        try:
            audio_url = self._upload_file(file_path)
            
            transcript = requests.post(
                "https://api.assemblyai.com/v2/transcript",
                headers=self.headers,
                json={
                    "audio_url": audio_url,
                    "speech_model": "slam-1",
                    "audio_start_from": settings.SEGMENT_START_MS,
                    "audio_end_at": settings.SEGMENT_END_MS
                }
            ).json()
            
            return self._poll_transcription(transcript['id'])
            
        except Exception as e:
            print(f"Transcription failed: {str(e)}")
            return None

    def _poll_transcription(self, transcript_id: str) -> Path:
        """Poll for transcription completion"""
        
        while True:
            try:
                result = requests.get(
                    f"https://api.assemblyai.com/v2/transcript/{transcript_id}",
                    headers=self.headers
                ).json()
                
                if result["status"] == "completed":
                    return self._save_transcript(transcript_id, result["text"])
                elif result["status"] == "error":
                    raise TranscriptionError(result.get("error", "Unknown error"))
                
                time.sleep(5)
                
            except RequestException as e:
                raise TranscriptionError(f"Polling error: {str(e)}")

    def _save_transcript(self, transcript_id: str, text: str) -> Path:
        """Save transcript to designated directory"""
        
        filename = self.transcripts_dir / f"{transcript_id}.txt"
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(text)
        return filename

class TranscriptionError(Exception):
    """Custom exception for transcription failures"""
    pass
