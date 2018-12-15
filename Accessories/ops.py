from itertools import chain, islice


def chunk(iterable, n):
    """ For parsing very large files

	:param iterable: (iter)	File iterable
	"""
    iterable = iter(iterable)
    while True:
        yield chain([next(iterable)], islice(iterable, n - 1))


def read_until(line, ch):
    """

	:param line: (str)	Line to read
	:param ch: (str)	Break at char (non-inclusive)
	:return str:
	"""
    # Read in id
    _id = ""
    for ch in line:
        if ch != "\t":
            _id += ch
        else:
            break
    return _id
