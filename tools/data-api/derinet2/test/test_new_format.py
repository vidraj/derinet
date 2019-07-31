import unittest
import io
from derinet import Lexicon, DerinetError, DerinetFileParseError


class TestNewFormat(unittest.TestCase):
    def test_load_empty(self):
        db = ""

        lexicon = Lexicon()
        db_file = io.StringIO(db)
        lexicon.load(db_file)

        self.assertEqual(len(list(lexicon.iter_lexemes())), 0)

    def test_load_single_lexeme(self):
        db = """0.0	0	lexeme							{}
"""

        lexicon = Lexicon()
        db_file = io.StringIO(db)
        lexicon.load(db_file)

        self.assertEqual(len(list(lexicon.iter_lexemes())), 1)
        self.assertEqual(list(lexicon.iter_lexemes())[0].lemma, "lexeme")

    def test_load_missing_json_error(self):
        db = """0.0	lexeme#N	lexeme	N						
"""

        lexicon = Lexicon()
        db_file = io.StringIO(db)
        with self.assertRaises(DerinetFileParseError):
            lexicon.load(db_file)

    def test_load_missing_lemma_error(self):
        db = """0.0	lexeme#N		N						{}
"""

        lexicon = Lexicon()
        db_file = io.StringIO(db)
        with self.assertRaises(DerinetFileParseError):
            lexicon.load(db_file)

    @unittest.expectedFailure
    def test_load_missing_lemid_error(self):
        """
        It is not clear at all whether lemids are necessary. Perhaps they can actually be empty?
        """
        db = """0.0		lexeme	N						{}
"""

        lexicon = Lexicon()
        db_file = io.StringIO(db)
        with self.assertRaises(DerinetFileParseError):
            lexicon.load(db_file)

    def test_load_no_trailing_newline(self):
        db = """0.0	0	lexeme							{}"""

        lexicon = Lexicon()
        db_file = io.StringIO(db)
        with self.assertRaises(DerinetFileParseError):
            lexicon.load(db_file)

    def test_load_malformed_id_1(self):
        db = """0	lexeme#N	lexeme	N						{}
"""

        lexicon = Lexicon()
        db_file = io.StringIO(db)
        with self.assertRaises(DerinetFileParseError):
            lexicon.load(db_file)

    def test_load_malformed_id_2(self):
        db = """	lexeme#N	lexeme	N						{}
"""

        lexicon = Lexicon()
        db_file = io.StringIO(db)
        with self.assertRaises(DerinetFileParseError):
            lexicon.load(db_file)

    def test_load_two_lexemes(self):
        db = """0.0	0	lexeme							{}
0.1	1	lexemer				0.0			{}
"""

        lexicon = Lexicon()
        db_file = io.StringIO(db)
        lexicon.load(db_file)

        self.assertEqual(len(list(lexicon.iter_lexemes())), 2)

    @unittest.expectedFailure
    def test_load_duplicate_lemid(self):
        """
        Duplicate lemids are to be expected, at least in Czech, given that
        they are constructed as a lemma+tagmask combination. Many homonyms
        share the same lemid.
        """
        db = """0.0	0	lexeme							{}
0.1	0	lexemer				0.0			{}
"""

        lexicon = Lexicon()
        db_file = io.StringIO(db)

        with self.assertRaises(DerinetFileParseError):
            lexicon.load(db_file)

    def test_load_duplicate_id_1(self):
        db = """0.0	0	lexeme							{}
0.1	1	lexemer				0.0			{}
0.1	2	lexemes				0.0			{}
"""

        lexicon = Lexicon()
        db_file = io.StringIO(db)

        with self.assertRaises(DerinetFileParseError):
            lexicon.load(db_file)

    def test_load_duplicate_id_2(self):
        db = """0.0	0	lexeme							{}

0.0	1	lexemer							{}
"""

        lexicon = Lexicon()
        db_file = io.StringIO(db)

        with self.assertRaises(DerinetFileParseError):
            lexicon.load(db_file)

    @unittest.expectedFailure
    def test_load_duplicate_load(self):
        """
        Since there is no distinguishing feature to the lexeme, there is no way
        of detecting duplicities. If we used the ID for that, we would effectively
        disable loading multiple databases into a single Lexicon instance.
        """
        db = """0.0	0	lexeme							{}
"""

        lexicon = Lexicon()
        db_file = io.StringIO(db)

        lexicon.load(db_file)
        db_file.seek(0)

        with self.assertRaises(DerinetError):
            lexicon.load(db_file)

        self.assertEqual(len(list(lexicon.iter_lexemes())), 1)

    def test_load_two_dbs(self):
        db1 = """0.0	0	lexeme							{}
"""
        db2 = """1.0	1	word							{}
"""

        lexicon = Lexicon()
        db_file_1 = io.StringIO(db1)
        db_file_2 = io.StringIO(db2)

        lexicon.load(db_file_1)
        lexicon.load(db_file_2)

        self.assertEqual(len(list(lexicon.iter_lexemes())), 2)

    def test_load_conjoined_trees_1(self):
        """
        In this test, we check that the loader rejects a file in which
        two trees are written without a blank line between them.
        """
        db = """0.0	0	lexeme							{}
1.1	1	word							{}
"""

        lexicon = Lexicon()
        db_file = io.StringIO(db)

        with self.assertRaises(DerinetFileParseError):
            lexicon.load(db_file)

    def test_load_conjoined_trees_2(self):
        db = """0.0	0	lexeme							{}
1.1	1	word				0.0			{}
"""

        lexicon = Lexicon()
        db_file = io.StringIO(db)

        with self.assertRaises(DerinetFileParseError):
            lexicon.load(db_file)

    def test_load_duplicate_id(self):
        db = """0.0	0	lexeme							{}
0.0	1	word							{}
"""

        lexicon = Lexicon()
        db_file = io.StringIO(db)

        with self.assertRaises(DerinetFileParseError):
            lexicon.load(db_file)

    def test_load_self_reference(self):
        db = """0.0	0	lexeme				0.0			{}
        """

        lexicon = Lexicon()
        db_file = io.StringIO(db)

        with self.assertRaises(DerinetFileParseError):
            lexicon.load(db_file)

    def test_load_forward_reference(self):
        db = """0.0	0	lexemer				0.1			{}
0.1	1	lexeme							{}
"""

        lexicon = Lexicon()
        db_file = io.StringIO(db)

        with self.assertRaises(DerinetFileParseError):
            lexicon.load(db_file)

    def test_load_out_of_tree_reference(self):
        """
        Cross-tree references are only allowed in secondary links, not in primary ones.
        """
        db = """0.0	0	lexeme							{}

1.0	1	lexemer				0.0			{}
"""

        lexicon = Lexicon()
        db_file = io.StringIO(db)

        with self.assertRaises(DerinetFileParseError):
            lexicon.load(db_file)

    def test_load_split_tree_1(self):
        db = """0.0	0	lexeme							{}

0.1	1	lexemer				0.0			{}
"""

        lexicon = Lexicon()
        db_file = io.StringIO(db)

        with self.assertRaises(DerinetFileParseError):
            lexicon.load(db_file)

    def test_load_split_tree_2(self):
        db = """0.0	0	lexeme							{}

0.1	1	lexemer							{}
"""

        lexicon = Lexicon()
        db_file = io.StringIO(db)

        with self.assertRaises(DerinetFileParseError):
            lexicon.load(db_file)

    def test_load_child_before_parent(self):
        db = """0.1	0	lexemer				0.0			{}
0.0	1	lexeme							{}
"""

        lexicon = Lexicon()
        db_file = io.StringIO(db)

        with self.assertRaises(DerinetFileParseError):
            lexicon.load(db_file)

    def test_load_segmentation(self):
        db = """7.3	aachenskost#N	aachenskost	N		End=6&Morph=aachen&Start=0&Type=Prefix|End=8&Start=6|End=11&Morph=ost&Start=8&Type=Suffix				{}
"""

        lexicon = Lexicon()
        db_file = io.StringIO(db)

        lexicon.load(db_file)

        lexeme = lexicon.get_lexemes("aachenskost")[0]
        self.assertEqual(len(lexeme.segmentation), 3)

    def test_load_segmentation_noninteger_start(self):
        db = """7.3	aachenskost#N	aachenskost	N		End=6&Morph=aachen&Start=0.1&Type=Prefix|End=8&Morph=sk&Start=6&Type=Root|End=11&Morph=ost&Start=8&Type=Suffix				{}
"""

        lexicon = Lexicon()
        db_file = io.StringIO(db)

        self.assertRaises(DerinetFileParseError, lexicon.load, db_file)

    def test_load_segmentation_noninteger_end(self):
        db = """7.3	aachenskost#N	aachenskost	N		End=6a&Morph=aachen&Start=0&Type=Prefix|End=8&Morph=sk&Start=6&Type=Root|End=11&Morph=ost&Start=8&Type=Suffix				{}
"""

        lexicon = Lexicon()
        db_file = io.StringIO(db)

        self.assertRaises(DerinetFileParseError, lexicon.load, db_file)

    def test_load_segmentation_missing_start(self):
        db = """7.3	aachenskost#N	aachenskost	N		End=6&Morph=aachen&Type=Prefix|End=8&Morph=sk&Start=6&Type=Root|End=11&Morph=ost&Start=8&Type=Suffix				{}
"""

        lexicon = Lexicon()
        db_file = io.StringIO(db)

        self.assertRaises(DerinetFileParseError, lexicon.load, db_file)

    def test_load_segmentation_missing_end(self):
        db = """7.3	aachenskost#N	aachenskost	N		Morph=aachen&Start=0&Type=Prefix|End=8&Morph=sk&Start=6&Type=Root|End=11&Morph=ost&Start=8&Type=Suffix				{}
"""

        lexicon = Lexicon()
        db_file = io.StringIO(db)

        self.assertRaises(DerinetFileParseError, lexicon.load, db_file)


if __name__ == '__main__':
    unittest.main()
