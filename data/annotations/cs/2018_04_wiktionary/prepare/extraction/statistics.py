# !usr/bin/env python3
# coding: utf-8

"""A."""

from collections import defaultdict


class Statistics:
    """A."""

    def __init__(self):
        """A."""
        # vocabulary of lexemes with wf relation (is child or parent)
        self.output_vocabulary = set()
        # number of active lexeme in wiktionary (findable in search engine)
        self.active_lexemes = 0
        # number of extracted relations in wiktionary
        self.relations = 0

    def add_active_lexeme(self):
        """A."""
        self.active_lexemes += 1

    def add_vocabulary(self, lexeme):
        """A."""
        self.output_vocabulary.add(lexeme)

    def add_relations(self):
        """A."""
        self.relations += 1

    def get_active_lexeme(self):
        """A."""
        return self.active_lexemes

    def get_vocabulary(self):
        """A."""
        return self.output_vocabulary

    def get_relations(self):
        """A."""
        return self.relations

    def get_pos(self):
        """A."""
        pos = defaultdict(int)
        for i in self.output_vocabulary:
            w = i.split('_')[1]
            pos[w] += 1
        return pos
