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
