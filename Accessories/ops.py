from itertools import chain, islice

"""
Script holds functions for optimizing speed (e.g. chunking, splitting at line, etc)

"""
# TODO: Optimize with cython calls


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
    char_count = 0
    for _c in line:
        if _c != delim:
            char_count += 1
        else:
            break
    return line[:char_count]


def split_line_at(line, delim, return_delim=False):
    """ Return value before delimiter

    :param return_delim: (bool) Return the end of line with the delimiter
    :param line: (str)	Line to read
    :param delim: (str)	Break at char (non-inclusive)
    :return str:
    """
    char_count = 0
    for _c in line:
        if _c != delim:
            char_count += 1
        else:
            break
    if return_delim:
        return line[:char_count], line[char_count:]
    else:
        return line[:char_count], line[char_count + 1:]


def touch(path):
    """ Create file (mimics touch in unix)

    :param path: (str)  Location to create file
    :return:
    """
    open(path, 'a').close()
