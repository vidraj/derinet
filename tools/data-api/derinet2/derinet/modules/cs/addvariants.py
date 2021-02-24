from derinet import Block, Lexicon
import argparse
import logging

logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s %(levelname)-8s %(message)s',
                    datefmt='%a, %d %b %Y %H:%M:%S')

logger = logging.getLogger(__name__)


class AddVariants(Block):
    def __init__(self, fname):
        # The arguments to __init__ are None (returned from below).
        self.fname = fname

    def process(self, lexicon: Lexicon):
        """Read annotation in the form of
        repre-lemma(_pos_gender_animacy) TAB var1(_pos_gender_animacy) TAB ...
        and add variant relations between the lemmas."""

        # load lemmas
        with open(self.fname, mode='r', encoding='U8', newline='\n') as f:
            for line in f:
                line = line.rstrip().split(' ')

                # find lexemes
                variants = list()
                for lemma in line:
                    lemma = lemma.split('_')

                    # get desired lexemes accorging to given features
                    if len(lemma) == 1:  # only lemma given
                        lexemes = lexicon.get_lexemes(lemma=lemma[0])

                    elif len(lemma) == 2:  # lemma + pos
                        lexemes = lexicon.get_lexemes(lemma=lemma[0],
                                                      pos=lemma[1])

                    elif len(lemma) == 3:  # lemma + pos + gender
                        lexemes = lexicon.get_lexemes(lemma=lemma[0],
                                                      pos=lemma[1])
                        lexemes = [l for l in lexemes
                                   if l.feats.get('Gender', 'x') == lemma[2]]

                    elif len(lemma) == 4:  # lemma + pos + gender + animacy
                        lexemes = lexicon.get_lexemes(lemma=lemma[0],
                                                      pos=lemma[1])
                        lexemes = [l for l in lexemes
                                   if l.feats.get('Gender', '') == lemma[2]
                                   and l.feats.get('Animacy', '') == lemma[3]]

                    elif len(line) > 4:
                        logger.warning('Too many arguments has been given: {}.'
                                       .format(line.strip()))
                        continue

                    # store lexeme variants
                    if len(lexemes) < 1:
                        logger.info('Lexeme {} not found.'.format(line[0]))
                    else:
                        variants.append(lexemes)

                # flatten the list if there are homonymy in non-representative
                # lexemes of variant, so all forms are captured as variants
                for idx in range(len(variants)):
                    if len(variants[idx]) > 1:
                        variants = variants + [v for v in variants[idx][1:]]
                    variants[idx] = variants[idx][0]

                # select representative lexeme
                repre = variants[0]
                variants = variants[1:]

                # add variant relations
                for nonrepre in variants:

                    # (i) repre. is in the subtree of the non-repre lemma
                    if repre in list(nonrepre.iter_subtree()):
                        logger.info('Relation between lexeme {} and '
                                    'lexeme {} was deleted.'
                                    .format(repre, repre.parent))
                        repre.parent_relation.remove_from_lexemes()

                    # (ii) nonrepre is in the subtree of the repre lemma
                    if nonrepre in list(repre.iter_subtree()):
                        logger.info('Relation between lexeme {} and '
                                    'lexeme {} was deleted.'
                                    .format(nonrepre, nonrepre.parent))
                        nonrepre.parent_relation.remove_from_lexemes()

                    # (iii) connect non-repre + their subtrees -> repre lemma
                    # non-repre lemma does not have parent
                    if not nonrepre.parent:
                        # connect non-repre. lemma to repre lemma
                        logger.info('Relation between lexeme {} and lexeme'
                                    ' {} was added and labeled as Variant.'
                                    .format(repre, nonrepre))
                        lexicon.add_variant(source=repre, target=nonrepre)

                    # non-repre lemma does have parent as well as repre
                    elif repre.parent:
                        logger.info('Relation between lexeme {} '
                                    'and lexeme {} was deleted.'
                                    .format(nonrepre, nonrepre.parent))
                        nonrepre.parent_relation.remove_from_lexemes()
                        logger.info('Relation between lexeme {} and lexeme'
                                    ' {} was added and labeled as Variant.'
                                    .format(repre, nonrepre))
                        lexicon.add_variant(source=repre, target=nonrepre)

                    # non-repre lemma does have parent and repre does not
                    elif not repre.parent:
                        # connect repre lemma to non-repre parent
                        logger.info('Relation between lexeme {} and '
                                    'lexeme {} was reconnected as '
                                    'relation between lexeme {} and '
                                    'lexeme {}.'
                                    .format(nonrepre, nonrepre.parent,
                                            repre, nonrepre.parent))
                        lexicon.add_derivation(source=nonrepre.parent,
                                               target=repre)
                        nonrepre.parent_relation.remove_from_lexemes()
                        logger.info('Relation between lexeme {} and lexeme'
                                    ' {} was added and labeled as Variant.'
                                    .format(repre, nonrepre))
                        lexicon.add_variant(source=repre, target=nonrepre)

                    # (iv) reconnect non-repre. children to repre lemma
                    for child in nonrepre.children:
                        logger.info('Relation between lexeme {} and '
                                    'lexeme {} was reconnected as '
                                    'relation between lexeme {} and '
                                    'lexeme {}.'
                                    .format(nonrepre, child,
                                            repre, child))
                        child.parent_relation.remove_from_lexemes()
                        lexicon.add_derivation(source=repre,
                                               target=child)

        return lexicon

    @staticmethod
    def parse_args(args):
        """Parse a list of strings containing the arguments, pick the relevant
        ones from the beginning and leave the rest be. Return the parsed args
        to this module and the unprocessed rest."""
        parser = argparse.ArgumentParser(
            prog=__class__.__name__,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter
        )
        parser.add_argument('file', help='The file to load annotation from.')
        # argparse.REMAINDER tells argparse not to be eager and to process
        # only the start of the args.
        parser.add_argument('rest', nargs=argparse.REMAINDER,
                            help='A list of other modules and arguments.')
        args = parser.parse_args(args)
        fname = args.file
        # Return *args to __init__, **kwargs to init and the unprocessed tail
        # of arguments to other modules.
        return [fname], {}, args.rest
