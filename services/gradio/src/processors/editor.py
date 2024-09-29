import logging
from time import sleep
from typing import Any, Dict, List, Tuple, cast
from core import ProcessingState, ResultVideo, Subtitles, TimecodedText, UserPreferences
from pydantic import BaseModel
import openai
import uuid
import os
import moviepy.editor as mpe
import time

from common import convert_words_sentences
from utils import chunks, extract_json_from_text

logger = logging.getLogger(__name__)

fade_duration = 0.4

LLM_TEXT_MODEL = os.environ["LLM_TEXT_MODEL"]
LLM_IMG_MODEL = os.environ["LLM_IMG_MODEL"]

SENTENCES_CHUNK_SIZE = 50

response_json_format = """{
    "selected_fragments":[
        {
            "selected_sentences": [1, 2, 3], # a list of numbers of selected sentence
            "explanation": "The explanation of choice" # here is a short explanation
        },
        # here must be another 2-4 fragments
    ]
}"""


class LlmClipFragment(BaseModel):
    selected_sentences: List[int]
    explanation: str


class LlmClipFragmentsResponse(BaseModel):
    selected_fragments: List[LlmClipFragment]


def process(state: ProcessingState) -> ProcessingState:
    if not state.source_video_path:
        logger.warning("No video not provided")
        return state
    if not state.source_subtitles:
        logger.warning("No source subtitles provided")
        return state
    if not state.user_preferences:
        logger.warning("No user preferences provided")
        return state

    if not state.source_subtitles.words:
        state.result = []
        return state

    output_dir = f"/tmp/clip-maker/{uuid.uuid4()}"
    os.makedirs(output_dir, exist_ok=True)

    result: List[ResultVideo] = []
    sentences = convert_words_sentences(state.source_subtitles.words)

    selected_fragments = []
    fragment_explainations = []
    for chunk_sentences in chunks(sentences, SENTENCES_CHUNK_SIZE):
        chunk_selected_fragments, chunk_fragment_explainations = select_sentences(
            sentences=chunk_sentences, user_preferences=state.user_preferences
        )
        selected_fragments += chunk_selected_fragments
        fragment_explainations += chunk_fragment_explainations

    for i, (output_file, clip_words) in enumerate(
        compile_clips(
            input_path=state.source_video_path,
            output_dir=output_dir,
            source_words=state.source_subtitles.words,
            selected_fragments=selected_fragments,
        )
    ):
        subtitles = Subtitles()
        subtitles.words = clip_words
        result.append(
            ResultVideo(
                path=output_file,
                subtitles=subtitles,
                explanation=fragment_explainations[i],
            )
        )

    state.result = result

    return state


def select_sentences(sentences: List[TimecodedText], user_preferences: UserPreferences):
    for _ in range(5):
        try:
            return select_sentences_attempt(sentences, user_preferences)
        except Exception as ex:
            logger.error(ex)
            time.sleep(1.0)
    raise RuntimeError("Request to LLM failed in all attempts")


