import unittest
from derinet.lexeme import Lexeme
import derinet.relation as r
from derinet.utils import DerinetCycleCreationError


class TestRelation(unittest.TestCase):
    def test_abstract_base(self):
        a = Lexeme("dog", "N")
        b = Lexeme("doggie", "N")

        with self.assertRaisesRegex(
                TypeError,
                "^Can't instantiate abstract class Relation with abstract methods .*__init__"
        ):
            r.Relation([a], a, [b], b)  # pylint: disable=abstract-class-instantiated

    def test_relation_creation(self):
        a = Lexeme("cat", "N")
        b = Lexeme("kitten", "N")
        c = Lexeme("Tom", "N")
        d = Lexeme("tomcat", "N")

        d_relation = r.DerivationalRelation(a, b)
        self.assertIsInstance(d_relation, r.Relation)

        self.assertIs(d_relation.main_source, a)
        self.assertIs(d_relation.main_target, b)

        c_relation = r.CompoundRelation((c, a), a, d)
        self.assertIsInstance(c_relation, r.Relation)

        self.assertIs(c_relation.main_source, a)
        self.assertIs(c_relation.main_target, d)

    def test_relation_add_to_lexemes(self):
        a = Lexeme("cat", "N")
        b = Lexeme("kitten", "N")
        c = Lexeme("Tom", "N")
        d = Lexeme("tomcat", "N")

        d_relation = r.DerivationalRelation(a, b)
        d_relation.add_to_lexemes()

        self.assertEqual(len(a.child_relations), 1)
        self.assertIs(a.child_relations[0], d_relation)

        self.assertEqual(len(a.children), 1)
        self.assertIs(a.children[0], b)

        self.assertIs(b.parent_relation, d_relation)
        self.assertIs(b.parent, a)

        c_relation = r.CompoundRelation((c, a), a, d)
        c_relation.add_to_lexemes()

        self.assertEqual(len(a.child_relations), 2)
        self.assertEqual(len(a.children), 2)
        self.assertEqual(len(c.child_relations), 1)
        self.assertEqual(len(c.children), 0)

        self.assertIs(d.parent_relation, c_relation)
        self.assertIs(d.parent, a)

    def test_composition_head_not_in_sources(self):
        a = Lexeme("cat", "N")
        b = Lexeme("kitten", "N")
        c = Lexeme("Tom", "N")
        d = Lexeme("tomcat", "N")

        with self.assertRaises(ValueError):
            r.CompoundRelation((c, b), a, d)

    def test_composition_target_in_sources(self):
        a = Lexeme("cat", "N")
        d = Lexeme("tomcat", "N")

        with self.assertRaises(DerinetCycleCreationError):
            r.CompoundRelation((d, a), a, d)

    def test_relation_reflexive(self):
        a = Lexeme("cat", "N")
        b = Lexeme("kitten", "N")

        with self.assertRaises(DerinetCycleCreationError):
            r.DerivationalRelation(a, a)


    def test_dict_nonexistence(self):
        """
        This verifies that the __dict__ object is not being created for relations,
        resulting in less garbage, smaller memory footprint and faster object creation.
        """
        a = Lexeme("cat", "N")
        b = Lexeme("kitten", "N")

        relation = r.DerivationalRelation(a, b)
        with self.assertRaises(AttributeError):
            # noinspection PyDunderSlots,PyUnresolvedReferences
            relation.nonexistent_attribute = True  # pylint: disable=assigning-non-slot

    def test_derivation_equality_reflexive(self):
        a = Lexeme("cat", "N")
        b = Lexeme("kitten", "N")

        relation = r.DerivationalRelation(a, b)
        self.assertIs(relation == relation, True)
        self.assertIs(relation != relation, False)

    def test_derivation_equality(self):
        a = Lexeme("cat", "N")
        b = Lexeme("kitten", "N")

        relation_a = r.DerivationalRelation(a, b)
        relation_b = r.DerivationalRelation(a, b)
        self.assertIs(relation_a == relation_b, True)
        self.assertIs(relation_b == relation_a, True)
        self.assertIs(relation_a != relation_b, False)
        self.assertIs(relation_b != relation_a, False)

    def test_derivation_nonequality_simple(self):
        a = Lexeme("cat", "N")
        b = Lexeme("kitten", "N")

        relation_a = r.DerivationalRelation(a, b)
        relation_b = r.DerivationalRelation(b, a)
        self.assertIs(relation_a == relation_b, False)
        self.assertIs(relation_a != relation_b, True)

    def test_derivation_nonequality_equal_lexeme(self):
        a = Lexeme("cat", "N")
        b = Lexeme("cat", "N")
        c = Lexeme("kitten", "N")

        relation_a = r.DerivationalRelation(a, c)
        relation_b = r.DerivationalRelation(b, c)
        self.assertIs(relation_a == relation_b, False)
        self.assertIs(relation_a != relation_b, True)

    def test_composition_equality(self):
        a = Lexeme("cat", "N")
        b = Lexeme("Tom", "N")
        c = Lexeme("tomcat", "N")

        relation_a = r.CompoundRelation((b, a), a, c)
        relation_b = r.CompoundRelation((b, a), a, c)

        self.assertIs(relation_a == relation_b, True)

    def test_composition_equality_different_order(self):
        a = Lexeme("cat", "N")
        b = Lexeme("Tom", "N")
        c = Lexeme("tomcat", "N")

        relation_a = r.CompoundRelation((b, a), a, c)
        relation_b = r.CompoundRelation((a, b), a, c)

        self.assertIs(relation_a == relation_b, False)

    def test_composition_equality_different_head(self):
        a = Lexeme("cat", "N")
        b = Lexeme("Tom", "N")
        c = Lexeme("tomcat", "N")

        relation_a = r.CompoundRelation((a, b), a, c)
        relation_b = r.CompoundRelation((a, b), b, c)

        self.assertIs(relation_a == relation_b, False)

    def test_composition_equality_different_length(self):
        a = Lexeme("cat", "N")
        b = Lexeme("Tom", "N")
        c = Lexeme("tomcat", "N")

        relation_a = r.CompoundRelation((a, b), a, c)
        relation_b = r.CompoundRelation((a, b, a), a, c)

        self.assertIs(relation_a == relation_b, False)
        self.assertIs(relation_b == relation_a, False)

    def test_hash(self):
        """
        This tests that the hash function of relations is consistent with their equality comparison.
        """
        a = Lexeme("dog", "N")
        b = Lexeme("doggie", "N")

        relation_a = r.DerivationalRelation(a, b)
        relation_b = r.DerivationalRelation(a, b)
        relation_c = r.DerivationalRelation(a, b)
        relation_d = r.DerivationalRelation(a, b)

        set_of_relations = {relation_a, relation_b, relation_c, relation_d}
        self.assertEqual(len(set_of_relations), 1)
        self.assertSetEqual({relation_a}, set_of_relations)
        self.assertIn(relation_a, {relation_b})

    def test_other_sources(self):
        a = Lexeme("cat", "N")
        b = Lexeme("Tom", "N")
        c = Lexeme("tomcat", "N")

        relation = r.CompoundRelation((a, b), a, c)
        self.assertEqual(relation.other_sources, (b,))

        relation = r.CompoundRelation((b, a, b, b), a, c)
        self.assertEqual(relation.other_sources, (b, b, b))


if __name__ == '__main__':
    unittest.main()
