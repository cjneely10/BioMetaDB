from itertools import chain, islice


def chunk(iterable, n):
    """ For parsing very large files

    :param n: (int) Chunk size
    :param iterable: (iter)	File iterable
    """
    iterable = iter(iterable)
    while True:
        yield chain([next(iterable)], islice(iterable, n - 1))


def read_until(line, delim):
    """ Return value before delimiter

    :param line: (str)	Line to read
    :param delim: (str)	Break at char (non-inclusive)
    :return str:
    """
    # Read in id
    _id = ""
    for _c in line:
        if _c != delim:
            _id += _c
        else:
            break
    return _id


def touch(path):
    """ Create file (mimics touch in unix)

    :param path: (str)  Location to create file
    :return:
    """
    open(path, 'a').close()