def select_sentences_attempt(
    sentences: List[TimecodedText], user_preferences: UserPreferences
):
    client = openai.OpenAI()
    fragment_explainations = []
    selected_fragments: List[List[TimecodedText]] = []

    prompt_sentences: List[str] = []
    key_to_sentence_map: Dict[str, TimecodedText] = {}
    for i, sentence in enumerate(sentences):
        sentence_key = f"{i+1}"
        key_to_sentence_map[sentence_key] = sentence
        prompt_sentences.append(f"{sentence_key}: {sentence.text}")

    prompt = f"""
Here`s a numbered text, you MUST take EVERY most INTERESTING FRAGMENTS from it.

You are creating content for the most viral videos on the internet.
Videos MUST be attention-grabbing, unique, interesting, and unusual.
Each fragment MUST start with something that will catch the viewer's attention and make them watch till the end.

CRITICAL RULES:
1. Each fragment MUST consist of STRICTLY CONSECUTIVE sentences.
2. Fragments MUST NOT contain any uninteresting sentences.
3. Each fragment must focus on ONE unique event, person, or action.
4. All sentences in a fragment MUST belong to the same scene.
5. The start and end of each fragment MUST have the same overall meaning or theme.

SELECTION PROCESS:
1. Identify the most interesting or attention-grabbing sentence.
2. Check adjacent sentences (before and after) to see if they belong to the same scene and add to the fragment's impact.
3. Include adjacent sentences ONLY if they maintain the fragment's focus and interest level.
4. Stop adding sentences as soon as the scene changes or the interest level drops.

NUMBERING:
- ALWAYS use the original sentence numbers from the source text.
- Ensure the numbers are strictly consecutive.
- CORRECT: [1, 2, 3, 4, 5] (consecutive)
- INCORRECT: [1, 2, 3, 5, 7] (not consecutive) - THIS IS FORBIDDEN

Return your answer in JSON Format:
{response_json_format}

The numbered text:
{"\n".join(prompt_sentences)}
"""

    response = client.beta.chat.completions.parse(
        model=LLM_TEXT_MODEL,
        messages=[
            {
                "role": "system",
                "content": "You are text editor, which helps to choose most attention-grabbing fragments from large text with numbered sentences.",
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

    res = LlmClipFragmentsResponse.model_validate_json(json_strs[-1])

    fragment_explainations = []
    selected_fragments: List[List[TimecodedText]] = []

    for fragment in res.selected_fragments:
        selected_sentences: List[TimecodedText] = []
        for sentence_key_raw in fragment.selected_sentences:
            sentence_key = str(sentence_key_raw)
            if sentence_key not in key_to_sentence_map:
                logger.warning(f"Key '{sentence_key}' (from LLM) is not valid")
                continue
            selected_sentences.append(key_to_sentence_map[sentence_key])

        if not selected_sentences:
            continue

        fragment_explainations.append(fragment.explanation)
        selected_fragments.append(selected_sentences)

    if not selected_fragments:
        raise RuntimeError("No fragments selected by LLM")

    return selected_fragments, fragment_explainations


def compile_clips(
    input_path: str,
    output_dir: str,
    source_words: List[TimecodedText],
    selected_fragments: List[List[TimecodedText]],
):
    full_video = mpe.VideoFileClip(input_path, audio=True)
    ret: List[Tuple[str, List[TimecodedText]]] = []
    for idx, selected_sentences in enumerate(selected_fragments):
        sentence_subclips: List[mpe.VideoFileClip] = []
        for sentence in selected_sentences:
            sentence_subclip = (
                cast(Any, full_video)
                .subclip(sentence.start, sentence.end)
                .audio_fadein(0.01)
                .audio_fadeout(0.01)
            )
            sentence_subclips.append(sentence_subclip)

        final_clip = mpe.concatenate_videoclips(sentence_subclips)

        output_file = f"{output_dir}/{idx}.mp4"
        clip = (
            cast(Any, final_clip)
            # .fadein(fade_duration)
            .fadeout(fade_duration)
            .audio_fadein(fade_duration)
            .audio_fadeout(fade_duration)
        )
        clip.write_videofile(output_file)

        clip_words: List[TimecodedText] = []
        final_clip_duration = 0
        for sentence in selected_sentences:
            for word in source_words:
                if (
                    sentence.start <= word.start <= sentence.end
                    and sentence.start <= word.end <= sentence.end
                ):
                    shifted_start = final_clip_duration + word.start - sentence.start
                    shifted_end = final_clip_duration + word.end - sentence.start

                    clip_words.append(
                        TimecodedText(
                            text=word.text,
                            start=shifted_start,
                            end=shifted_end,
                        )
                    )
            final_clip_duration += sentence.end - sentence.start

        ret.append((output_file, clip_words))
    return ret
