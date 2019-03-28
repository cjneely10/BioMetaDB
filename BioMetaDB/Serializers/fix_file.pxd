from libc.stdio cimport FILE

cdef extern from "stdio.h":
    FILE *fopen(const char *, const char *)


cdef class FixFile:
    cdef char* file_name
    cdef FILE* fp
    cdef initialize_file(self)
    cdef load_file(self)
    cdef write_issue(self, char* issue_id, char* data_type, char* issue_type, char* fix_type)
    cdef char* read_issue(self)
