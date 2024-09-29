import sys
import dotenv

sys.path.append(".")
sys.path.append("./src")

from src.core import ProcessingState, Subtitles, TimecodedText
from src.processors import editor
from pprint import pprint

dotenv.load_dotenv(dotenv_path="../../.env")

samples_dir = "../../samples"

sample_subtitles1 = [
    TimecodedText(text="a", start=10.0, end=11.0),
    TimecodedText(text=" b1 ", start=12.0, end=13.0),
    TimecodedText(text=" b2 ", start=14.0, end=15.0),
    TimecodedText(text=" b3 .", start=16.0, end=28.0),
    TimecodedText(text=" c ", start=30.0, end=40.0),
    TimecodedText(text=" d !", start=50.0, end=60.0),
    TimecodedText(text=" e ", start=70.0, end=80.0),
]


def test_concantenate_subtitles(topic, words):
    print(f"Testing: {topic}")
    result = editor.convert_words_sentences(words)

    pprint([i.__dict__ for i in result])


# test_concantenate_subtitles(
#     "Unended",
#     sample_subtitles1,
# )

# test_concantenate_subtitles("Empty", [])

sample_file = samples_dir + "/test_video1.mp4"


state = ProcessingState()
subtitles = Subtitles()
subtitles.words = sample_subtitles1
state.source_subtitles = subtitles
state.source_video_path = sample_file

state = editor.process(state)
