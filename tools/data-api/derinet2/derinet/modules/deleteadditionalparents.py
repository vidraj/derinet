from derinet import Block, Lexicon

class DeleteAdditionalParents(Block):
    """
    Keep only a single parent for each lexeme and delete all the rest,
    therefore enforcing a strict tree structure.
    """
    def process(self, lexicon: Lexicon):
        for lexeme in lexicon.iter_lexemes(sort=True):
            if len(lexeme.all_parents) > 1:
                # Remove all extra parents.
                removed_sources = []
                # Where do they come from?
                # It might be from the otherrels. Delete them all.
                for relation in lexeme.otherrels:
                    removed_sources.extend(relation.sources)
                    relation.remove_from_lexemes()
                # And it might also be from the main relation, which
                #  might be e.g. compounding.
                if len(lexeme.parent_relation.sources) > 1:
                    source = lexeme.parent_relation.main_source
                    removed_sources.extend(lexeme.parent_relation.other_sources)
                    # TODO Store the removed targets as well?
                    #targets = lexeme.parent_relation.targets
                    feats = lexeme.parent_relation.feats

                    lexeme.parent_relation.remove_from_lexemes()
                    lexicon.add_derivation(source, lexeme, feats)

                lexeme.misc["omitted_parents"] = [str(l) for l in removed_sources]

        return lexicon
