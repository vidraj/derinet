import unittest
from derinet.lexeme import Lexeme
from derinet.utils import DerinetMorphError


class TestMorphs(unittest.TestCase):
    def test_segmentation_default(self):
        lexeme = Lexeme("unnecessarily", "A")
        self.assertEqual(1, len(lexeme.segmentation))
        self.assertEqual("unnecessarily", lexeme.segmentation[0]["morph"])

    def test_morph_add(self):
        lexeme = Lexeme("unnecessarily", "A")
        lexeme.add_morph(0, 2, {"type": "prefix"})

        self.assertEqual(2, len(lexeme.segmentation))
        self.assertEqual("un", lexeme.segmentation[0]["morph"])

    def test_morph_add_multiple(self):
        lexeme = Lexeme("unnecessarily", "A")
        lexeme.add_morph(0, 2, {"type": "prefix"})
        lexeme.add_morph(2, 11, {"type": "root", "morpheme": "necessary"})
        lexeme.add_morph(11, 13, {"type": "suffix"})

        self.assertEqual(3, len(lexeme.segmentation))
        self.assertEqual("un", lexeme.segmentation[0]["morph"])
        self.assertEqual("necessari", lexeme.segmentation[1]["morph"])
        self.assertEqual("ly", lexeme.segmentation[2]["morph"])

    def test_morph_add_overlapping(self):
        lexeme = Lexeme("unnecessarily", "A")
        lexeme.add_morph(0, 2, {"type": "prefix"})
        lexeme.add_morph(2, 11, {"type": "root", "morpheme": "necessary"})

        self.assertRaises(
            DerinetMorphError,
            lexeme.add_morph,
            10,
            13,
            {"type": "suffix"}
        )

    def test_morph_add_overlapping_short(self):
        lexeme = Lexeme("dogs", "N")
        lexeme.add_morph(3, 4, {"type": "suffix"})

        self.assertRaises(
            DerinetMorphError,
            lexeme.add_morph,
            2,
            4,
            {"type": "suffix"}
        )

    def test_morph_add_identical(self):
        lexeme = Lexeme("dogs", "N")
        lexeme.add_morph(3, 4, {"type": "suffix"})

        # TODO do we want an exception to be raised here, or rather a silent acceptance of the duplicate?
        self.assertRaises(
            DerinetMorphError,
            lexeme.add_morph,
            3,
            4,
            {"type": "suffix"}
        )

    def test_morph_add_oob(self):
        lexeme = Lexeme("dog", "N")

        self.assertRaises(
            ValueError,
            lexeme.add_morph,
            0,
            4,
            {"type": "root"}
        )

        self.assertRaises(
            ValueError,
            lexeme.add_morph,
            -1,
            1,
            {"type": "prefix"}
        )

    def test_morph_add_zero_len(self):
        lexeme = Lexeme("dog", "N")

        self.assertRaises(
            ValueError,
            lexeme.add_morph,
            0,
            0,
            {"type": "prefix"}
        )

        self.assertRaises(
            ValueError,
            lexeme.add_morph,
            1,
            1,
            {"type": "root"}
        )

    def test_boundary_add(self):
        lexeme = Lexeme("dogs", "N")
        lexeme.add_boundary(3, True)
        lexeme.add_boundary(2, False)

        self.assertTrue(lexeme.is_boundary_allowed(3))
        self.assertFalse(lexeme.is_boundary_allowed(2))

    def test_boundary_add_oob(self):
        lexeme = Lexeme("dog", "N")
        self.assertRaises(ValueError, lexeme.add_boundary, -1, True)
        self.assertRaises(ValueError, lexeme.add_boundary, 4, True)
        self.assertRaises(ValueError, lexeme.add_boundary, -1, False)
        self.assertRaises(ValueError, lexeme.add_boundary, 4, False)

    def test_boundary_default(self):
        lexeme = Lexeme("dogs", "N")

        self.assertTrue(lexeme.is_boundary_allowed(0))
        self.assertTrue(lexeme.is_boundary_allowed(1))
        self.assertTrue(lexeme.is_boundary_allowed(2))
        self.assertTrue(lexeme.is_boundary_allowed(3))
        self.assertTrue(lexeme.is_boundary_allowed(4))

    def test_boundary_oob(self):
        lexeme = Lexeme("dogs", "N")

        self.assertFalse(lexeme.is_boundary_allowed(-1))
        self.assertFalse(lexeme.is_boundary_allowed(5))

    def test_boundary_forbid_edge(self):
        """
        Test that the lemma edges cannot be forbidden as splits.
        """
        lexeme = Lexeme("dog", "N")
        self.assertRaises(DerinetMorphError, lexeme.add_boundary, 0, False)
        self.assertRaises(DerinetMorphError, lexeme.add_boundary, 3, False)

    def test_boudary_set_default(self):
        lexeme = Lexeme("dogs", "N")
        lexeme.add_boundary(3, True)
        lexeme.add_boundary(2, False)

        self.assertTrue(lexeme.is_boundary_allowed(3, False))
        self.assertFalse(lexeme.is_boundary_allowed(2, True))

        self.assertFalse(lexeme.is_boundary_allowed(0, False))
        self.assertFalse(lexeme.is_boundary_allowed(1, False))
        self.assertFalse(lexeme.is_boundary_allowed(4, False))

    def test_boundary_splits(self):
        """
        Check that adding a positive morph boundary splits the word into morphs.
        """
        lexeme = Lexeme("dogs", "N")
        lexeme.add_boundary(3, True)

        self.assertEqual(2, len(lexeme.segmentation))
        self.assertEqual("dog", lexeme.segmentation[0]["morph"])
        self.assertEqual("s", lexeme.segmentation[1]["morph"])

    def test_nonboundary_nonsplits(self):
        """
        Check that adding a negative morph boundary doesn't split the word into morphs.
        """
        lexeme = Lexeme("dogs", "N")
        lexeme.add_boundary(2, False)

        self.assertEqual(1, len(lexeme.segmentation))
        self.assertEqual("dogs", lexeme.segmentation[0]["morph"])

    def test_morph_allows_boundaries(self):
        lexeme = Lexeme("unnecessarily", "A")
        lexeme.add_morph(0, 2, {"type": "prefix"})
        lexeme.add_morph(2, 11, {"type": "root", "morpheme": "necessary"})
        lexeme.add_morph(11, 13, {"type": "suffix"})

        self.assertTrue(lexeme.is_boundary_allowed(0, False))
        self.assertTrue(lexeme.is_boundary_allowed(2, False))
        self.assertTrue(lexeme.is_boundary_allowed(11, False))
        self.assertTrue(lexeme.is_boundary_allowed(13, False))

    def test_morph_disallows_boundaries(self):
        lexeme = Lexeme("unnecessarily", "A")
        lexeme.add_morph(0, 2, {"type": "prefix"})
        lexeme.add_morph(2, 11, {"type": "root", "morpheme": "necessary"})
        lexeme.add_morph(11, 13, {"type": "suffix"})

        self.assertFalse(lexeme.is_boundary_allowed(1))
        self.assertFalse(lexeme.is_boundary_allowed(3))
        self.assertFalse(lexeme.is_boundary_allowed(7))
        self.assertFalse(lexeme.is_boundary_allowed(10))
        self.assertFalse(lexeme.is_boundary_allowed(12))


if __name__ == '__main__':
    unittest.main()
