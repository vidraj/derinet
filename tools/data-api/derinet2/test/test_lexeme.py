import unittest
from derinet.lexeme import Lexeme
from derinet.utils import DerinetError


class TestLexeme(unittest.TestCase):
    def test_lexeme_creation_basic(self):
        lexeme = Lexeme("dog", "N")

        self.assertIsNotNone(lexeme)
        self.assertIsInstance(lexeme, Lexeme)

        self.assertEqual(lexeme.lemma, "dog")
        self.assertEqual(lexeme.pos, "N")

    def test_lexeme_creation_optional_fields(self):
        lexeme1 = Lexeme("dog", "N", lemid="dog#NN-??-----A---?")

        self.assertEqual(lexeme1.techlemma, "dog")
        self.assertEqual(lexeme1.lemid, "dog#NN-??-----A---?")

        lexeme2 = Lexeme("cat", "N", lemid="cat#NN-??-----A---?", misc={"techlemma": "cat-1"})

        self.assertEqual(lexeme2.techlemma, "cat-1")

    def test_lexeme_creation_improper_input(self):
        """Currently, these checks are only done in development mode, when assertions are turned on.
        This may cause this test to fail spuriously."""
        with self.assertRaises(Exception):
            Lexeme(1, "N")

        with self.assertRaises(Exception):
            Lexeme("", "N")

        with self.assertRaises(Exception):
            Lexeme("dog", 1)

        with self.assertRaises(Exception):
            Lexeme("dog", "N", lemid=[])

        with self.assertRaises(Exception):
            Lexeme("dog", "N", segmentation={})

        with self.assertRaises(Exception):
            Lexeme("dog", "N", misc=[])

    # noinspection PyPropertyAccess
    def test_lexeme_immutability(self):
        lexeme = Lexeme("dog", "N")

        with self.assertRaises(AttributeError):
            lexeme.lemid = "cat#D"

        with self.assertRaises(AttributeError):
            lexeme.lemma = "cat"

        with self.assertRaises(AttributeError):
            lexeme.pos = "A"

        with self.assertRaises(AttributeError):
            lexeme.techlemma = "dog-2"

    def test_lexeme_default_fields(self):
        lexeme = Lexeme("dog", "N")

        self.assertIs(lexeme.techlemma, lexeme.lemma)

        self.assertIsInstance(lexeme.misc, dict)
        self.assertDictEqual(lexeme.misc, {})

        self.assertIsInstance(lexeme.lemid, str)
        self.assertEqual(lexeme.lemid, "dog#N")

    def test_dict_nonexistence(self):
        """
        This verifies that the __dict__ object is not being created for lexemes,
        resulting in less garbage, smaller memory footprint and faster object creation.
        """
        a = Lexeme("cat", "N")

        with self.assertRaises(AttributeError):
            # noinspection PyDunderSlots,PyUnresolvedReferences
            a.nonexistent_attribute = True  # pylint: disable=assigning-non-slot

    def test_feat_add(self):
        a = Lexeme("cat", "N")
        a.add_feature("Animacy", "Anim")

        self.assertEqual("Anim", a.feats["Animacy"])
        self.assertEqual(1, len(a.feats))

    def test_feat_del(self):
        a = Lexeme("cat", "N")
        a.add_feature("Animacy", "Anim")
        a.add_feature("Animacy", None)

        self.assertNotIn("Animacy", a.feats)

    def test_feat_del_nonexistent(self):
        a = Lexeme("cat", "N")
        a.add_feature("Animacy", None)
        self.assertNotIn("Animacy", a.feats)

    def test_feat_add_multiple_same(self):
        a = Lexeme("cat", "N")
        a.add_feature("Animacy", "Anim")
        a.add_feature("Animacy", "Anim")

        self.assertEqual("Anim", a.feats["Animacy"])

    def test_feat_add_multiple_different(self):
        a = Lexeme("cat", "N")
        a.add_feature("Animacy", "Anim")
        with self.assertRaises(DerinetError):
            a.add_feature("Animacy", "Inan")

        self.assertEqual("Anim", a.feats["Animacy"])

    # # TODO Test parent relations, child relations etc.
    # def test_setting_parent_relation(self):
    #     # TODO maybe these tests shouldn't be here? If we set the relations through the API of Relation,
    #     #  maybe we should check through that, as there is little checkable code here anyway?
    #     raise NotImplementedError()

    # def test_get_tree_root(self):
    #     raise NotImplementedError()
    #
    # def test_iter_subtree(self):
    #     raise NotImplementedError()


if __name__ == '__main__':
    unittest.main()
