import unittest
from derinet import DerinetMorphError, Format, Lexicon
import io


class TestMorphStorage(unittest.TestCase):
    def test_morph_roundtrip(self):
        lexicon = Lexicon()
        lexeme = lexicon.create_lexeme("unnecessarily", "A")
        lexeme.add_morph(0, 2, {"Type": "Prefix"})
        lexeme.add_morph(2, 11, {"Type": "Root", "Morpheme": "necessary"})
        lexeme.add_morph(11, 13, {"Type": "Suffix"})

        db_file = io.StringIO()
        lexicon.save(db_file, fmt=Format.DERINET_V2)
        db_file.seek(0)

        lexicon2 = Lexicon()
        lexicon2.load(db_file, fmt=Format.DERINET_V2)
        lexeme2 = lexicon2.get_lexemes("unnecessarily", "A")[0]

        self.assertEqual(len(lexeme.segmentation), len(lexeme2.segmentation))
        for morph, morph2 in zip(lexeme.segmentation, lexeme2.segmentation):
            self.assertEqual(morph, morph2)

    def test_boundary_roundtrip(self):
        lexicon = Lexicon()
        lexeme = lexicon.create_lexeme("dogs", "N")
        lexeme.add_boundary(3, True)
        lexeme.add_boundary(2, False)

        db_file = io.StringIO()
        lexicon.save(db_file, fmt=Format.DERINET_V2)
        db_file.seek(0)

        lexicon2 = Lexicon()
        lexicon2.load(db_file, fmt=Format.DERINET_V2)
        lexeme2 = lexicon2.get_lexemes("dogs", "N")[0]

        for i in range(len(lexeme.lemma) + 1):
            self.assertEqual(lexeme.is_boundary_allowed(i), lexeme2.is_boundary_allowed(i))

        self.assertEqual(len(lexeme.segmentation), len(lexeme2.segmentation))
        for morph, morph2 in zip(lexeme.segmentation, lexeme2.segmentation):
            self.assertEqual(morph, morph2)
