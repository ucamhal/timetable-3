from functools import partial
from itertools import chain
from operator import getitem

def int_safe(string, base=10, default=None):
    """Parse string as an int, returning default on failure."""
    try:
        return int(string, base)
    except (TypeError, ValueError):
        return default

def to_digits(integer, base=10):
    "Gets the digits of an integer in base n."
    assert base > 1, "Bases < 2 are not supported."
    is_negative = abs(integer) != integer
    integer = abs(integer)
    digits = []
    while True:
        digits.insert(0, integer % base)
        integer /= base
        if integer == 0:
            break
    return (digits, is_negative)

def from_digits((digits, is_negative), base=10):
    "Creates an integer from a list of digits in base n."
    value = 0
    for n, digit in enumerate(reversed(digits)):
        value += digit * (base ** n)

    return value * (-1 if is_negative else 1)

def build_codec(encoded_digits):
    """Given a list of encoded digit representations, builds encoder and 
    decoder functions for to_string and from_string
    
    The encoder when called with an integer digit returns the encoded character 
    form. The decoder when called with an encoded character yields the decoded
    integer digit.
    
    Returns: A tuple of (encoder_func, decoder_func).
    """
    reverse_lookup = dict((ed, n) for n, ed in enumerate(encoded_digits))
    return (partial(getitem, encoded_digits),
            partial(getitem, reverse_lookup))

_LOOKUP_TABLE = [chr(x) for x in chain(
        xrange(ord("0"), ord("9") + 1),
        xrange(ord("A"), ord("Z") + 1))]

default_encoder, default_decoder = build_codec(_LOOKUP_TABLE)

def to_string(integer, base=10, digit_encoder=default_encoder):
    """Encodes an integer (as a string) in base n.
    
    Args:
        integer: The int to encode
        base: the base to represent the integer in. Must be >= 2
        digit_encoder: A function of int -> str which encodes a digit into a
            string. The default function supports bases up to 36, and uses the
            chars 0..9 A..Z to represent digits.
    """
    digits, is_negative = to_digits(integer, base)
    return "%s%s" % ("-" if is_negative else "",
            "".join(map(digit_encoder, digits)))

def from_string(value, base=10, digit_decoder=default_decoder):
    if value.startswith("-"):
        is_negative = True
        value = value[1:]
    else:
        is_negative = False

    return from_digits((map(digit_decoder, value), is_negative), base)

def hash_ints(integers, m=2 ** 64, a=6364136223846793005,
        c=1442695040888963407, initial=1):
    # LCG PRNG with Knuth's constants mixing in the char code on each 
    # iteration
    x = initial
    for integer in integers:
        x = ((a * x * integer) + c) % m
    return x
