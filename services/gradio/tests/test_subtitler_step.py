import sys
import dotenv
import shutil

sys.path.append(".")
sys.path.append("./src")

from src.core import ProcessingState, ResultVideo, Subtitles, UserPreferences, TimecodedText
from src.processors import subtitler
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
    TimecodedText(text=" very long duration ", start=70.0, end=90.0),
]

sample_subtitles2 = [
    TimecodedText(text="Hello, World", start=0.0, end=0.5),
    TimecodedText(text="aaaooo ccceee ccceee ccceee", start=0.5, end=1.0),
    TimecodedText(text="hello, world, world", start=1.0, end=1.5),
    TimecodedText(text="aaaooo ccceee ccceee", start=1.5, end=2.0),
    TimecodedText(text="hello, world!", start=3.0, end=4.0),
]

def test_concantenate_subtitles(topic, words, frame_duration: float):
    print(f"Testing: {topic}")
    res = subtitler.group_words_in_time_frames(words, frame_duration)
    pprint(
        [
            {"words": [word.__dict__ for word in group.words], "group": group.__dict__}
            for group in res
        ]
    )


# test_concantenate_subtitles("Empty worlds", [], 0.1)

# test_concantenate_subtitles("Small frame", sample_subtitles1, 0.1)

# test_concantenate_subtitles("Middle size frame", sample_subtitles1, 10.0)

# test_concantenate_subtitles("Very big frame", sample_subtitles1, 100000.0)


sample_file = samples_dir + "/0.mp4"
sample_file_copy = samples_dir + "/0-copy.mp4"
shutil.copy(sample_file, sample_file_copy)


state = ProcessingState()
subtitles = Subtitles()
subtitles.words = sample_subtitles1
res_subtitles = Subtitles()
res_subtitles.words = sample_subtitles2
state.result = [ResultVideo(path=sample_file_copy, subtitles=res_subtitles)]
state.source_subtitles = subtitles
state.user_preferences = UserPreferences()


state = subtitler.process(state)


print(state)
