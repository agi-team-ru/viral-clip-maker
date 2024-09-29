import sys

sys.path.append(".")
sys.path.append("./src")

from src.utils import extract_json_from_text
from pprint import pprint


pprint(
    extract_json_from_text(
        """
Hello from LLLM
{"a": 1}

There is another one JSON
{"key 1": {"key2": "value 1"}}

Good bye!
"""
    )
)
