import unittest
import derinet.utils as u


class TestUtils(unittest.TestCase):
    def test_parse_v1_id(self):
        self.assertEqual(u.parse_v1_id("0"), 0)
        self.assertEqual(u.parse_v1_id("1"), 1)
        self.assertEqual(u.parse_v1_id("123"), 123)
        self.assertEqual(u.parse_v1_id("10000000"), 10000000)

        with self.assertRaises(ValueError):
            u.parse_v1_id("")

        with self.assertRaises(ValueError):
            u.parse_v1_id("-1")

        with self.assertRaises(ValueError):
            u.parse_v1_id("- 1")

        with self.assertRaises(ValueError):
            u.parse_v1_id("   ")

        with self.assertRaises(ValueError):
            u.parse_v1_id("\n")

        with self.assertRaises(ValueError):
            u.parse_v1_id("0x10")

        with self.assertRaises(ValueError):
            u.parse_v1_id("16h")

        with self.assertRaises(ValueError):
            u.parse_v1_id("abc")

        with self.assertRaises(ValueError):
            u.parse_v1_id("10A")

        with self.assertRaises(ValueError):
            u.parse_v1_id("A15")

    def test_parse_v2_id(self):
        self.assertTupleEqual(u.parse_v2_id("0.0"), (0, 0))
        self.assertTupleEqual(u.parse_v2_id("1.2"), (1, 2))
        self.assertTupleEqual(u.parse_v2_id("1000000.6000000"), (1000000, 6000000))

        with self.assertRaises(TypeError):
            # noinspection PyTypeChecker
            u.parse_v2_id(123.1)

        with self.assertRaises(ValueError):
            u.parse_v2_id("0")

        with self.assertRaises(ValueError):
            u.parse_v2_id("0.0.0")

        with self.assertRaises(ValueError):
            u.parse_v2_id(".1")

        with self.assertRaises(ValueError):
            u.parse_v2_id("1.")

        with self.assertRaises(ValueError):
            u.parse_v2_id("a.1")

        with self.assertRaises(ValueError):
            u.parse_v2_id("1.a")

        with self.assertRaises(ValueError):
            u.parse_v2_id("  0.0")

        with self.assertRaises(ValueError):
            u.parse_v2_id("0.0  ")

        with self.assertRaises(ValueError):
            u.parse_v2_id("0.0\n")

        with self.assertRaises(ValueError):
            u.parse_v2_id("")

        with self.assertRaises(ValueError):
            u.parse_v2_id("  ")

        with self.assertRaises(ValueError):
            u.parse_v2_id(".")

        with self.assertRaises(ValueError):
            u.parse_v2_id(" . ")

    def test_parse_v2_id_roundtrip(self):
        """
        The following tests may fail with disabled asserts. They are here to
        ensure that the ID roundtrips properly. Otherwise, you could refer
        to a lexeme with ID 0.0 using "00.00", or not, depending on the internal
        representation. We do not want to force a particular representation on
        implementers.
        """
        with self.assertRaises(AssertionError):
            u.parse_v2_id("00.1")

        with self.assertRaises(AssertionError):
            u.parse_v2_id("0.01")

    def test_range_overlap(self):
        # Trivial cases.
        self.assertTrue(u.range_overlaps((0, 1), (0, 1)))
        self.assertTrue(u.range_overlaps((0, 10), (0, 10)))

        # Not so trivial cases.
        self.assertTrue(u.range_overlaps((0, 10), (0, 1)))
        self.assertTrue(u.range_overlaps((0, 10), (-3, 1)))
        self.assertTrue(u.range_overlaps((0, 10), (3, 5)))
        self.assertTrue(u.range_overlaps((0, 10), (9, 10)))
        self.assertTrue(u.range_overlaps((0, 10), (9, 12)))

        # The same in reverse.
        self.assertTrue(u.range_overlaps((0, 1), (0, 10)))
        self.assertTrue(u.range_overlaps((-3, 1), (0, 10)))
        self.assertTrue(u.range_overlaps((3, 5), (0, 10)))
        self.assertTrue(u.range_overlaps((9, 10), (0, 10)))
        self.assertTrue(u.range_overlaps((9, 12), (0, 10)))

    def test_range_nonoverlap(self):
        self.assertFalse(u.range_overlaps((0, 10), (-3, -1)))
        self.assertFalse(u.range_overlaps((0, 10), (12, 50)))
        self.assertFalse(u.range_overlaps((0, 10), (-1, 0)))
        self.assertFalse(u.range_overlaps((0, 10), (10, 15)))

    def test_range_invalid(self):
        self.assertRaises(
            ValueError,
            u.range_overlaps,
            (0, 0),
            (1, 5)
        )

        self.assertRaises(
            ValueError,
            u.range_overlaps,
            (0, 5),
            (0, 0)
        )

        self.assertRaises(
            ValueError,
            u.range_overlaps,
            (3, 2),
            (1, 5)
        )

        self.assertRaises(
            ValueError,
            u.range_overlaps,
            (1, 5),
            (10, 7)
        )


if __name__ == '__main__':
    unittest.main()
