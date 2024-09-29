import sys
from typing import List
import dotenv
import json

sys.path.append(".")
sys.path.append("./src")

from src.utils import read_file
from src.core import ProcessingState, Subtitles, TimecodedText
from src.processors import editor
from pprint import pprint

dotenv.load_dotenv(dotenv_path="../../.env")

samples_dir = "../../samples"
output_dir = "../../samples/output"

video_file = samples_dir + "/sample1.mp4"
subtitle_file = samples_dir + "/sample1.json"

subtitles_json = json.loads(read_file(subtitle_file))
source_words = [
    TimecodedText(text=word["text"], start=float(word["start"]), end=float(word["end"]))
    for word in subtitles_json
]

sentences = editor.convert_words_sentences(source_words)
# selected_fragments = [sentences]  # take all, expect same video
selected_fragments = [
    sentences[0:1] + sentences[4:6],
    sentences[8:12],
]  # take all, expect same video

for output_file, clip_words in editor.compile_clips(
    input_path=video_file,
    output_dir=output_dir,
    source_words=source_words,
    selected_fragments=selected_fragments,
):

    pprint(clip_words)
