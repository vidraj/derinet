from derinet import Block, Format, Lexicon
import re
import argparse
import logging

logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s %(levelname)-8s %(message)s',
                    datefmt='%a, %d %b %Y %H:%M:%S')

logger = logging.getLogger(__name__)


def has_parent(lexeme, f, checked=None):
    """
    Ensures that lexeme satisfies f, or any of its ancestors do.
    :param lexeme: The starting point of the search for ancestors.
    :param f: The predicate function of Lexeme → truthy value.
    :param checked: A set of lexemes which were already checked.
    :return: f(ancestor), if there is an ancestor, for which f(ancestor)
             returns a truthy value. False otherwise.
    """

    if checked is None:
        checked = set()

    # Break cycles.
    if lexeme in checked:
        return False
    else:
        checked.add(lexeme)

    # First, check whether lexeme satisfies the proposition.
    r = f(lexeme)
    if r:
        return r

    # If it doesn't, search its parents depth-first.
    for parent_rel in lexeme.parent_relations:
        for parent in parent_rel.sources:
            r = has_parent(parent, f, checked)
            if r:
                return r

    return False


class CheckEnumeratedWords(Block):
    def __init__(self):
        pass

    def process(self, lexicon: Lexicon):
        """
        Verify that each Czech word in the lexicon, in which an ambiguous
        consonant is followed by a hard y, is in the list of enumerated words
        or is descended from one.
        """

        ambiguous_consonants = {
            # The functions are inlined here, because vy- and vý- cannot be
            #  enumerated and have to be tested programatically.
            "b": lambda lexeme: lexeme if lexeme.lemma in frozenset(["by", "být", "bydlet", "obyvatel", "byt", "příbytek", "nábytek", "dobytek", "zbytek", "obyčej", "bystrý", "bylina", "kobyla", "býk", "Přibyslav", "babyka", "trubýš"]) else False,
            "f": lambda lexeme: lexeme if lexeme.lemma in frozenset(["fyzika", "refýž", "zefýr"]) else False,
            "l": lambda lexeme: lexeme if lexeme.lemma in frozenset(["slyšet", "mlýn", "blýskat", "polykat", "plynout", "plyn", "plýtvat", "vzlykat", "lysý", "lýtko", "lýko", "lyže", "pelyněk", "plyš", "slynout", "plytký", "vlys"]) else False,
            "m": lambda lexeme: lexeme if lexeme.lemma in frozenset(["my", "mýt ", "mýval", "myslet", "myslit", "mýlit", "hmyz", "myš", "hlemýžď", "mýtit", "vymýtit", "zamykat", "smýkat", "dmýchat", "chmýří", "nachomýtnout", "mýto", "mykat", "mys", "sumýš"]) else False,
            "p": lambda lexeme: lexeme if lexeme.lemma in frozenset(["pýcha", "pýchavka", "pytel", "pysk", "netopýr", "slepýš", "pyl", "opylovat", "kopyto", "klopýtat", "třpytit", "zpytovat", "pykat", "pýr", "pýřit", "čepýřit", "pýří", "pyj"]) else False,
            "s": lambda lexeme: lexeme if lexeme.lemma in frozenset(["syn", "sytý", "sýr", "sýrový", "syrový", "syrý", "sychravý", "usychat", "usýchat", "sýkora", "sýček", "sysel", "syčet", "sypat"]) else False,
            "v": lambda lexeme: lexeme if (lexeme.lemma in frozenset(["vy", "vysoký", "výt", "výskat", "zvykat", "žvýkat", "vydra", "výr", "vyžle", "povyk", "výheň", "cavyky", "vyza", "kavyl"]) or lexeme.lemma.startswith("vy") or lexeme.lemma.startswith("vý")) else False,
            "z": lambda lexeme: lexeme if lexeme.lemma in frozenset(["brzy", "jazyk", "nazývat", "ozývat", "vyzývat", "vzývat", "Ruzyně"]) else False
        }

        for consonant, test_fn in ambiguous_consonants.items():
            regex_string = consonant + "[yý]"
            regex = re.compile(regex_string)

            # For listing all such lexemes, including derived ones, change this to iter_lexemes.
            # For a listing of only root lexemes, change it to iter_trees.
            for lexeme in lexicon.iter_lexemes(sort=False):
                if "foreign" not in lexeme.misc:
                    logger.warning("Lexeme {} doesn't have the foreign tag specified".format(lexeme))
                    continue

                if lexeme.misc["foreign"]:
                    # Ignore foreign lexemes.
                    #logger.debug("Lexeme {} is foreign, ignoring".format(lexeme))
                    continue

                if re.search("^[A-ZÁÉÍÓÚŮĚŽŠČŘĎŤŇ]", lexeme.lemma):
                    # Ignore proper names.
                    continue

                if (lexeme.pos == "A" and re.search("ý$", lexeme.lemma)) or (lexeme.pos == "D" and re.search("y$", lexeme.lemma)):
                    # Don't take into account known suffixes and/or endings.
                    shortened_lemma = lexeme.lemma[:-1]
                else:
                    shortened_lemma = lexeme.lemma

                if regex.search(shortened_lemma):
                    # The combination is there, therefore, an enumerated word
                    #  must be in the lexeme's ancestors.

                    # Only print the roots of problematic subtrees – therefore,
                    #  if the parent is problematic as well, ignore this lexeme
                    #  and only print the parent (in a later / earlier iteration).
                    parent_also_enumerated = False
                    for parent_rel in lexeme.parent_relations:
                        for parent in parent_rel.sources:
                            # TODO this should maybe be a shortened lemma as well.
                            if regex.search(parent.lemma) or re.search("^[A-ZÁÉÍÓÚŮĚŽŠČŘĎŤŇ]", parent.lemma):
                                # The parent satisfies the condition as well,
                                #  or is a proper name, which we want to ignore.
                                parent_also_enumerated = True
                                break # Only breaks the inner loop, but whatever.

                    if parent_also_enumerated:
                        # Only print the root of broken subtrees.
                        continue

                    parent = has_parent(lexeme, test_fn)
                    if parent:
                        #logger.debug("Lexeme {} has enumerated parent {}".format(lexeme, parent))
                        pass
                    else:
                        logger.warning("Lexeme {} doesn't have an enumerated word in its ancestors.".format(lexeme))
                        if lexeme.parent_relations:
                            logger.info("But it has a parent, which doesn't have the ambiguous consonant.")
                            print(lexeme.techlemma, lexeme.pos, lexeme.parent.techlemma, lexeme.parent.pos, sep="\t", end="\n")
                        else:
                            print(lexeme.techlemma, lexeme.pos, "", "", sep="\t", end="\n")


        return lexicon

    @staticmethod
    def parse_args(args):
        return [], {}, args
