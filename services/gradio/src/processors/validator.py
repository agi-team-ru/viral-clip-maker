import logging
from typing import Any, Dict

from core import ProcessingState

logger = logging.getLogger(__name__)


def process(state: ProcessingState) -> ProcessingState:

    logging.info("No validation rules defined")

    # raise if not valid
    return state
