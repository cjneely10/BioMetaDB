from libc.stdio cimport FILE

cdef extern from "stdio.h":
    FILE *fopen(const char *, const char *)


cdef class FixFile:
    cdef initialize_file(self)
    cdef load_file(self)
    cdef read_issue(self)
    cdef object file_name
    cdef object fp
    cdef list issues
    cdef int num_issues
