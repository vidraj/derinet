import sys
import argparse
from derinet.lexicon import Lexicon, Format

formats = {
    "derinet-v1": Format.DERINET_V1,
    "derinet-v2": Format.DERINET_V2,
    "pickle-v4": Format.PICKLE_V4
}

format_list_string = ", ".join(formats.keys())
format_help_string = "One of {}.".format(format_list_string)

parser = argparse.ArgumentParser()
parser.add_argument("input_format", help=format_help_string)
parser.add_argument("--save", help=format_help_string)
args = parser.parse_args()

if args.input_format not in formats:
    print("Format {} not supported. It must be one of {}".format(args.input_format, format_list_string), file=sys.stderr, flush=True)
    sys.exit(1)

if args.save is not None and args.save not in formats:
    print("Format {} not supported. It must be one of {}".format(args.save, format_list_string), file=sys.stderr, flush=True)
    sys.exit(1)

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
