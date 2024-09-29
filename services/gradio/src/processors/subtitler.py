import os
import logging
import re
from typing import Any, List, Optional, cast
from PIL import Image, ImageDraw, ImageFont
import cv2
from cv2.typing import MatLike
from core import ProcessingState, ResultVideo, UserPreferences, TimecodedText
from vidgear.gears import CamGear, WriteGear
import moviepy.editor as mpe
import numpy as np

logger = logging.getLogger(__name__)
from constants import FONTS_DIR
import pathlib

SPACE_REGEX = r"\s+"
SUBTITLE_FRAME_DURATION = 2.5

FONT_SIZE_TO_WIDTH_RATIO = 1.0 / 20.0
SUBTITLE_REL_POS = (0.5, 0.66)  # (x, y) percents
SUBTITLE_BOX_MAX_WIDTH = 0.75  # percents
SUBTITLE_LINE_SPACING = 1.5  # relative to line height
BG_RADIUS_RATIO = 0.25  # relative to line height
BG_PADDING_RATIO = 0.1  # relative to line height
# Colors
COLOR_FG = (76, 201, 240)
COLOR_BG = (114, 9, 183)
COLOR_HIGHLIGHT = (247, 37, 133)


class WordGroup:
    def __init__(self) -> None:
        self.words: List[TimecodedText] = []
        self.start = 0.0
        self.end = 0.0


def process(state: ProcessingState) -> ProcessingState:
    if not state.result:
        logger.warning("No result provided")
        return state
    if not state.user_preferences:
        logger.warning("No user preferences provided")
        return state

    for video in state.result:
        cam_gear = CamGear(source=cast(Any, video.path)).start()
        base_src_path, _ = os.path.splitext(video.path)
        output_path = f"{base_src_path}_subtitled.mp4"

        try:
            process_clip(
                cam_gear=cam_gear,
                video=video,
                user_preferences=state.user_preferences,
                output_path=output_path,
            )
        finally:
            cam_gear.stop()

        apply_audio(video.path, output_path)

        pathlib.Path.unlink(pathlib.Path(video.path))
        video.path = output_path

    return state


def apply_audio(src_path: str, dist_path: str):
    src_video = mpe.VideoFileClip(src_path)
    dist_video = mpe.VideoFileClip(dist_path)
    dist_video: Any = dist_video.set_audio(src_video.audio)
    dist_basename, _ = os.path.splitext(src_path)
    tmp_dist_path = dist_basename + "_with_audio_.mp4"
    dist_video.write_videofile(tmp_dist_path)
    os.remove(dist_path)
    os.rename(tmp_dist_path, dist_path)


def process_clip(
    cam_gear: CamGear,
    video: ResultVideo,
    user_preferences: UserPreferences,
    output_path: str,
):

    font: Optional[ImageFont.FreeTypeFont] = None

    writer = WriteGear(output=output_path)

    word_groups = group_words_in_time_frames(
        video.subtitles.words, frame_duration=SUBTITLE_FRAME_DURATION
    )

    fps = cam_gear.framerate
    frame_count = 0

    while True:
        frame = cam_gear.read()
        if frame is None:
            break

        if font is None:
            font_size = frame.shape[1] * FONT_SIZE_TO_WIDTH_RATIO
            font = ImageFont.truetype(FONTS_DIR + "/nunito.ttf", font_size)

        current_time = frame_count / fps
        # print(f"current_time = {current_time}")
        selected_group: Optional[WordGroup] = None
        for group in word_groups:
            if group.start <= current_time < group.end:
                selected_group = group
                break

        if selected_group != None and selected_group.words:
            frame = draw_subtitles_on_frame(
                frame,
                word_group=selected_group,
                font=font,
                user_preferences=user_preferences,
                current_time=current_time,
            )

        frame_count += 1
        writer.write(frame)

    writer.close()


class DrawingWord:
    def __init__(
        self, text: str, width: float, height: float, highlighting: bool
    ) -> None:
        self.highlighting = highlighting
        self.text = text
        self.width = width
        self.height = height

    def __repr__(self) -> str:
        return f"'{self.text}' (w:{self.width})"


class DrawingLine:
    def __init__(self) -> None:
        self.words: List[DrawingWord] = []
        self.width: float = 0.0
        self.height: float = 0.0

    def __repr__(self) -> str:
        return f"{repr(self.words)}: (w:{self.width})"


