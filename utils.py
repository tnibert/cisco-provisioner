import re
from functools import reduce

format_octet_binary = lambda n: '{0:08b}'.format(n)
strip_blank_lines = lambda s: re.sub(r'^$\n', '', s, flags=re.MULTILINE)

def partition(p, l):
    """
    :param p: predicate
    :param l: the iterable
    Partitions an iterable based on a predicate.
    See https://stackoverflow.com/a/4579086
    """
    return reduce(lambda x, y: x[not p(y)].append(y) or x, l, ([], []))
