import sys
from typing import Any

sys.path.append(".")
sys.path.append("./src")

from src.processors.cropper import calc_target_resolution, centered_crop
from src.utils import chunks


assert calc_target_resolution((16, 9), 1.0) == (9, 9)
assert calc_target_resolution((16, 9), 16.0 / 9.0) == (16, 9)
assert calc_target_resolution((16, 16), 16.0 / 9.0) == (16, 9)

assert calc_target_resolution((9, 16), 1.0) == (9, 9)
assert calc_target_resolution((9, 16), 9.0 / 16.0) == (9, 16)
assert calc_target_resolution((16, 16), 9.0 / 16.0) == (9, 16)


def assert_equals(actual: Any, expected: Any):
    if expected != actual:
        print(f"{actual} != {expected}")
        raise AssertionError()


assert_equals(centered_crop((10, 16), (10, 16), (0, 0)), ((0, 0), (10, 16)))
assert_equals(centered_crop((10, 16), (10, 16), (5, 5)), ((0, 0), (10, 16)))
assert_equals(centered_crop((10, 16), (10, 16), (0, 15)), ((0, 0), (10, 16)))
assert_equals(centered_crop((10, 16), (10, 16), (9, 0)), ((0, 0), (10, 16)))

assert_equals(centered_crop((10, 16), (10, 6), (0, 0)), ((0, 0), (10, 6)))
assert_equals(centered_crop((10, 16), (10, 6), (9, 15)), ((0, 10), (10, 16)))

assert_equals(centered_crop((10, 16), (5, 16), (0, 0)), ((0, 0), (5, 16)))
assert_equals(centered_crop((10, 16), (5, 16), (9, 15)), ((5, 0), (10, 16)))

print(list(chunks(list(range(10)), 3)))

print("OK")
