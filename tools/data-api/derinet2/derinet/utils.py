import re
from typing import Tuple

class DerinetError(Exception):
    """
    The base class for all custom Derinet errors.

    It is defined so that you can safely catch all linguistic and annotation
    errors with a single `except` type statement, while not catching unintended
    errors such as TypeErrors.
    """
    pass


class DerinetFileParseError(DerinetError):
    """
    The exception raised when a Derinet file cannot be parsed while loading the lexicon.
    """
    pass


class DerinetCycleCreationError(DerinetError):
    """
    The exception created when an attempt of changing a relation forms a cycle
    in the spanning tree of main relations.
    """
    pass


def parse_v1_id(val: str) -> int:
    """
    Parse a textual representation of a DeriNet-1.X ID to an integer.

    :param val: a string containing the ID
    :return: an integer representing the same ID
    """
    num = int(val)
    if num < 0:
        raise ValueError("ID must be a positive integer, is '{}'".format(val))
    return num


v2_id_regex = re.compile(r"([0-9]+)\.([0-9]+)")
def parse_v2_id(val: str) -> Tuple[int, int]:
    """
    Parse a textual representation of a DeriNet-2.X ID to a pair of integers.

    :param val: a string containing the ID
    :return: a tuple of two integers representing the same ID
    """
    match = v2_id_regex.fullmatch(val)
    if match is None:
        raise ValueError("ID must be a pair of two positive integers separated by a dot, is '{}'".format(val))

    tree_id_str, lex_id_str = match.groups()
    tree_id, lex_id = int(tree_id_str), int(lex_id_str)

    # Check that the numbers are not overlong, i.e. 0001 is not allowed.
    assert str(tree_id) == tree_id_str
    assert str(lex_id) == lex_id_str

    return tree_id, lex_id


def format_kwstring(d):
    if d is None or len(d) == 0:
        return ""
    else:
        raise NotImplementedError()


def parse_kwstring(s):
    if s == "":
        return []
    else:
        raise NotImplementedError()


def _valid_range(r):
    if isinstance(r, tuple) and len(r) == 2 and r[0] < r[1]:
        return True
    else:
        return False


def range_overlaps(a, b):
    """
    Check whether range a overlaps range b in any way.

    :param a: A tuple of (start, end)
    :param b: A tuple of (start, end)
    :return: True if there is overlap, False otherwise
    """
    if not _valid_range(a):
        raise ValueError("Invalid range {}".format(a))
    if not _valid_range(b):
        raise ValueError("Invalid range {}".format(b))

    a_start, a_end = a
    b_start, b_end = b

    # B starts inside A.
    if a_start <= b_start < a_end:
        return True

    # B ends inside A.
    if a_start < b_end <= a_end:
        return True

    # A starts inside B.
    if b_start <= a_start < b_end:
        return True

    # A ends inside B.
    if b_start < a_end <= b_end:
        return True

    # None of the above.
    return False
