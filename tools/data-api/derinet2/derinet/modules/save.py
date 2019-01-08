from derinet.modules.block import Block

class Save(Block):
    def __init__(self, args):
        if "file" not in args:
            raise ValueError("Argument 'file' must be supplied.")
        else:
            self.fname = args["file"]

        if "version" in args:
            self.version = int(args["version"])
        else:
            self.version = 2

        if "morph_source" in args:
            self.morph_source = args["morph_source"]
        else:
            self.morph_source = None

    def process(self, derinet):
        # TODO assert that there are no arguments other than "file" in self.args.
        if self.version == 1:
            with open(self.fname, 'wt', encoding='utf8') as f:
                for lexeme in derinet.iter_lexemes():
                    if self.morph_source is None:
                        techlemma = lexeme.techlemma
                    else:
                        if "segmentation" in lexeme.misc and self.morph_source in lexeme.misc["segmentation"]:
                            techlemma = '‧'.join(lexeme.misc["segmentation"][self.morph_source]["segments"])
                        else:
                            techlemma = lexeme.lemma
                    print("{}\t{}\t{}\t{}\t{}".format(lexeme.lex_id, lexeme.lemma, techlemma, lexeme.pos, lexeme.parent_id if lexeme.parent_id is not None else ""), file=f)
        elif self.version == 2:
            derinet.save(self.fname)
        else:
            raise ValueError("Unknown version {}.".format(self.version))
        return derinet
