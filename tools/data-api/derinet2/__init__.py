
# user-defined error classes
class LexemeNotFoundError(Exception):
    pass


class AmbiguousLexemeError(Exception):
    pass


class AmbiguousParentError(Exception):
    pass


class ParentNotFoundError(Exception):
    pass


class AlreadyHasParentError(Exception):
    pass


class IsNotParentError(Exception):
    pass


class CycleCreationError(Exception):
    pass

class UnknownFileVersion(Exception):
    pass