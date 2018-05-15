from derinet.modules.block import Block

import derinet as derinet_api
import logging
import re

logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s %(levelname)-8s %(message)s',
                    datefmt='%a, %d %b %Y %H:%M:%S')

logger = logging.getLogger(__name__)


class AddJK(Block):
    def __init__(self, args):
        if "file" not in args:
            raise ValueError("Argument 'file' must be supplied.")
        else:
            self.fname = args["file"]

    def process(self, derinet):
        """2nd and 3rd datasets"""
        logger.info('Adding {}'.format(self.fname))
        with open(self.fname, 'rt', encoding='utf-8') as import_file:
            for line in import_file:
                mark, id, child, parent, action = line.strip().split(',')[:5]
                try:
                    if '_' in parent: # have a technical lemma
                        tech, parent = parent, parent.replace('-', '_').split('_')[0]
                    else:
                        tech = None
                    if action == 'NO_PARENT_IN_DERINET' and mark != '-':
                        candidate_parents = [candidate for candidate in derinet.search_lexemes(parent) if candidate.pos in {'N', 'V'}]
                        if len(candidate_parents) == 1:
                            logger.info('Setting {} <- {}'.format(child, parent))
                            derinet.add_derivation(child, candidate_parents[0])
                        else:
                            if tech is not None:
                                derinet.add_derivation(child, parent, parent_morph=tech)
                            else:
                                print('Error: parent ambiguous, choice from: ', end='')
                                print([candidate.morph for candidate in candidate_parents])

                    elif action == 'DIFFERENT_PARENT_IN_DERINET' and mark == '+':
                        logger.info('Setting {} <- {}'.format(child, parent))
                        derinet.add_derivation(child, parent)
                except (derinet_api.AlreadyHasParentError, derinet_api.CycleCreationError) as error:
                    logger.warning(error)
                    try:
                        derinet.add_derivation(child, parent, force=True)
                    except derinet_api.CycleCreationError as error:
                        logger.error(error)
                # FIXME solve the ambiguity outlined below and uncomment appropriate code sections.
                #  The problem is that AmbiguousLexemeError is no longer signalled.
                #except derinet_api.AmbiguousLexemeError as error:
                    ## this part is correct ONLY for this dataset
                    ## because there only two cases with ambiguous child
                    ## and both are to be resolved this way 
                    #print('Warning: child ambiguous, adding both: '.format(error), end='')
                    #candidate_children = [candidate for candidate in derinet.search_lexemes(child) if candidate.pos in {'N', 'V'}]
                    #print([candidate.morph for candidate in candidate_children])
                    #for candidate_child in candidate_children:
                        #derinet.add_derivation(candidate_child, parent)

                except derinet_api.ParentNotFoundError as error:
                    logger.error('parent missing: {}'.format(error))
                except derinet_api.LexemeNotFoundError as error:
                    logger.error('child missing: {}'.format(error))
                except derinet_api.IsNotParentError as error:
                    logger.error(error)
        return derinet