# NOTE: word_group must not be empty
def draw_subtitles_on_frame(
    frame: MatLike,
    word_group: WordGroup,
    font: ImageFont.FreeTypeFont,
    user_preferences: UserPreferences,
    current_time: float,
) -> MatLike:

    img = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))

    img_width = img.width
    img_height = img.height

    subtitle_box_max_width = img_width * SUBTITLE_BOX_MAX_WIDTH

    draw = ImageDraw.Draw(img)

    drawing_words: List[DrawingWord] = []
    for word in word_group.words:
        stripped_text = strip_text(word.text)
        drawing_words.append(
            DrawingWord(
                text=stripped_text,
                width=calc_text_width(font=font, text=stripped_text),
                height=font.size,
                highlighting=word.start <= current_time < word.end,
            )
        )
    separator_width = calc_text_width(" ", font=font)
    # join words into lines to fin in subtitle_box_max_width
    lines = split_words_into_lines(
        drawing_words,
        separator_width=separator_width,
        max_width=subtitle_box_max_width,
    )

    full_text_width = max(line.width for line in lines)
    full_text_height = sum(line.height for line in lines)
    full_text_corner_x = max(
        img_width * SUBTITLE_REL_POS[0] - full_text_width / 2.0, 0.0
    )
    full_text_corner_y = max(
        img_height * SUBTITLE_REL_POS[1] - full_text_height / 2.0, 0.0
    )

    line_vertical_offset = full_text_corner_y
    for i, line in enumerate(lines):
        line_height = line.height
        line_width = line.width
        centering_offset = (full_text_width - line_width) / 2
        bg_padding = line_height * BG_PADDING_RATIO
        line_x = full_text_corner_x + centering_offset
        line_y = line_vertical_offset
        draw.rounded_rectangle(
            (
                (line_x - bg_padding, line_y - bg_padding),
                (
                    line_x + line_width + bg_padding * 2,
                    line_y + line_height + bg_padding * 2,
                ),
            ),
            fill=COLOR_BG,
            radius=line_height * BG_RADIUS_RATIO,
        )
        line_word_offset_x = 0.0
        line_word_offset_y = line_height / 2.0
        for word in line.words:
            draw.text(
                (line_x + line_word_offset_x, line_y + line_word_offset_y),
                text=word.text,
                font=font,
                fill=COLOR_HIGHLIGHT if word.highlighting else COLOR_FG,
                anchor="lm",
            )
            line_word_offset_x += word.width + separator_width
        line_vertical_offset += line_height * SUBTITLE_LINE_SPACING

    return cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)


def split_words_into_lines(
    words: List[DrawingWord],
    separator_width: float,
    max_width: float,
) -> List[DrawingLine]:
    lines: List[DrawingLine] = []
    for word in words:
        if not lines:
            lines.append(DrawingLine())
        last_line = lines[-1]
        candidate_line_words = last_line.words + [word]
        candidate_width = (
            sum(word.width for word in candidate_line_words)
            + max(0, len(candidate_line_words) - 1) * separator_width
        )
        if last_line and candidate_width > max_width:  # last line is not empty
            lines.append(DrawingLine())

        last_line = lines[-1]
        if last_line.words:
            last_line.width += separator_width
        last_line.words.append(word)
        last_line.width += word.width
        last_line.height = max(last_line.height, word.height)

    return lines


def calc_text_width(text: str, font: ImageFont.FreeTypeFont):
    box = font.getbbox(text)  # left, top, right, bottom
    return box[2] - box[0]


def strip_text(text: str):
    return re.sub(SPACE_REGEX, " ", text).strip()


def group_words_in_time_frames(
    words: List[TimecodedText], frame_duration: float
) -> List[WordGroup]:
    result: List[WordGroup] = []

    current_group = WordGroup()
    result.append(current_group)

    for word in words:
        # make sure to add word anyway, even if it longer then frame
        if not current_group.words:
            current_group.words.append(word)
            continue

        first_word = current_group.words[0]
        duration = word.end - first_word.start

        if duration > frame_duration:
            current_group = WordGroup()
            result.append(current_group)

        current_group.words.append(word)

    for group in result:
        if not group.words:
            continue
        group.start = group.words[0].start
        group.end = group.words[-1].end

    return result
