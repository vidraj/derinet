from derinet import Block, Format, Lexicon
import argparse


class Save(Block):
    def __init__(self, file, format=Format.DERINET_V2, on_err="raise"):
        self.file = file
        self.format = format
        self.on_err = on_err

    def process(self, lexicon: Lexicon):
        lexicon.save(self.file, fmt=self.format, on_err=self.on_err)
        return lexicon

    @staticmethod
    def parse_args(args):
        parser = argparse.ArgumentParser(
            prog=__class__.__name__,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter
        )

        known_formats = {fmt.name: fmt for fmt in Format}

        parser.add_argument("-f", "--format", choices=known_formats, default=Format.DERINET_V2.name, help="The format of the file to save.")
        parser.add_argument("-k", "--keep-going", action="store_true", help="Keep going on errors instead of dying.")
        parser.add_argument("file", type=argparse.FileType("wt"), help="The file to save to.")
        parser.add_argument("rest", nargs=argparse.REMAINDER, help="A list of other modules and their arguments.")

        args = parser.parse_args(args)

        fmt = known_formats.get(args.format)

        if args.keep_going:
            on_err = "continue"
        else:
            on_err = "raise"

        file = args.file

        return [file], {"format": fmt, "on_err": on_err}, args.rest
