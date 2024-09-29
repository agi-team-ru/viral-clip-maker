import logging
from typing import Any, Callable, List, Optional, Tuple, cast
import pathlib

from cv2.typing import MatLike

from core import AspectRatio, ProcessingState, ResultVideo, UserPreferences
import os
import mediapipe as mp
import cv2

import scenedetect
import moviepy.editor as mpe

mp_face_detection = cast(Any, mp.solutions).face_detection
mp_drawing = cast(Any, mp.solutions).drawing_utils
logger = logging.getLogger(__name__)


aspect_ratios = {
    AspectRatio.HORIZONTAL: 16.0 / 9.0,
    AspectRatio.SQUARE: 1.0,
    AspectRatio.VERTICAL: 9.0 / 16.0,
}


class Rect:
    def __init__(self, x: int, y: int, w: int, h: int) -> None:
        self.x = x
        self.y = y
        self.w = w
        self.h = h

    def __repr__(self) -> str:
        return f"(x:{self.x}, y:{self.y}, w:{self.w}, h:{self.h})"


class FrameTrace:
    def __init__(self, frame_idx: int, faces: List[Rect]) -> None:
        self.frame_idx = frame_idx
        self.faces = faces

    def __repr__(self) -> str:
        return f"{self.frame_idx}: {self.faces}"


def process(state: ProcessingState) -> ProcessingState:
    if not state.source_video_path:
        logger.warning("No video not provided")
        return state
    if not state.user_preferences:
        logger.warning("No user preferences provided")
        return state
    if not state.result:
        logger.warning("No result provided")
        return state

    for video in state.result:
        base_src_path, _ = os.path.splitext(video.path)
        output_path = f"{base_src_path}_cropped.mp4"

        if not process_clip(
            input_path=video.path,
            user_preferences=state.user_preferences,
            output_path=output_path,
        ):
            continue

        pathlib.Path.unlink(pathlib.Path(video.path))
        video.path = output_path

    return state


def process_clip(
    input_path: str,
    user_preferences: UserPreferences,
    output_path: str,
):
    scene_list = scenedetect.detect(input_path, scenedetect.AdaptiveDetector())

    mfd = mp_face_detection.FaceDetection(
        model_selection=1, min_detection_confidence=0.5
    )
    vc = cv2.VideoCapture(input_path)
    clip = mpe.VideoFileClip(input_path)

    aspect_ratio = aspect_ratios[user_preferences.aspect_ratio]

    target_resolution = calc_target_resolution(clip.size, aspect_ratio)

    # print("target_resolution", target_resolution)

    scene_clips = []
    for frame_from, frame_to in scene_list:
        face_trace = trace_faces_in_frame(
            vc=vc,
            mfd=mfd,
            start_frame=frame_from.frame_num or 0,
            end_frame=frame_to.frame_num or 0,
        )

        scene_clip: Any = clip.subclip(
            cast(int, frame_from.get_seconds()), frame_to.get_seconds()
        )

        desired_center = None
        if face_trace:
            desired_center = detect_trace_center(face_trace)

        centered_scene_clip = scene_clip.fl(
            lambda gf, t, tr=target_resolution, dc=desired_center: fl_crop_frame(
                gf, t, tr, dc
            )
        )
        scene_clips.append(centered_scene_clip)

    if not scene_clips:
        logger.warning("No scene clips")
        return False

    final_clip = mpe.concatenate_videoclips(scene_clips)
    final_clip.write_videofile(output_path, fps=clip.fps)
    return True


def detect_trace_center(trace: List[FrameTrace]) -> Tuple[int, int]:
    selected_face = 0
    x: int = 0
    y: int = 0
    for ft in trace:
        face = ft.faces[selected_face]
        x += face.x + face.w // 2
        y += face.y + face.h // 2
    n = len(trace)
    return x // n, y // n


def fl_crop_frame(
    get_frame: Callable[[int], MatLike],
    t: int,
    target_resolution: Tuple[int, int],
    desired_center: Optional[Tuple[int, int]],
):

    frame = get_frame(t)
    height, width, _ = frame.shape

    if desired_center == None:
        desired_center = (width // 2, height // 2)

    (x1, y1), (x2, y2) = centered_crop(
        (width, height), target_resolution, desired_center
    )

    cropped_frame = frame[y1:y2, x1:x2]

    return cropped_frame


def centered_crop(
    source_size: Tuple[int, int], target_size: Tuple[int, int], center: Tuple[int, int]
):
    src_width, src_height = source_size
    target_width, target_height = target_size
    center_x, center_y = center
    if src_width > target_width:  # need crop horizontal margins
        x1 = max(0, center_x - target_width // 2)
        x1 = min(x1, src_width - target_width)
        x2 = x1 + target_width
        y1 = 0
        y2 = src_height
    else:
        y1 = max(0, center_y - target_height // 2)
        y1 = min(y1, src_height - target_height)
        y2 = y1 + target_height
        x1 = 0
        x2 = src_width
    return ((x1, y1), (x2, y2))


def trace_faces_in_frame(
    vc: cv2.VideoCapture, start_frame: int, end_frame: int, mfd: Any
):
    ret: List[FrameTrace] = []
    if start_frame >= end_frame:
        logger.warning(f"Invalid scene frames: {start_frame} - {end_frame}")
        return ret

    vc.set(cv2.CAP_PROP_POS_FRAMES, start_frame)

    for frame_idx in range(start_frame, end_frame):
        ret_val, frame = vc.read()
        if not ret_val:
            break

        height, width, _ = frame.shape
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        face_results = mfd.process(rgb_frame)

        if face_results.detections:
            faces: List[Rect] = []
            for detection in face_results.detections:
                rbbox = detection.location_data.relative_bounding_box
                faces.append(
                    Rect(
                        x=int(rbbox.xmin * width),
                        y=int(rbbox.ymin * height),
                        w=int(rbbox.width * width),
                        h=int(rbbox.height * height),
                    )
                )
            if faces:
                # faces are detected unordered
                faces.sort(key=lambda face: face.x)
                ret.append(FrameTrace(frame_idx=frame_idx, faces=faces))
    return ret


def calc_target_resolution(
    src_resolution: Tuple[int, int], aspect_ratio: float
) -> Tuple[int, int]:
    src_w, src_h = src_resolution

    if src_h >= src_w / aspect_ratio:
        return (src_w, int(src_w / aspect_ratio + 0.001))
    else:
        return (int(src_h * aspect_ratio + 0.001), src_h)
