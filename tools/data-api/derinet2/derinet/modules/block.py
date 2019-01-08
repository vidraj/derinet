class Block:
    def __init__(self, args):
        self.args = args

    def process(self, derinet):
        for lexeme in derinet.iter_lexemes():
            self.process_lexeme(lexeme)

        return derinet

    def process_lexeme(self, lexeme):
        raise NotImplementedError("process_lexeme method has to be implemented")

    @property
    def signature(self):
        # TODO use self.__class__.__name__ or similar, together with a printout of args.
        # TODO how to print args when subclasses can redefine __init__ and not save them?
        return self.__str__()
