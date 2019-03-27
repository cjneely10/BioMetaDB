from itertools import chain, islice
from libc.stdlib cimport malloc, free

"""
Script holds functions for optimizing speed (e.g. chunking, splitting at line, etc)

"""
cdef extern from "Python.h":
    char* PyUnicode_AsUTF8(object unicode)


def chunk(iterable, int n):
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


def split_line_at(str line, str delim, bint return_delim=False):
    """ Return value before delimiter

    :param return_delim: (bool) Return the end of line with the delimiter
    :param line: (str)	Line to read
    :param delim: (str)	Break at char (non-inclusive)
    :return str:
    """
    cdef int char_count
    cdef str _c
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


def print_if_not_silent(bint silence_value, str output_text):
    """ Prints value to standard output if user-setting for "silent" is not set

    :param silence_value:
    :param output_text:
    :return:
    """
    if not silence_value:
        print(output_text)


cdef char** to_cstring_array(list list_str):
    """ Converts list of python strings to c array
    
    :param list_str: 
    :return: 
    """
    cdef char **ret = <char **>malloc(len(list_str) * sizeof(char *))
    cdef int i
    for i in range(len(list_str)):
        ret[i] = PyUnicode_AsUTF8(list_str[i])
    return ret


cdef free_cstring_array(char **cstring_array):
    """
    
    :param length: 
    :param cstring_array: 
    :return: 
    """
    free(cstring_array)


cdef char* to_cstring(str py_string):
    """
    
    :param py_string: 
    :return: 
    """
    cdef bytes py_bytes = py_string.encode()
    cdef char* c_string = py_bytes
    return c_string


cdef free_cstring(char* cstring):
    """
    
    :param cstring: 
    :return: 
    """
    free(cstring)


cdef str to_pystring(char* cstring):
    """
    
    :param cstring: 
    :return: 
    """
    cdef str s = ""
    cdef int length = sizeof(cstring) / sizeof(cstring[0])
    cdef int i
    for i in range(length):
        s += chr(cstring[i])
    return s

