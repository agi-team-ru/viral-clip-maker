import logging
from typing import List
from core import ProcessingState, TimecodedText
from pydantic import BaseModel
import openai
import os
import time

from common import convert_words_sentences
from utils import extract_json_from_text

logger = logging.getLogger(__name__)

LLM_TEXT_MODEL = os.environ["LLM_TEXT_MODEL"]


def process(state: ProcessingState) -> ProcessingState:
    if not state.result:
        logger.warning("No result provided")
        return state

    for video in state.result:
        if not video.subtitles or not video.subtitles.words:
            continue
        sentences = convert_words_sentences(video.subtitles.words)
        video.hashtags = generate_hashtags(sentences)

    return state


response_json_format = """{
    "related_hashtags": ["#...", "#...", "#..."]
}"""


class LlmHashtagsResponse(BaseModel):
    related_hashtags: List[str]


def generate_hashtags(sentences: List[TimecodedText]):
    for _ in range(5):
        try:
            return generate_hashtags_attempt(sentences)
        except Exception as ex:
            logger.error(ex)
            time.sleep(1.0)
    raise RuntimeError("Request to LLM failed in all attempts")


def generate_hashtags_attempt(sentences: List[TimecodedText]):
    client = openai.OpenAI()

    prompt = f"""
You are given subtitles of a video.

Your task is to:
1. Tell why the video is popular, why people like it, how much can it get popular.
2. Generate 15 hashtags that can be used for the video.
3. Write in russian.

Hashtags must be the most popular and related hashtags.
Use the most simple hashtags.

Do not tell about the amount of views or likes or other metrics.
Only tell why the video is can be popular.

Response JSON format:
{response_json_format}

Generate response in JSON format.
Follow JSON format strictly.

Subtitles:
{'\n'.join([subtitle.text for subtitle in sentences])}
"""

    response = client.beta.chat.completions.parse(
        model=LLM_TEXT_MODEL,
        messages=[
            {
                "role": "system",
                "content": "You are professional video reviewer, which helps to generate hashtags for short video clips.",
            },
            {"role": "user", "content": prompt},
        ],
    )
    llm_response = response.choices[0].message.content
    if llm_response == None:
        raise RuntimeError("Unexpected empty response from LLM")

    json_strs = extract_json_from_text(llm_response)
    if not json_strs:
        raise RuntimeError("Unexpected empty JSON from LLM")

    res = LlmHashtagsResponse.model_validate_json(json_strs[-1])

    return [hashtag.strip().strip("#").lower() for hashtag in res.related_hashtags]
