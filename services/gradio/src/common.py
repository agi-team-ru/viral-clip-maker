from typing import List, Optional
import re
from core import TimecodedText

SPACE_REGEX = r"\s+"
SENTENCE_END_CHARS = [".", "!", "?"]

def convert_words_sentences(words: List[TimecodedText]) -> List[TimecodedText]:
    result: List[TimecodedText] = []
    text: Optional[str] = None
    text_start: Optional[float] = None
    last_i = len(words) - 1
    for i, word in enumerate(words):
        if text_start == None:
            text_start = word.start
        if text == None:
            text = word.text
        else:
            text += " " + word.text
        is_last = i == last_i
        if is_last or is_last_sentence_word(word.text, next_word=words[i + 1].text):
            sentence = TimecodedText(
                text=re.sub(SPACE_REGEX, " ", text).strip(),
                start=text_start,
                end=word.end,
            )
            result.append(sentence)
            text_start = None
            text = None

    return result


def is_last_sentence_word(word: str, next_word: str) -> bool:
    if not any(word.endswith(sign) for sign in SENTENCE_END_CHARS):
        return False

    # if next word is lowercase, then it is abbreviation rather then end of sentance
    if next_word != None and next_word.strip()[0].islower():
        return False

    return True
