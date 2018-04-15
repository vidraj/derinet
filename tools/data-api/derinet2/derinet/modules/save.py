from derinet.modules.block import Block

class Save(Block):
    def __init__(self, args):
        if "file" not in args:
            raise ValueError("Argument 'file' must be supplied.")
        else:
            self.fname = args["file"]

    def process(self, derinet):
        # TODO assert that there are no arguments other than "file" in self.args.
        derinet.save(self.fname)
        return derinet
