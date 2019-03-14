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


def format_kwstring(d):
    if d is None or len(d) == 0:
        return ""
    else:
        raise NotImplementedError()


def parse_kwstring(s):
    if s == "":
        return {}
    else:
        raise NotImplementedError()
