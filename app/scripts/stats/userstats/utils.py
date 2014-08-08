

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
