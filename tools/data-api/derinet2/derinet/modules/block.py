class Block:

    def process(self, derinet):
        for lexeme in derinet._data:
            self.process_lexeme(lexeme)

        return derinet

    def process_lexeme(self, lexeme):
        raise NotImplementedError("process_lexeme method has to be implemented")

    @property
    def signature(self):
        return self.__str__()
