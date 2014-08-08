import itertools
import operator


def ilen(seq):
    """
    Return the number of items in an iterator or iterable.
    """
    if hasattr(seq, "__len__"):
        return len(seq)
    try:
        return max(i for i, _ in enumerate(seq)) + 1
    except ValueError:
        return 0

def window(seq, n=2):
    iters = [
        itertools.islice(i, n, None)
        for n, i in enumerate(itertools.tee(seq, n))
    ]
    return itertools.izip(*iters)


class EmptySequenceException(ValueError):
    pass

def average(seq, division_type=float):
    count = len(seq)
    if count == 0:
        raise EmptySequenceException("average() received empty seq")
    return reduce(operator.add, seq) / division_type(count)
