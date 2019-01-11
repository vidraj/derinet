import unittest
import io

from nose.tools import assert_raises, raises

from derinet import DeriNetError, LexemeNotFoundError, LexemeAlreadyExistsError, LexemeAmbiguousError
from derinet.derinet import DeriNet
from derinet.utils import Node


class TestFiles(unittest.TestCase):

    def setUp(self):
        data_v1 = """0\tAaasen\tAaasen_;S\tN\t
1\tAaasenův\tAaasenův_;S_^(*2)\tA\t0
2\tAabar\tAabar_;S\tN\t
3\tAabarův\tAabarův_;S_^(*2)\tA\t2
4\tAabarův\tAabarův_;X_^(*2)\tX\t2
"""
        data_v2 = """
        """
        data_v3 = """455709	pes	pes_^(zvíře)	N	
580101	psice	psice_^(*3ík)	N	580107
580102	psíček	psíček	N	580107
580103	psičin	psičin_^(*3ce)	A	580101
580106	psíčkův	psíčkův_^(*3ek)	A	580102
580107	psík	psík	N	455709
580111	psíkův	psíkův_^(*2)	A	580107
580178	psovitě	psovitě_^(*1ý)	D	580180
580179	psovitost	psovitost_^(*3ý)	N	580180
580180	psovitý	psovitý	A	455709
580230	psův	psův_^(zvíře)_(*3es)	A	455709
"""

        data_v4 = """1\ttest\ttest-1\tN\t
2\ttest\ttest-2\tN\t
3\ttestův\ttestův-1\tN\t2
4\ttestův\ttestův-2\tN\t1
5\tzatrest\tzatrest\tN\t3
"""

        self.data_stream_v1 = io.StringIO(data_v1)
        self.data_stream_v2 = io.StringIO(data_v2)
        self.data_stream_v3 = io.StringIO(data_v3)
        self.data_stream_v4 = io.StringIO(data_v4)

    def test_data_v1_loaded(self):
        derinet = DeriNet(fname=self.data_stream_v1)
        desired_data = [Node(lex_id=0, pretty_id='0', lemma='Aaasen', morph='Aaasen_;S', pos='N', tag_mask='', parent_id='', composition_parents=[], misc={}, children=[1]),
                        Node(lex_id=1, pretty_id='1', lemma='Aaasenův', morph='Aaasenův_;S_^(*2)', pos='A', tag_mask='', parent_id=0, composition_parents=[], misc={}, children=[]),
                        Node(lex_id=2, pretty_id='2', lemma='Aabar', morph='Aabar_;S', pos='N', tag_mask='', parent_id='', composition_parents=[], misc={}, children=[3,4]),
                        Node(lex_id=3, pretty_id='3', lemma='Aabarův', morph='Aabarův_;S_^(*2)', pos='A', tag_mask='', parent_id=2, composition_parents=[], misc={}, children=[]),
                        Node(lex_id=4, pretty_id='4', lemma='Aabarův', morph='Aabarův_;X_^(*2)', pos='X', tag_mask='', parent_id=2, composition_parents=[], misc={}, children=[])
                        ]
        self.assertEqual(derinet._data, desired_data)

    def test_proper_id_is_get_by_lemma(self):
        derinet = DeriNet(fname=self.data_stream_v1)
        nid = derinet.get_id('Aaasen')
        self.assertEqual(nid, 0)

    def test_proper_id_is_get_by_lemma_pos(self):
        derinet = DeriNet(fname=self.data_stream_v1)
        nid = derinet.get_id('Aabarův', pos='A')
        self.assertEqual(nid, 3)
        nid = derinet.get_id('Aabarův', pos='X')
        self.assertEqual(nid, 4)

    def test_proper_id_is_get_by_lemma_morph(self):
        derinet = DeriNet(fname=self.data_stream_v1)
        nid = derinet.get_id('Aabarův', morph='Aabarův_;S_^(*2)')
        self.assertEqual(nid, 3)
        nid = derinet.get_id('Aabarův', morph='Aabarův_;X_^(*2)')
        self.assertEqual(nid, 4)

    def test_lexeme_not_found_raised(self):
        derinet = DeriNet(fname=self.data_stream_v1)
        with assert_raises(LexemeNotFoundError):
            derinet.get_id('Neexistujici')
        with assert_raises(LexemeNotFoundError):
            derinet.get_id('Aabarův', morph='Neexistujici')
        with assert_raises(LexemeNotFoundError):
            derinet.get_id('Aabarův', pos='Neexistujici')

    def test_lexeme_exists(self):
        derinet = DeriNet(fname=self.data_stream_v1)

        self.assertTrue(derinet.lexeme_exists(Node(lex_id=3, pretty_id='3', lemma='Aabarův', morph='Aabarův_;S_^(*2)', pos='A', tag_mask='', parent_id=2, composition_parents=[], misc={}, children=[])))
        self.assertTrue(derinet.lexeme_exists(Node(lex_id=1, pretty_id='3', lemma='Aabarův', morph='Aabarův_;S_^(*2)', pos='A', tag_mask='', parent_id=2, composition_parents=[], misc={}, children=[])))
        self.assertTrue(derinet.lexeme_exists(Node(lex_id=None, pretty_id='3', lemma='Aabarův', morph='Aabarův_;S_^(*2)', pos='A', tag_mask=None, parent_id=None, composition_parents=None, misc=None, children=None)))
        self.assertTrue(derinet.lexeme_exists(Node(lex_id=None, pretty_id='3', lemma='Aabarův', morph='Aabarův_;S_^(*2)', pos='A', tag_mask='abcd', parent_id=1, composition_parents=[2, 0], misc={"gender": "F"}, children=[4])))
        self.assertTrue(derinet.lexeme_exists(Node(lex_id=3, pretty_id=None, lemma='Aabarův', morph='Aabarův_;S_^(*2)', pos='A', tag_mask='', parent_id=2, composition_parents=[], misc={}, children=[])))

        self.assertFalse(derinet.lexeme_exists(Node(lex_id=3, pretty_id='2', lemma='Aabarův', morph='Aabarův_;S_^(*2)', pos='A', tag_mask='', parent_id=2, composition_parents=[], misc={}, children=[])))
        self.assertFalse(derinet.lexeme_exists(Node(lex_id=3, pretty_id='3', lemma='Aabarůvovo', morph='Aabarův_;S_^(*2)', pos='A', tag_mask='', parent_id=2, composition_parents=[], misc={}, children=[])))
        self.assertFalse(derinet.lexeme_exists(Node(lex_id=3, pretty_id='3', lemma='Aabarův', morph='Aabarův_;S_^(*2a)', pos='A', tag_mask='', parent_id=2, composition_parents=[], misc={}, children=[])))
        self.assertFalse(derinet.lexeme_exists(Node(lex_id=3, pretty_id='3', lemma='Aabarův', morph='Aabarův_;S_^(*2)', pos='D', tag_mask='', parent_id=2, composition_parents=[], misc={}, children=[])))

    def test_get_unique_id(self):
        derinet = DeriNet(fname=self.data_stream_v1)

        self.assertEqual(derinet.get_unique_id("Aaasen", "N", "Aaasen_;S"), 0)
        self.assertEqual(derinet.get_unique_id("Aaasen"), 0)
        self.assertRaises(LexemeNotFoundError, derinet.get_unique_id, "abc", "N", "abc")
        self.assertRaises(LexemeAmbiguousError, derinet.get_unique_id, "Aabarův")
        self.assertEqual(derinet.get_unique_id("Aabarův", "A"), 3)
        self.assertEqual(derinet.get_unique_id("Aabarův", morph="Aabarův_;X_^(*2)"), 4)


    def test_add_lexeme(self):
        derinet = DeriNet(fname=self.data_stream_v1)

        test_lexeme = Node(lex_id=None, pretty_id='5', lemma='lexém', morph='lexém', pos='N', tag_mask='', parent_id=None, composition_parents=[], misc={}, children=[])
        self.assertFalse(derinet.lexeme_exists(test_lexeme))
        derinet.add_lexeme(test_lexeme)
        self.assertTrue(derinet.lexeme_exists(test_lexeme))

        with assert_raises(LexemeAlreadyExistsError):
            derinet.add_lexeme(Node(lex_id=None, pretty_id='5', lemma='lexém', morph='lexém', pos='N', tag_mask='', parent_id=None, composition_parents=[], misc={}, children=[]))

        with assert_raises(DeriNetError): # It is possible for this to raise a different error. But it must be a subclass of DeriNetError anyway.
            derinet.add_lexeme(Node(lex_id=None, pretty_id='5', lemma='pseudolexém', morph='lexém-2', pos='N', tag_mask='', parent_id=None, composition_parents=[], misc={}, children=[]))

        # TODO test inserting malformatted lexemes.

    def test_database_load_pretty_ids(self):
        derinet = DeriNet(fname=self.data_stream_v3)

        id_pes = derinet.get_id("pes", "N")
        id_psovite = derinet.get_id("psovitě", "D")
        id_psik = derinet.get_id("psík", "N")
        id_psickuv = derinet.get_id("psíčkův", "A")

        derinet._valid_lex_id_or_raise(id_pes)
        derinet._valid_lex_id_or_raise(id_psovite)
        derinet._valid_lex_id_or_raise(id_psik)
        derinet._valid_lex_id_or_raise(id_psickuv)

        self.assertEqual(id_pes, derinet.get_parent(id_psik).lex_id)
        self.assertEqual(id_psik, derinet.get_parent(derinet.get_parent(id_psickuv).lex_id).lex_id)

    @raises(LexemeNotFoundError)
    def test_bad_id_raises_exception(self):
        derinet = DeriNet(fname=self.data_stream_v3)

        derinet._valid_lex_id_or_raise(42)

    def test_exists_loop_simple(self):
        derinet = DeriNet(fname=self.data_stream_v1)

        id_aaasen = derinet.get_id("Aaasen", "N")
        id_aaasenuv = derinet.get_id("Aaasenův", "A")
        id_aabar = derinet.get_id("Aabar", "N")
        id_aabaruva = derinet.get_id("Aabarův", "A")
        id_aabaruvx = derinet.get_id("Aabarův", "X")

        self.assertFalse(derinet.exists_loop(id_aaasen))
        self.assertFalse(derinet.exists_loop(id_aaasenuv))
        self.assertFalse(derinet.exists_loop(id_aabar))
        self.assertFalse(derinet.exists_loop(id_aabaruva))
        self.assertFalse(derinet.exists_loop(id_aabaruvx))

        self.assertFalse(derinet.exists_loop(id_aaasen, id_aaasenuv))
        self.assertFalse(derinet.exists_loop(id_aaasen, id_aabar))
        self.assertFalse(derinet.exists_loop(id_aaasen, id_aabaruva))
        self.assertFalse(derinet.exists_loop(id_aaasen, id_aabaruvx))
        self.assertFalse(derinet.exists_loop(id_aabaruva, id_aabaruvx))

        self.assertTrue(derinet.exists_loop(id_aaasenuv, id_aaasen))
        self.assertTrue(derinet.exists_loop(id_aabaruva, id_aabar))

    def test_exists_loop_complex(self):
        derinet = DeriNet(fname=self.data_stream_v3)

        id_pes = derinet.get_id("pes", "N")
        id_psovite = derinet.get_id("psovitě", "D")
        id_psik = derinet.get_id("psík", "N")
        id_psickuv = derinet.get_id("psíčkův", "A")

        self.assertFalse(derinet.exists_loop(id_pes))
        self.assertFalse(derinet.exists_loop(id_psovite))
        self.assertFalse(derinet.exists_loop(id_psik))
        self.assertFalse(derinet.exists_loop(id_psickuv))

        self.assertFalse(derinet.exists_loop(id_pes, id_psovite))
        self.assertFalse(derinet.exists_loop(id_pes, id_psik))
        self.assertFalse(derinet.exists_loop(id_pes, id_psickuv))
        self.assertFalse(derinet.exists_loop(id_psovite, id_psik))
        self.assertFalse(derinet.exists_loop(id_psovite, id_psickuv))
        self.assertFalse(derinet.exists_loop(id_psik, id_psickuv))
        self.assertFalse(derinet.exists_loop(id_psik, id_psovite))
        self.assertFalse(derinet.exists_loop(id_psickuv, id_psovite))

        self.assertTrue(derinet.exists_loop(id_psovite, id_pes))
        self.assertTrue(derinet.exists_loop(id_psik, id_pes))
        self.assertTrue(derinet.exists_loop(id_psickuv, id_pes))
        self.assertTrue(derinet.exists_loop(id_psickuv, id_psik))


    def test_roots_load(self):
        derinet = DeriNet(fname=self.data_stream_v1)

        expected_roots = {0, 2}
        self.assertEqual(derinet._roots, expected_roots)

    def test_roots_add_lexeme(self):
        derinet = DeriNet(fname=self.data_stream_v2)

        expected_roots_0 = set()
        self.assertEqual(derinet._roots, expected_roots_0)

        derinet.add_lexeme(Node(lex_id=None, pretty_id='0', lemma='lexém', morph='lexém', pos='N', tag_mask='',
                                parent_id=None, composition_parents=[], misc={}, children=[]))
        expected_roots_1 = {0}
        self.assertEqual(derinet._roots, expected_roots_1)

        derinet.add_lexeme(Node(lex_id=None, pretty_id='1', lemma='lexéma', morph='lexém', pos='N', tag_mask='',
                                parent_id=None, composition_parents=[], misc={}, children=[]))
        expected_roots_2 = {0, 1}
        self.assertEqual(derinet._roots, expected_roots_2)


    def test_roots_add_derivation(self):
        derinet = DeriNet(fname=self.data_stream_v1)

        test_lexeme = Node(lex_id=None, pretty_id='5', lemma='lexém', morph='lexém', pos='N', tag_mask='',
                           parent_id=None, composition_parents=[], misc={}, children=[])
        derinet.add_lexeme(test_lexeme)

        expected_roots_1 = {0, 2, 5}
        self.assertEqual(derinet._roots, expected_roots_1)

        derinet.add_derivation(5, 4)
        expected_roots_2 = {0, 2}
        self.assertEqual(derinet._roots, expected_roots_2)

    def test_roots_remove_derivation(self):
        derinet = DeriNet(fname=self.data_stream_v1)

        expected_roots_1 = {0, 2}
        self.assertEqual(derinet._roots, expected_roots_1)

        derinet.remove_derivation(4, 2)
        expected_roots_2 = {0, 2, 4}
        self.assertEqual(derinet._roots, expected_roots_2)

    def test_roots_updated_when_sort(self):
        derinet = DeriNet(fname=self.data_stream_v3)

        test_lexeme = Node(lex_id=None, pretty_id='5', lemma='neseřazen', morph='neseřazen', pos='A', tag_mask='',
                           parent_id=None, composition_parents=[], misc={}, children=[])
        derinet.add_lexeme(test_lexeme)
        # pes, neseřazen
        expected_roots_1 = {0, 11}
        self.assertEqual(derinet._roots, expected_roots_1)
        derinet.sort()
        # neseřazen seřazen, pes
        expected_roots_2 = {0, 1}
        self.assertEqual(derinet._roots, expected_roots_2)

    def test_homonym_selection(self):
        derinet = DeriNet(fname=self.data_stream_v4)
        # It should be possible to remove the existing derivation, but it should
        #  not be possible to remove the nonexisting derivation.
        # Bug #16 caused homonyms to be confused, this should prevent
        #  reoccurence.
        homonym_1_id = derinet.get_id("test", "N", "test-1")
        homonym_2_id = derinet.get_id("test", "N", "test-2")
        child_1_id = derinet.get_id("testův", "N", "testův-1")
        child_2_id = derinet.get_id("testův", "N", "testův-2")
        grandchild_id = derinet.get_id("zatrest", "N", "zatrest")

        self.assertNotEqual(homonym_1_id, homonym_2_id)
        self.assertNotEqual(child_1_id, child_2_id)

        homonym_1 = derinet.get_lexeme(homonym_1_id)
        homonym_2 = derinet.get_lexeme(homonym_2_id)
        child_1 = derinet.get_lexeme(child_1_id)
        child_2 = derinet.get_lexeme(child_2_id)
        grandchild = derinet.get_lexeme(grandchild_id)

        self.assertNotEqual(homonym_1, homonym_2)
        self.assertNotEqual(child_1, child_2)

        self.assertFalse(derinet.remove_derivation(child_1, homonym_1))
        self.assertTrue(derinet.remove_derivation(child_1, homonym_2))

        self.assertFalse(derinet.remove_derivation(child_2, homonym_2))
        self.assertTrue(derinet.remove_derivation(child_2, homonym_1))

        self.assertFalse(derinet.remove_derivation(grandchild, child_2))
        self.assertTrue(derinet.remove_derivation(grandchild, child_1))

    def test_lexeme_removal(self):
        derinet = DeriNet(fname=self.data_stream_v1)
        derinet.remove_lexeme("Aabar")

        self.assertEqual(derinet.search_lexemes("Aabar"), [])

        expected_data = [
            Node(lex_id=0, pretty_id='0', lemma='Aaasen', morph='Aaasen_;S', pos='N', tag_mask='', parent_id='', composition_parents=[], misc={}, children=[1]),
            Node(lex_id=1, pretty_id='1', lemma='Aaasenův', morph='Aaasenův_;S_^(*2)', pos='A', tag_mask='', parent_id=0, composition_parents=[], misc={}, children=[]),
            None,
            Node(lex_id=3, pretty_id='3', lemma='Aabarův', morph='Aabarův_;S_^(*2)', pos='A', tag_mask='', parent_id='', composition_parents=[], misc={}, children=[]),
            Node(lex_id=4, pretty_id='4', lemma='Aabarův', morph='Aabarův_;X_^(*2)', pos='X', tag_mask='', parent_id='', composition_parents=[], misc={}, children=[])
        ]
        self.assertEqual(derinet._data, expected_data)

        expected_roots = {0, 3, 4}
        self.assertEqual(derinet._roots, expected_roots)
