import logging
import random

from core import ProcessingState

logger = logging.getLogger(__name__)


def process(state: ProcessingState) -> ProcessingState:
    if not state.result:
        logger.warning("No result provided")
        return state

    for result_video in state.result:
        result_video.score = random.random()

    return state
