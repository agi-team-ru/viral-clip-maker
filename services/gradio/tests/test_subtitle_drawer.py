import sys
from PIL import ImageFont
import cv2
import dotenv
import shutil

sys.path.append(".")
sys.path.append("./src")

from src.core import (
    ProcessingState,
    ResultVideo,
    Subtitles,
    UserPreferences,
    TimecodedText,
)
from src.constants import FONTS_DIR
from src.processors import subtitler
from pprint import pprint

dotenv.load_dotenv(dotenv_path="../../.env")

samples_dir = "../../samples"


word_group = subtitler.WordGroup()
word_group.words = [
    TimecodedText(text="Hello, ", start=10.0, end=11.0),
    TimecodedText(text=" world!", start=12.0, end=13.0),
    TimecodedText(text="How is", start=14.0, end=15.0),
    TimecodedText(text=" it", start=16.0, end=28.0),
    TimecodedText(text=" going? ", start=30.0, end=40.0),
    TimecodedText(text=" Let's", start=50.0, end=60.0),
    TimecodedText(text="  see   ", start=70.0, end=90.0),
]

# print(subtitler.join_words(word_group.words))


# def text_split_into_lines(descr: str, words, max_width: float):
#     print(f"TEST: {descr}\n=============")
#     lines = subtitler.split_words_into_lines(
#         word_group.words, font=font, max_width=max_width
#     )
#     pprint(lines)


# text_split_into_lines("Very small box", word_group.words, max_width=1)
# text_split_into_lines("Medium box", word_group.words, max_width=100)
# text_split_into_lines("Very big box", word_group.words, max_width=10000)


font_size = 32
font = ImageFont.truetype(FONTS_DIR + "/nunito.ttf", font_size)
frame = cv2.imread(samples_dir + "/frame_p720_gray.png")
frame = subtitler.draw_subtitles_on_frame(
    font=font,
    frame=frame,
    user_preferences=UserPreferences(),
    word_group=word_group,
    current_time=10.5,
)
cv2.imwrite(samples_dir + "/frame_p720_gray_result.png", frame)
