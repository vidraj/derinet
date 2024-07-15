from derinet import Block, Lexicon, DerinetError
from derinet.utils import techlemma_to_lemma
import re
import argparse
import logging

#logging.basicConfig(level=logging.INFO,
                    #format='%(asctime)s %(levelname)-8s %(message)s',
                    #datefmt='%a, %d %b %Y %H:%M:%S')

logger = logging.getLogger(__name__)


class AddDerivationsFromEnumeratedWords(Block):
    def __init__(self, fname):
        # The arguments to __init__ are those that the parse_args method (below) returns.
        self.fname = fname

    def process(self, lexicon: Lexicon):
        """
        The annotation has the following format:
        - There is a header line which has to be ignored.
        - The columns are:
            1. Lemma
            2. POS
            3. Original parent lemma
            4. Original parent POS
            5. Annotation
            6. Notes
        - The notes are not actionable, so just ignore them.
        - The annotation is as follows:
            - ok means the Original parent is the correct parent
            - r means the lexeme should be unconnected
            - c means the lexeme is a compound
            - empty means missing annotation, probably the lexeme is wrong
            - ? means missing annotation (unresolved issue)
            - otherwise, there is a parent lemma somewhere in there.
                - prefixed by _ if the parent lexeme is a phantom
                - suffixed by space and (POS) if there is homonymy
                - it may contain dash-number techlemma spec if there is homonymy
        """

        solution_regex = re.compile(r"^SOLUTION:\s*([^ ]+)\s*>\s*([^ ]+)\s*$")

        with open(self.fname, "rt", encoding="utf-8", newline="\n") as f:
            # Consume the header.
            f.readline()

            for i, line in enumerate(f):
                line = line.rstrip()
                columns = line.split("\t")

                assert len(columns) >= 2

                techlemma = columns[0]
                lemma = techlemma_to_lemma(techlemma)
                pos = columns[1]

                lexemes = lexicon.get_lexemes(lemma, pos, techlemma=techlemma, techlemma_match_fuzzy=True)

                if not lexemes:
                    logger.error("Lexeme for line {} ({} {}) not found".format(i, techlemma, pos))
                    continue
                elif len(lexemes) > 1:
                    logger.warn("Lexeme for line {} ({} {}) ambiguous, selecting arbitrarily".format(i, techlemma, pos))
                lexeme = lexemes[0]

                if len(columns) < 5 or not columns[4].strip():
                    logger.warn("Incomplete annotation for line {} ({} {})".format(i, techlemma, pos))
                    # Nothing to do here.
                    continue

                annot = columns[4].strip()
                if annot == "r":
                    # Verify that the lexeme is a root.
                    if lexeme.parent_relation is None:
                        # All OK, the lexeme is actually a root.
                        pass
                    else:
                        logger.error("Lexeme {} should be a root, but it is descended from {} using a {}".format(lexeme, lexeme.all_parents, lexeme.parent_relation.type))
                elif annot == "c":
                    # Verify that the lexeme is connected as a compound
                    #  or unconnected and has the compounding mark. If
                    #  unconnected and markless, add the mark.
                    # TODO
                    if (lexeme.parent_relation is None
                        or lexeme.parent_relation.type == "Compounding"):
                        # Nothing wrong here.
                        if (lexeme.parent_relation is None
                            and lexeme.misc.get("is_compound")):
                            # The lexeme is missing the compounding mark.
                            # Add it.
                            logger.debug("Marking lexeme {} as a compound".format(lexeme))
                            lexeme.misc["is_compound"] = True
                    else:
                        # There is a relation and it is not compounding.
                        logger.error("Lexeme {} should be a compound, but it is descended from {} using a {}".format(lexeme, lexeme.all_parents, lexeme.parent_relation.type))

                elif annot == "?" or annot == "":
                    # The annotation is not filled in.
                    logger.warning("Unannotated lexeme {}".format(lexeme))

                else:
                    # The lexeme should be derived from something.
                    if annot == "ok":
                        # The parent is listed in columns 3 and 4.
                        ptechlemma = columns[2]
                        plemma = techlemma_to_lemma(ptechlemma)
                        ppos = columns[3]
                        phantom = None
                    else:
                        # The parent is listed in the manual annotation.
                        # The annotation is the lemma, optionally with a
                        #  POS tag and phantomness mark.
                        split_annot = annot.split(" ", maxsplit=1)
                        if len(split_annot) == 1:
                            ptechlemma = split_annot[0]
                            ppos = None
                        elif len(split_annot) == 2:
                            ptechlemma, ppos = split_annot
                        else:
                            logger.error("Cannot unpack lemma and POS from space-delimited list '{}'".format(annot))

                        if ptechlemma.startswith("_"):
                            # Parse the phantomness mark.
                            phantom = True
                            ptechlemma = ptechlemma[1:]
                        else:
                            phantom = False

                        plemma = techlemma_to_lemma(ptechlemma)
                        if plemma == ptechlemma:
                            # If the two are the same, ignore the techlemma
                            #  for purposes of searching the database.
                            ptechlemma = None

                        if ppos is not None:
                            # Remove the parentheses.
                            ppos = ppos[1:-1]

                    plexeme = lexeme.parent
                    if plexeme is not None:
                        # There is already a connection; verify that it
                        #  is what it should be.
                        if (plexeme.lemma == plemma
                            and (ppos is None or plexeme.pos == ppos)):
                            # The lexeme is already connected correctly.
                            logger.debug("Already connected '{}' {} to '{}' {}".format(lemma, pos, plemma, plexeme.pos))
                            continue
                        else:
                            logger.warning("Lexeme '{}' {} has wrong existing parent '{}' {}, should be '{}' {}".format(lemma, pos, plexeme.lemma, plexeme.pos, plemma, ppos))
                            # TODO disconnect or what?
                            continue

                    # The lexeme is not connected yet.
                    plexemes = lexicon.get_lexemes(plemma, ppos, techlemma=ptechlemma, techlemma_match_fuzzy=True)
                    # Filter out the child lexeme, if we're trying to connect a lexeme to its homonym (e.g. via conversion).
                    plexemes = [l for l in plexemes if l is not lexeme]
                    if not plexemes:
                        # There is no conforming parent.
                        logger.warning("Lexeme '{}' {} has no existing parent in the DB satisfying '{}' {}".format(lemma, pos, plemma, ppos))
                        continue
                    elif len(plexemes) > 1:
                        logger.warning("Lexeme '{}' {} has {} parents in the DB satisfying '{}' {}".format(lemma, pos, len(plexemes), plemma, ppos))
                    plexeme = plexemes[0]

                    # We have a parent!
                    logger.info("Deriving {} from {}".format(lexeme, plexeme))
                    try:
                        lexicon.add_derivation(plexeme, lexeme)
                    except DerinetError as e:
                        logger.error("An error happened when deriving {} from {}".format(lexeme, plexeme), exc_info=e)

                    # Verify that the phantomness is set correctly as well.
                    if (phantom is not None and not (phantom and plexeme.feats.get("Fictitious"))
                        and (phantom or plexeme.feats.get("Fictitious"))):
                        logger.error("Wrong phantomness of '{}' {}".format(lemma, pos))
                        # TODO fix that.

        return lexicon

    @classmethod
    def parse_args(cls, args):
        """Parse a list of strings containing the arguments, pick the relevant
        ones from the beginning and leave the rest be. Return the parsed args
        to this module and the unprocessed rest."""
        parser = argparse.ArgumentParser(
            prog=cls.__name__,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter
        )

        parser.add_argument("file", help="The file to load annotation from.")
        # argparse.REMAINDER tells argparse not to be eager and to process only the start of the args.
        parser.add_argument("rest", nargs=argparse.REMAINDER, help="A list of other modules and their arguments.")

        args = parser.parse_args(args)

        fname = args.file

        # Return *args to __init__, **kwargs to init and the unprocessed tail of arguments to other modules.
        return [fname], {}, args.rest
