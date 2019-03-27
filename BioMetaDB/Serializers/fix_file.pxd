from libc.stdio cimport FILE

cdef extern from "stdio.h":
    FILE *fopen(const char *, const char *)

ctypedef int (*FIX)(char*)


ctypedef struct Issue_s:
    char* data_type
    char* issue_type
    FIX fix_type

cdef class Issue:
    cdef Issue_s issue


cdef class FixFile:
    cdef char* file_name
    cdef FILE* fp
    cdef write_issue(self, str data_type, str issue_type, str fix_type)
    cdef _initialize_file(self)
