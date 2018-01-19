from collections import namedtuple

# a simple structure to represent a node
Node = namedtuple('Node',
                  ['lex_id', # internal reference for the node
                   'pretty_id', # more readable hierarchical id
                   'lemma',
                   'morph',
                   'pos',
                   'tag_mask',
                   'parent_id',
                   'composition_parents', # list of pairs of parents that compose
                   'misc', # miscellaneous information about the node in the JSON format
                   'children',  # these are actual children nodes, not ids
                   ])


def safe_str(line):
    if line is None:
        return ''
    return line


def no_parent(parent_id_or_node):
    if isinstance(parent_id_or_node, Node):
        parent_id = parent_id_or_node.parent_id
    else:
        parent_id = parent_id_or_node
    return parent_id == '' or parent_id is None


def pretty_lexeme(lemma, pos, morph):
    items = [lemma]
    for item in (pos, morph):
        if item is not None:
            items.extend([' ', item])
    return '"{}"'.format(''.join(items))


def partial_lexeme_match(node, lemma, pos, morph):
    return all(item is None or node[field] == item
               for field, item in (
                   (1, lemma),
                   (3, pos),
                   (2, morph)
               ))


def flatten_list(l):
    for el in l:
        if isinstance(el, list) and not isinstance(el, (str, bytes)):
            yield from flatten_list(el)
        else:
            yield el


class DeriNetError(Exception):
    """The base class for all custom DeriNet errors.

    It is defined so that you can safely catch all linguistic and annotation
    errors with a single `except` type statement, while not catching unintended
    errors such as TypeErrors.
    """
    pass

class LexemeNotFoundError(DeriNetError):
    pass


class ParentNotFoundError(LexemeNotFoundError):
    pass


class AlreadyHasParentError(DeriNetError):
    pass


class CycleCreationError(DeriNetError):
    pass


class UnknownFileVersion(DeriNetError):
    pass


class LexemeAlreadyExistsError(DeriNetError):
    """Thrown when adding a lexeme that was already defined in the database."""
    pass
