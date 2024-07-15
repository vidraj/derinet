from derinet import Block, Format, Lexicon
import argparse
import sys


class Save(Block):
    def __init__(self, filename, format=Format.DERINET_V2, on_err="raise"):
        self.filename = filename
        self.format = format
        self.on_err = on_err

    def process(self, lexicon: Lexicon):
        if self.filename == "-":
            lexicon.save(sys.stdout, fmt=self.format, on_err=self.on_err)
        else:
            lexicon.save(self.filename, fmt=self.format, on_err=self.on_err)
        return lexicon

    @classmethod
    def parse_args(cls, args):
        parser = argparse.ArgumentParser(
            prog=cls.__name__,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter
        )

        known_formats = {fmt.name: fmt for fmt in Format}

        parser.add_argument("-f", "--format", choices=known_formats, default=Format.DERINET_V2.name, help="The format of the file to save.")
        parser.add_argument("-k", "--keep-going", action="store_true", help="Keep going on errors instead of dying.")
        # We don't use `argparse.FileType("wt")` here, because we only
        #  want the file to be created when the module is run, not when
        #  the args are parsed. This prevents clobbering earlier files
        #  and/or creating empty files (which confuse Make) on error.
        parser.add_argument("file", help="The file to save to.")
        parser.add_argument("rest", nargs=argparse.REMAINDER, help="A list of other modules and their arguments.")

        args = parser.parse_args(args)

        fmt = known_formats.get(args.format)

        if args.keep_going:
            on_err = "continue"
        else:
            on_err = "raise"

        filename = args.file

        return [filename], {"format": fmt, "on_err": on_err}, args.rest
