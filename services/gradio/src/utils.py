import json
from typing import List, TypeVar


def extract_json_from_text(text: str) -> List[str]:
    start_json_char = "{"
    decoder = json.JSONDecoder(strict=False)
    pos = 0
    ret: List[str] = []
    while True:
        start_char_pos = text.find(start_json_char, pos)
        if start_char_pos < 0:
            break
        try:
            result, index = decoder.raw_decode(text[start_char_pos:])
            pos = start_char_pos + index
            ret.append(json.dumps(result, ensure_ascii=False))
        except ValueError:
            pos = start_char_pos + 1
    return ret


def read_file(path: str):
    with open(path, "r") as f:
        return f.read()


T = TypeVar("T")


def chunks(lst: List[T], n: int):
    """Yield successive n-sized chunks from lst."""
    for i in range(0, len(lst), n):
        yield lst[i : i + n]
