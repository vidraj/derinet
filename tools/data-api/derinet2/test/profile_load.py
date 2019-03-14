import sys
from derinet.lexicon import Lexicon, FileFormatType

lexicon = Lexicon()
lexicon.load(sys.argv[1], fmt=FileFormatType.DERINET_V1)

if len(sys.argv) == 3:
    lexicon.save(sys.argv[2], FileFormatType.PICKLE_V4)
