import sys
from derinet.lexicon import Lexicon, FileFormatType

lexicon = Lexicon()
lexicon.load(sys.argv[1], fmt=FileFormatType.PICKLE_V4)
