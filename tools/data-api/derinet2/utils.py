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


def lexeme_info(lexeme):
    assert type(lexeme) == Node
    return (lexeme.lemma, lexeme.pos, lexeme.morph)

def flatten_list(l):
    for el in l:
        if isinstance(el, list) and not isinstance(el, (str, bytes)):
            yield from flatten_list(el)
        else:
            yield el