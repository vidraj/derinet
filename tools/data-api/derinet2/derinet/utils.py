import re
import sys
from typing import Any, Dict, Iterable, List, Tuple
if sys.version_info >= (3, 10):
    from typing import TypeAlias
else:
    from typing_extensions import TypeAlias

KWKey: TypeAlias = str
KWVal: TypeAlias = str
KWPair: TypeAlias = Tuple[KWKey, KWVal]
KWDict: TypeAlias = Dict[KWKey, KWVal]
KWList: TypeAlias = List[KWDict]

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


class DerinetMorphError(DerinetError):
    """
    The exception raised when an incorrect morph is identified in a lexeme.
    For example, when the morph boundaries are out of range or when the morph
    overlaps another morph.
    """
    pass


class DerinetLexemeDeleteError(DerinetError):
    """
    The exception raised when an incorrect morph is identified in a lexeme.
    For example, when the morph boundaries are out of range or when the morph
    overlaps another morph.
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


def _sanitize_kwpair_item(x: str) -> str:
    for c in {"=", "&", "|", "\n", "\t"}:
        if c in x:
            raise ValueError("Illegal char '{}' in kwstring part '{}'".format(c, x))

    return x


def _format_kwpair(k: KWKey, v: KWVal) -> str:
    if not isinstance(k, str):
        raise TypeError("key-value pair keys must be string, not {} (key '{}', value '{}')".format(type(k), repr(k), repr(v)))
    if not isinstance(v, str):
        raise TypeError("key-value pair values must be string, not {} (key '{}', value '{}')".format(type(v), repr(k), repr(v)))

    k = _sanitize_kwpair_item(k)
    v = _sanitize_kwpair_item(v)

    return "{}={}".format(k, v)


def format_kwstring(d: KWList) -> str:
    if d is None:
        return ""

    if not isinstance(d, list):
        raise TypeError("d must be a list of dicts")

    for item in d:
        if not isinstance(item, dict):
            # import pdb; pdb.set_trace()
            raise TypeError("d must be a list of dicts")

    if len(d) == 0:
        return ""
    else:
        return "|".join(
            ["&".join([_format_kwpair(k, v) for k, v in sorted(inner_dict.items())]) for inner_dict in d]
        )


def _parse_kwpair(s: str) -> KWPair:
    k, v = s.split("=", maxsplit=1)
    return k, v


def parse_kwstring(s: str) -> KWList:
    if s == "":
        return []
    else:
        l = []
        dict_strs = s.split("|")

        for dict_str in dict_strs:
            inner_dict = {}
            for eqstring in dict_str.split("&"):
                k, v = _parse_kwpair(eqstring)

                if k in inner_dict:
                    raise ValueError("Key {} encountered twice".format(k))

                inner_dict[k] = v
            l.append(inner_dict)

        return l


def _valid_range(r: Tuple[int, int]) -> bool:
    return isinstance(r, tuple) and len(r) == 2 and r[0] < r[1]


def range_overlaps(a: Tuple[int, int], b: Tuple[int, int]) -> bool:
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


def techlemma_to_lemma(techlemma: str) -> str:
    """Cut off the technical suffixes from the string techlemma and return the raw lemma"""
    shortlemma = re.sub("[_`].+", "", techlemma)
    lemma = re.sub("-\\d+$", "", shortlemma)
    return lemma

def remove_keys(d: Dict[str, Any], ks: Iterable[str]) -> Dict[str, Any]:
    """Remove keys in collection ks from dict d, return the new dict"""
    ks = set(ks)
    return {k: d[k] for k in d.keys() if k not in ks}
