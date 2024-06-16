import unittest
from derinet.lexicon import Lexicon
from derinet.modules.cs.checkfeatsandmisc import CheckFeatsAndMisc
import logging

# The check?? functions log their results verbosely. Disable logging for
#  the duration of this test so that the user is not spammed by
#  nonsensical messages.
def setUpModule():
    logging.disable(logging.CRITICAL)

def tearDownModule():
    logging.disable(logging.NOTSET)

class TestCheckFeatsAndMisc(unittest.TestCase):
    def test_misc_key_removal_using_class(self):
        lexicon = Lexicon()

        a = lexicon.create_lexeme("pay", "V", misc={"x1": {"y1": {"z1": "delete"}, "y2": "stay"}, "x2": "stay", "x3": {"y3": "delete", "y4": "delete"}})
        b = lexicon.create_lexeme("phone", "N", misc={"x1": {"y1": "stay", "y2": "stay"}, "x2": "stay", "x3": None})
        c = lexicon.create_lexeme("payphone", "N", misc={"x1": {"y1": {"z1": None, "z2": "stay"}, "y2": "stay"}, "x2": {"x3": "stay", "z1": "stay"}})

        block = CheckFeatsAndMisc()

        self.assertTrue(block.checkMV(a, ("x2",), {"stay"}))
        self.assertFalse(block.checkMV(a, ("x2",), {"delete"}))

        self.assertTrue(block.checkMV(a, ("x1", "y1", "z1"), {"delete"}))
        self.assertTrue(block.checkMV(a, ("x1", "y1", "z2"), {"delete"}))
        self.assertTrue(block.checkMV(a, ("x1", "y2", "z1"), {"delete"}))
        self.assertFalse(block.checkMV(a, ("x1", "y2"), {"delete"}))
        self.assertTrue(block.checkMV(a, ("x1", "y2"), {"delete", "stay"}))

if __name__ == '__main__':
    unittest.main()
