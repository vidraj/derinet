import sys
from derinet.lexicon import Lexicon, Format

lexicon = Lexicon()
lexicon.load(sys.argv[1], fmt=Format.PICKLE_V4)
