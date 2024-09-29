import sys
from typing import List
import dotenv
import json
import shutil

sys.path.append(".")
sys.path.append("./src")

from src.utils import read_file
from src.core import (
    AspectRatio,
    ProcessingState,
    ResultVideo,
    Subtitles,
    TimecodedText,
    UserPreferences,
)
from src.processors import editor, subtitler, cropper, scene_recognizer
from pprint import pprint
import random

dotenv.load_dotenv(dotenv_path="../../.env")

samples_dir = "../../samples"
output_dir = "../../samples/output"

video_file = samples_dir + "/sample_dialog_short.mp4"
subtitle_file = samples_dir + "/sample1.json"

subtitles_json = json.loads(read_file(subtitle_file))
source_words = [
    TimecodedText(text=word["text"], start=float(word["start"]), end=float(word["end"]))
    for word in subtitles_json
]


def create_state(
    source_video: str, source_words: List[TimecodedText]
) -> ProcessingState:
    video_file_copy = f"{samples_dir}/output/tmp_{random.random()}.mp4"
    shutil.copy(video_file, video_file_copy)

    state = ProcessingState()
    state.source_video_path = source_video
    state.source_subtitles = Subtitles()
    state.source_subtitles.words = source_words

    res_subtitles = Subtitles()
    res_subtitles.words = source_words
    state.result = [ResultVideo(path=video_file_copy, subtitles=res_subtitles)]
    state.user_preferences = UserPreferences()
    state.user_preferences.aspect_ratio = AspectRatio.VERTICAL

    return state


state = create_state(source_video=video_file, source_words=source_words)


# state = subtitler.process(state)
state = scene_recognizer.process(state)
state = cropper.process(state)


# pprint(selected_fragments)
