"""
Just a little series of helper functions

"""


def chunker(seq, size):
    """
    Splits a list in seq un into chunks of size
    """
    return (seq[pos : pos + size] for pos in range(0, len(seq), size))
