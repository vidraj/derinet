import unittest
from derinet.lexicon import Lexicon
from derinet.utils import DerinetLexemeDeleteError

class TestDeletingLexemes(unittest.TestCase):
    def test_lexeme_deletion_basic(self):
        lexicon = Lexicon()

        lex = lexicon.create_lexeme("dog", "N")

        self.assertEqual(1, len(list(lexicon.iter_lexemes())))
        lexicon.delete_lexeme(lex)
        self.assertEqual(0, len(list(lexicon.iter_lexemes())))

    def test_lexeme_deletion_multiple(self):
        lexicon = Lexicon()

        lex_a = lexicon.create_lexeme("dog", "N")
        lex_b = lexicon.create_lexeme("doggie", "N")

        self.assertEqual(2, len(list(lexicon.iter_lexemes())))
        lexicon.delete_lexeme(lex_a)
        self.assertEqual(1, len(list(lexicon.iter_lexemes())))

        self.assertEqual([], lexicon.get_lexemes("dog"))
        self.assertEqual([lex_b], lexicon.get_lexemes("doggie"))

        lexicon.delete_lexeme(lex_b)
        self.assertEqual(0, len(list(lexicon.iter_lexemes())))
        self.assertEqual([], lexicon.get_lexemes("doggie"))

    def test_lexeme_deletion_nonexistent(self):
        lexicon = Lexicon()

        lex_a = lexicon.create_lexeme("dog", "N")
        lex_b = lexicon.create_lexeme("doggie", "N")

        lexicon.delete_lexeme(lex_a)
        with self.assertRaises(ValueError):
            lexicon.delete_lexeme(lex_a)

    def test_deleting_derived_lexemes_fail(self):
        lexicon = Lexicon()

        lex_a = lexicon.create_lexeme("dog", "N")
        lex_b = lexicon.create_lexeme("doggie", "N")

        lexicon.add_derivation(lex_a, lex_b)

        with self.assertRaises(DerinetLexemeDeleteError):
            lexicon.delete_lexeme(lex_a)

        with self.assertRaises(DerinetLexemeDeleteError):
            lexicon.delete_lexeme(lex_b)
