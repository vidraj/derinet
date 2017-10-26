class Block:

    def __init__(self, derinet):
        self.derinet = derinet

    def process(self):
        for lexeme in self.derinet.lexemes:
            self.process_lexeme(lexeme)

    def process_lexeme(self, lexeme):
        raise NotImplementedError("process_lexeme method has to be implemented")

    @property
    def signature(self):
        return self.__name__
