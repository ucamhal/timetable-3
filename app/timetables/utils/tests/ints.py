from django.test import TestCase

from timetables.utils import ints
import random

class IntegerBaseConversionTest(TestCase):

    def test_base_10(self):
        self.assertEqual(([1, 0], False), ints.to_digits(10, base=10))
        self.assertEqual(([1], False), ints.to_digits(1, base=10))
        self.assertEqual(([9, 9, 3], False), ints.to_digits(993, base=10))
        self.assertEqual(([2, 7, 3, 8], True), ints.to_digits(-2738, base=10))

    def test_encode(self):
        # Encode some random values in bases 2 to 26 and check that the encoded
        # representations decode to the input value (using Python's int() 
        # function).
        bases = range(2, 37)
        values = [random.randint(-1000000, 1000000) for _ in range(200)]
        for base in bases:
            for value in values:
                encoded = ints.to_string(value, base)
                self.assertEqual(int(encoded, base), value,
                        "%d in base %d encoded as: %s" % (value, base, encoded))

    def test_decode(self):
        # Encode some random values in bases 2 to 26 and check that the encoded
        # representations decode to the input value (using our from_string() 
        # function.
        bases = range(2, 37)
        values = [random.randint(-1000000, 1000000) for _ in range(200)]
        for base in bases:
            for value in values:
                encoded = ints.to_string(value, base)
                decoded = ints.from_string(encoded, base)
                self.assertEqual(decoded, value,
                        "%d in base %d encoded as: %s, decoded as: %s" % (
                                value, base, encoded, decoded))

    def test_from_digits(self):
        self.assertEqual(10, ints.from_digits(([1, 0], False)))
