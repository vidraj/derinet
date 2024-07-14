import sys
import argparse
from derinet.lexicon import Lexicon, Format

formats = {
    "derinet-v1": Format.DERINET_V1,
    "derinet-v2": Format.DERINET_V2,
    "pickle-v4": Format.PICKLE_V4
}

parser = argparse.ArgumentParser()
parser.add_argument("input_format", choices=formats.keys(), help="Input format to load")
parser.add_argument("--save", choices=formats.keys(), help="Output format to save to")
args = parser.parse_args()

input_format = formats[args.input_format]

lexicon = Lexicon()

if input_format == Format.PICKLE_V4:
    # Read in binary mode.
    lexicon.load(sys.stdin.buffer, fmt=input_format)
else:
    # Read in text mode.
    lexicon.load(sys.stdin, fmt=input_format)

if args.save is not None:
    output_format = formats[args.save]
    if output_format == Format.PICKLE_V4:
        # The output stream must be in binary mode.
        lexicon.save(sys.stdout.buffer, fmt=output_format)
    else:
        # Text mode is good enough.
        lexicon.save(sys.stdout, fmt=output_format)
