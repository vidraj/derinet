import unittest
from derinet.lexicon import Lexicon
from derinet.modules.removemisckeys import RemoveMiscKeys


class TestRemoveMiscKeys(unittest.TestCase):
    def test_misc_key_removal_using_class(self):
        lexicon = Lexicon()

        a = lexicon.create_lexeme("pay", "V", misc={"x1": {"y1": {"z1": "delete"}, "y2": "stay"}, "x2": "stay", "x3": {"y3": "delete", "y4": "delete"}})
        b = lexicon.create_lexeme("phone", "N", misc={"x1": {"y1": "stay", "y2": "stay"}, "x2": "stay", "x3": None})
        c = lexicon.create_lexeme("payphone", "N", misc={"x1": {"y1": {"z1": None, "z2": "stay"}, "y2": "stay"}, "x2": {"x3": "stay", "z1": "stay"}})

        block = RemoveMiscKeys([["x1", "y1", "z1"], ["x3"]])
        block.process(lexicon)

        # Check that x2 stays unchanged.
        self.assertIn("x2", a.misc)
        self.assertEqual("stay", a.misc["x2"])
        self.assertIn("x2", b.misc)
        self.assertEqual("stay", b.misc["x2"])
        self.assertIn("x2", c.misc)
        self.assertIn("x3", c.misc["x2"])
        self.assertEqual("stay", c.misc["x2"]["x3"])
        self.assertIn("z1", c.misc["x2"])
        self.assertEqual("stay", c.misc["x2"]["z1"])

        # Check that x3 gets deleted.
        self.assertNotIn("x3", a.misc)
        self.assertNotIn("x3", b.misc)
        self.assertNotIn("x3", c.misc)

        # Check that ["x1", "y1", "z1"] get deleted.
        self.assertIn("x1", a.misc)
        self.assertIn("y1", a.misc["x1"])
        self.assertNotIn("z1", a.misc["x1"]["y1"])
        self.assertIn("x1", b.misc)
        self.assertIn("y1", b.misc["x1"])
        self.assertNotIn("z1", b.misc["x1"]["y1"])
        self.assertIn("x1", c.misc)
        self.assertIn("y1", c.misc["x1"])
        self.assertNotIn("z1", c.misc["x1"]["y1"])

        # Check that the rest of x1 stays.
        self.assertIn("y2", a.misc["x1"])
        self.assertEqual("stay", a.misc["x1"]["y2"])
        self.assertEqual("stay", b.misc["x1"]["y1"])
        self.assertIn("y2", b.misc["x1"])
        self.assertEqual("stay", b.misc["x1"]["y2"])
        self.assertIn("y2", c.misc["x1"])
        self.assertEqual("stay", c.misc["x1"]["y2"])
        self.assertIn("z2", c.misc["x1"]["y1"])
        self.assertEqual("stay", c.misc["x1"]["y1"]["z2"])

    def test_misc_key_arg_parsing(self):
        lexicon = Lexicon()

        a = lexicon.create_lexeme("pay", "V", misc={"x1": {"y1": {"z1": "delete"}, "y2": "stay"}, "x2": "stay", "x3": {"y3": "delete", "y4": "delete"}})
        b = lexicon.create_lexeme("phone", "N", misc={"x1": {"y1": "stay", "y2": "stay"}, "x2": "stay", "x3": None})
        c = lexicon.create_lexeme("payphone", "N", misc={"x1": {"y1": {"z1": None, "z2": "stay"}, "y2": "stay"}, "x2": {"x3": "stay", "z1": "stay"}})

        args, kwargs, rest = RemoveMiscKeys.parse_args(["--key", "x1/x2/z1", "-kx3", "rest"])

        self.assertEqual(["rest"], rest)
        self.assertEqual([[['x1', 'x2', 'z1'], ['x3']]], args)

if __name__ == '__main__':
    unittest.main()
