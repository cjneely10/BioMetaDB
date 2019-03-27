from libc.stdio cimport FILE
from BioMetaDB.Accessories.ops cimport to_cstring
from BioMetaDB.Accessories.ops cimport free_cstring
from libc.stdlib cimport malloc, free

cdef extern from "stdio.h":
    FILE *fopen(const char *, const char *)
    int fclose(FILE *)
    size_t getline(char **, size_t *, FILE*)


cdef class Issue:
    def __init__(self, char* data_type, char* issue_type, char* fix_type):
        cdef Issue_s issue
        issue.data_type = <char *>malloc(sizeof(data_type) / sizeof(data_type[0]))
        issue.issue_type = <char *>malloc(sizeof(issue_type) / sizeof(issue_type[0]))
        issue.data_type = data_type
        issue.issue_type = issue_type
        self.issue = issue

    def __del__(self):
        free(self.issue.data_type)
        free(self.issue.issue_type)


cdef class FixFile:
    def __init__(self, str file_name):
        """ FixFile writes and reads .fix files from project integrity checks

        :param file_name:
        """
        self.file_name = to_cstring(file_name)
        self.fp = NULL
        self._initialize_file()

    def __del__(self):
        """ Clear memory when deleted

        :return:
        """
        free_cstring(self.file_name)

    cdef _initialize_file(self):
        """ Creates file

        :return:
        """
        cdef FILE* cfile
        cfile = fopen(self.file_name, "w")
        if cfile == NULL:
            raise FileNotFoundError(2, "No such file or directory: %s" % self.file_name)
        self.fp = cfile

    cdef write_issue(self, str data_type, str issue_type, str fix_type):
        cdef Issue issue = Issue(to_cstring(data_type), to_cstring(issue_type), to_cstring(fix_type))
