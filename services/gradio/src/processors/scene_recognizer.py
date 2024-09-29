from typing import List
from core import ProcessingState, VideoScene
import logging
from scenedetect import detect, AdaptiveDetector

logger = logging.getLogger(__name__)


def process(state: ProcessingState) -> ProcessingState:
    if not state.source_video_path:
        logger.warning("No source video provided")
        return state

    scene_list = detect(state.source_video_path, AdaptiveDetector())

    source_scenes: List[VideoScene] = []

    for frame_from, frame_to in scene_list:
        video_scene = VideoScene(
            start_frame=frame_from.frame_num or 0,
            end_frame=frame_to.frame_num or 0,
            start=frame_from.get_seconds(),
            end=frame_to.get_seconds(),
        )
        source_scenes.append(video_scene)

    state.source_scenes = source_scenes

    return state
