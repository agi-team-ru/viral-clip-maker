from abc import abstractmethod
from enum import StrEnum
import logging
import os
from typing import Callable, List, Optional, Tuple
import gradio as gr

logger = logging.getLogger(__name__)

DEV_MODE = os.environ.get("GRADIO_WATCH_DEMO_NAME", "") != ""


def make_public_uri(public_path: str):
    return f"/file={public_path}"


class Context:
    def __init__(self, gr_state: gr.State, gr_current_page: gr.State) -> None:
        self.gr_state = gr_state
        self.gr_page_name = gr_current_page


class Router:
    def __init__(self, ctx: Context) -> None:
        self.ctx = ctx

    def attach_go(self, event: Callable, page_name: str):
        def handle_event(prev_page_page: str):
            logger.info(f"Page switch from {prev_page_page} to {page_name}")
            return page_name

        event(handle_event, inputs=self.ctx.gr_page_name, outputs=self.ctx.gr_page_name)


class VideoScene:
    def __init__(
        self,
        start: float,
        end: float,
        start_frame: int,
        end_frame: int,
    ) -> None:
        self.start = start
        self.end = end
        self.start_frame = start_frame
        self.end_frame = end_frame

    def __repr__(self) -> str:
        return f"{self.start:.2f}-{self.end:.2f}"


class TimecodedText:
    def __init__(
        self,
        text: str,
        start: float,
        end: float,
    ) -> None:
        self.text = text
        self.start = start
        self.end = end

    def __repr__(self) -> str:
        return f"{self.start:.2f}-{self.end:.2f}: '{self.text}'"


class Subtitles:
    words: List[TimecodedText]


class VideoAnnotations:
    annotations: List[TimecodedText]


class ResultVideo:
    def __init__(
        self,
        path: str,
        subtitles: Subtitles,
        explanation: Optional[str] = None,
        score: float = 0.0,
        hashtags: Optional[List[str]] = None,
    ) -> None:
        self.path = path
        self.subtitles = subtitles
        self.score = score
        self.explanation = explanation
        self.hashtags = hashtags


class AspectRatio(StrEnum):
    VERTICAL = "VERTICAL"
    SQUARE = "SQUARE"
    HORIZONTAL = "HORIZONTAL"


class ClipTemplate(StrEnum):
    RECOMBINED = "RECOMBINED"
    CROPPED = "CROPPED"
    EXTENDED = "EXTENDED"


class Language(StrEnum):
    # NOTE: value MUST be compatible with Whisper language param
    RU = "ru"
    EN = "en"


class UserPreferences:
    aspect_ratio: AspectRatio
    duration: Tuple[int, int]
    use_emoji: bool
    keyword_highlight: bool
    keywords: str
    template: ClipTemplate
    language: Language


class ProcessingState:
    def __init__(self) -> None:
        self.source_video_path: Optional[str] = None
        self.source_subtitles: Optional[Subtitles] = None
        self.source_annotations: Optional[VideoAnnotations] = None
        self.source_scenes: Optional[List[VideoScene]] = None
        self.user_preferences: Optional[UserPreferences] = None
        self.result: Optional[List[ResultVideo]] = None


Processor = Callable[[ProcessingState], ProcessingState]


class UserState:
    def __init__(self) -> None:
        self.page_name: str = ""
        self.src_video: str = ""
        self.video_name: str = ""
        self.result: List[ResultVideo] = []
        self.user_preferences: Optional[UserPreferences] = None


class AbstractPage:
    name: str
    ctx: Context
    router: Router

    @abstractmethod
    def render(self, state: UserState): ...
