import sys
from derinet.lexicon import Lexicon, Format

lexicon = Lexicon()
lexicon.load(sys.argv[1], fmt=Format.DERINET_V1)

if len(sys.argv) == 3:
    lexicon.save(sys.argv[2], Format.PICKLE_V4)
