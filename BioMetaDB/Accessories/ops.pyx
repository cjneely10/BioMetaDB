from itertools import chain, islice
from libc.stdlib cimport malloc, free
from libc.string cimport strcmp, strlen

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


def read_until(str line, str delim):
    """ Return value before delimiter

    :param line: (str)	Line to read
    :param delim: (str)	Break at char (non-inclusive)
    :return str:
    """
    cdef int char_count = 0
    cdef str _c
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
    """ Frees array of character arrays
    
    :param cstring_array: 
    :return: 
    """
    free(cstring_array)


cdef str to_pystring(char* cstring):
    cdef str to_return = ""
    cdef size_t cstring_length = strlen(cstring)
    cdef size_t i
    for i in range(cstring_length):
        to_return += chr(cstring[i])
    return to_return


cdef char* to_cstring(str py_string):
    """ Converts str to char*
    
    :param py_string: 
    :return: 
    """
    cdef bytes py_bytes = py_string.encode()
    cdef char* c_string = py_bytes
    return c_string


cdef free_cstring(char* cstring):
    """ Frees memory from char array
    
    :param cstring: 
    :return: 
    """
    free(cstring)


cdef int count_characters(char* cstring, const char* search_val):
    """ Counts number of occurrences of search_val
    
    :param cstring: 
    :param search_val: 
    :return: 
    """
    cdef int count = 0
    cdef size_t cstring_size = strlen(cstring)
    cdef size_t i
    for i in range(cstring_size):
        if cstring[i] == search_val[0]:
            count += 1
    return count


cdef int stringarray_contains(char** list_of_strings, char* string_to_find):
    cdef size_t list_length = sizeof(list_of_strings) / sizeof(list_of_strings[0])
    cdef size_t i
    for i in range(list_length):
        if strcmp(list_of_strings[i], string_to_find) == 0:
            return 0
    return 1
