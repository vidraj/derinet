from derinet import Block, Format, Lexicon
import argparse


class Load(Block):
    def __init__(self, file, format=Format.DERINET_V2):
        self.file = file
        self.format = format

    def process(self, lexicon: Lexicon):
        lexicon.load(self.file, fmt=self.format)
        return lexicon

    @staticmethod
    def parse_args(args):
        parser = argparse.ArgumentParser(
            prog=__class__.__name__,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter
        )

        known_formats = {fmt.name: fmt for fmt in Format}

        parser.add_argument("-f", "--format", choices=known_formats, default=Format.DERINET_V2.name, help="The format of the file to load.")
        parser.add_argument("file", type=argparse.FileType("rt"), help="The file to load.")
        parser.add_argument("rest", nargs=argparse.REMAINDER, help="A list of other modules and their arguments.")

        args = parser.parse_args(args)

        fmt = known_formats.get(args.format)

        file = args.file

        return [file], {"format": fmt}, args.rest
