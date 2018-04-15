from derinet.modules.block import Block

import derinet as derinet_api
from distutils.util import strtobool
import logging

logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s %(levelname)-8s %(message)s',
                    datefmt='%a, %d %b %Y %H:%M:%S')

logger = logging.getLogger(__name__)


def get_info(morpho, pos):
    if '_' in morpho:
        return morpho.replace('-', '_').split('_')[0], pos, morpho
    if '-' in morpho:
        return morpho.split('-')[0], pos, None
    return (morpho, pos, None)


def check_and_add(derinet, child, parent, suppress_warnings=True):
    """
    Check candidate child and parent lexemes.
    If unambiguous, add the derivation.
    """
    child_candidates = derinet.search_lexemes(*child, allow_fallback=True)
    parent_candidates = derinet.search_lexemes(*parent, allow_fallback=True)
    if len(child_candidates) == 1 and len(parent_candidates) == 1:
        try:
            derinet.add_derivation(child_candidates[0], parent_candidates[0])
        except (derinet_api.AlreadyHasParentError,
                derinet_api.CycleCreationError) as error:
            if not suppress_warnings:
                logger.warning(error)
            try:
                derinet.add_derivation(child_candidates[0], parent_candidates[0], force=True)
            except derinet_api.CycleCreationError as error:
                logger.error(error)
                logger.error("Cycle in {} {} -> {} {}".format(parent_candidates[0].morph, parent_candidates[0].pos, child_candidates[0].morph, child_candidates[0].pos))
        except (derinet_api.DeriNetError) as error:
            print('Error:', error)

    else:
        if len(child_candidates) != 0 and len(parent_candidates) == 0:
            print('Error: parent missing:', end='')
        elif len(child_candidates) == 0 and len(parent_candidates) != 0:
            print('Error: child missing:', end='')
        elif len(child_candidates) == 0 and len(parent_candidates) == 0:
            print('Error: both missing:', end='')
        elif len(child_candidates) > 1 and len(parent_candidates) <= 1:
            print('Error: child ambiguous:', end='')
        elif len(child_candidates) <= 1 and len(parent_candidates) > 1:
            print('Error: parent ambiguous:', end='')
        elif len(child_candidates) > 1 and len(parent_candidates) > 1:
            print('Error: both ambiguous:', end='')

        print(' {} (child) has '.format(derinet_api.pretty_lexeme(*child)), end='')
        print(['{} {}'.format(child[2], child[1]) for child in child_candidates], end='')
        print(', {} (parent) has '.format(derinet_api.pretty_lexeme(*parent)), end='')
        print(['{} {}'.format(parent[2], parent[1]) for parent in parent_candidates])



class AddChangedEdgeProbabilities(Block):
    def __init__(self, args):
        if "suppress_warnings" in args:
            self.suppress_warnings = bool(strtobool(args["suppress_warnings"]))
        else:
            self.suppress_warnings = False

        if "file" not in args:
            raise ValueError("Argument 'file' must be supplied.")
        else:
            self.fname = args["file"]

    def process(self, derinet):
        """ 4th dataset """
        logger.info('Adding {}'.format(self.fname))
        with open(self.fname, 'rt', encoding='utf-8') as import_file:
            for line in import_file:
                mark, child, prob, new_parent, old_parent = line.rstrip('\n').split('\t')
                if mark == '+':
                    child = get_info(*child.split(' '))
                    parent = get_info(*new_parent.replace('NEW: ', '').split(' '))
                    logger.debug('Setting {} <- {}'.format(child, parent))
                    check_and_add(derinet, child, parent, suppress_warnings=self.suppress_warnings)

        return derinet
