from typing import Any, Dict

from core import ProcessingState, VideoAnnotations

def process(state: ProcessingState) -> ProcessingState:

    annotations = VideoAnnotations()

    state.source_annotations = annotations
    return state
