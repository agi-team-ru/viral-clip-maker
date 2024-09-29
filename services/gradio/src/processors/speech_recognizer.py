import logging
import os
from moviepy.editor import VideoFileClip
import tempfile
from core import ProcessingState, Subtitles
from services.whisper_client import WhisperClient

whisper_client = WhisperClient(os.environ["WHISPER_BASE_URL"])

logger = logging.getLogger(__name__)


def process(state: ProcessingState) -> ProcessingState:
    if not state.source_video_path:
        logger.warning("No source video provided")
        return state
    if not state.user_preferences:
        logger.warning("No user preferences provided")
        return state

    with tempfile.NamedTemporaryFile(suffix=".mp3") as tmp:

        clip = VideoFileClip(state.source_video_path)
        if not clip.audio:
            raise RuntimeWarning("No Audio in clip")
        # https://github.com/openai/whisper/discussions/870
        # converting to mono (-ac 1)
        audio = clip.audio.write_audiofile(
            tmp.name, fps=16000, bitrate="128k", ffmpeg_params=["-ac", "1"]
        )

        with open(tmp.name, "rb") as file:
            audio = file.read()

    language = state.user_preferences.language

    subtitles = Subtitles()
    subtitles.words = whisper_client.transcribe(language=language, audio=audio)

    state.source_subtitles = subtitles
    return state
