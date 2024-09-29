import logging
from typing import List
import httpx
import base64
from core import TimecodedText

logger = logging.getLogger(__name__)


class WhisperClient:
    def __init__(self, base_url: str) -> None:
        self.http = httpx.Client(base_url=base_url, timeout=3600)

    def transcribe(self, language: str, audio: bytes) -> List[TimecodedText]:
        for _ in range(3):
            try:
                return self.transcribe_attempt(language, audio)
            except Exception as ex:
                logger.error(ex)
        raise RuntimeError("Request to Wisper failed in all attempts")

    def transcribe_attempt(self, language: str, audio: bytes) -> List[TimecodedText]:
        res = self.http.post(
            "/transcribe",
            json={
                "language": language,
                "audio": base64.b64encode(audio).decode("ascii"),
            },
        )
        if httpx.codes.is_error(res.status_code):
            logger.error(f"Request to Wisper failed: code={res.status_code}")
            raise RuntimeError(
                f"Request to Wisper server failed with code {res.status_code}"
            )

        # print(f"transcription {res.json()}")
        return [
            TimecodedText(
                text=raw_word["text"], start=raw_word["start"], end=raw_word["end"]
            )
            for raw_word in res.json()
        ]
