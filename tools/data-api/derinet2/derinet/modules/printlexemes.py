from .block import Block

class PrintLexemes(Block):

    def process_lexeme(self, lexeme):
        if lexeme.lemma.startswith('Aa'):
            print(lexeme.lemma)