import sys
from typing import Any, cast

from moviepy.editor import VideoFileClip

sys.path.append(".")
sys.path.append("./src")

from src.services.whisper_client import WhisperClient
from pprint import pprint


# client = WhisperClient(base_url="http://localhost:9001/")
client = WhisperClient(base_url="https://open-core.ru:9001")

samples_dir = "../../samples"


clip = VideoFileClip(samples_dir + "/long_movie_240p.mp4")
if not clip.audio:
    raise RuntimeWarning("No Audio in clip")
# https://github.com/openai/whisper/discussions/870
# converting to mono (-ac 1)
audio = cast(Any, clip.audio.subclip(1000, 2000)).write_audiofile(
    f"{samples_dir}/long_2h_whisper_audio_128k.mp3",
    fps=16000,
    bitrate="128k",
    ffmpeg_params=["-ac", "1"],
)


with open(f"{samples_dir}/long_2h_whisper_audio_128k.mp3", "rb") as file:
    audio = file.read()

result = client.transcribe("ru", audio=audio)


pprint(result)
