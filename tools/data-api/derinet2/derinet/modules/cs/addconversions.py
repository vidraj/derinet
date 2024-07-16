from derinet import Block, Lexicon
import argparse
import logging


logger = logging.getLogger(__name__)


class AddConversions(Block):
    def __init__(self, fname):
        # The arguments to __init__ are None (returned from below).
        self.fname = fname

    def process(self, lexicon: Lexicon):
        """Read annotation in the form of
        parent(_pos_gender_animacy) TAB > TAB child(_pos_gender_animacy)
        and add conversion relations between the lemmas."""

        # load lemmas
        with open(self.fname, mode='r', encoding='U8', newline='\n') as f:
            for line in f:
                parent, _, child = line.rstrip().split('\t')

                # find parent
                parent = parent.split('_')
                if len(parent) == 1:  # only lemma given
                    p_lms = lexicon.get_lexemes(lemma=parent[0])

                elif len(parent) == 2:  # lemma + pos
                    p_lms = lexicon.get_lexemes(lemma=parent[0], pos=parent[1])

                elif len(parent) == 3:  # lemma + pos + gender
                    p_lms = lexicon.get_lexemes(lemma=parent[0], pos=parent[1])
                    p_lms = [lemma for lemma in p_lms
                             if lemma.feats.get('Gender', 'x') == parent[2]]

                elif len(parent) == 4:  # lemma + pos + gender + animacy
                    p_lms = lexicon.get_lexemes(lemma=parent[0], pos=parent[1])
                    p_lms = [lemma for lemma in p_lms
                             if lemma.feats.get('Gender', '') == parent[2]
                             and lemma.feats.get('Animacy', '') == parent[3]]

                # find child
                child = child.split('_')
                if len(child) == 1:  # only lemma given
                    c_lms = lexicon.get_lexemes(lemma=child[0])

                elif len(child) == 2:  # lemma + pos
                    c_lms = lexicon.get_lexemes(lemma=child[0], pos=child[1])

                elif len(child) == 3:  # lemma + pos + gender
                    c_lms = lexicon.get_lexemes(lemma=child[0], pos=child[1])
                    c_lms = [lemma for lemma in c_lms
                             if lemma.feats.get('Gender', 'x') == child[2]]

                elif len(child) == 4:  # lemma + pos + gender + animacy
                    c_lms = lexicon.get_lexemes(lemma=child[0], pos=child[1])
                    c_lms = [lemma for lemma in c_lms
                             if lemma.feats.get('Gender', '') == child[2]
                             and lemma.feats.get('Animacy', '') == child[3]]

                # add conversion relation
                if c_lms and p_lms:
                    c_node, p_node = c_lms[0], p_lms[0]
                    # skip if they are the same
                    if c_node == p_node:
                        continue

                    # disconnect child from its original parent
                    lexicon.remove_all_parent_relations(c_node)

                    # disconnect possible cycles
                    for node in c_node.get_tree_root().iter_subtree():
                        if node == p_node and p_node.parent:
                            lexicon.remove_relation(p_node)

                    # add conversion relation
                    lexicon.add_conversion(source=p_node, target=c_node)
                    logger.info('Relation between {} and {} was added.'
                                .format(p_node, c_node))

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
