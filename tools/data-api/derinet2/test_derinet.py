import unittest
import io

from nose.tools import assert_raises

from . import LexemeNotFoundError
from .derinet import DeriNet
from .utils import Node


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
        self.data_stream_v1 = io.StringIO(data_v1)
        self.data_stream_v2 = io.StringIO(data_v2)


    def test_data_v1_loaded(self):
        derinet = DeriNet(fname=self.data_stream_v1)
        desired_data = [Node(lex_id=0, pretty_id='0', lemma='Aaasen', morph='Aaasen_;S', pos='N', tag_mask='', parent_id='', composition_parents=[], misc={}, children=[
                            Node(lex_id=1, pretty_id='1', lemma='Aaasenův', morph='Aaasenův_;S_^(*2)', pos='A', tag_mask='', parent_id=0, composition_parents=[], misc={}, children=[])
                        ]),
                        Node(lex_id=1, pretty_id='1', lemma='Aaasenův', morph='Aaasenův_;S_^(*2)', pos='A', tag_mask='', parent_id=0, composition_parents=[], misc={}, children=[]),
                        Node(lex_id=2, pretty_id='2', lemma='Aabar', morph='Aabar_;S', pos='N', tag_mask='', parent_id='', composition_parents=[], misc={}, children=[
                            Node(lex_id=3, pretty_id='3', lemma='Aabarův', morph='Aabarův_;S_^(*2)', pos='A', tag_mask='', parent_id=2, composition_parents=[], misc={}, children=[]),
                            Node(lex_id=4, pretty_id='4', lemma='Aabarův', morph='Aabarův_;X_^(*2)', pos='X', tag_mask='', parent_id=2, composition_parents=[], misc={}, children=[])
                        ]),
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
