
# user-defined error classes
class LexemeNotFoundError(Exception):
    pass


class AlreadyHasParentError(Exception):
    pass


class CycleCreationError(Exception):
    pass


class UnknownFileVersion(Exception):
    pass
