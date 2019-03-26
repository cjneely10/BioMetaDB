from cpython.ref cimport PyObject
from cpython.mem cimport PyMem_Malloc, PyMem_Realloc, PyMem_Free
from libc.stdlib cimport malloc, free


cdef class IntegrityManager:
    cdef object sess
    cdef object TableClass
    cdef object cfg

    def __init__(self):
        pass