import os
from libc.stdio cimport fputs, fprintf
from BioMetaDB.Accessories.ops cimport to_cstring
from BioMetaDB.Accessories.ops cimport free_cstring
from BioMetaDB.Accessories.ops cimport count_characters

cdef extern from "stdio.h":
    FILE *fopen(const char *, const char *)
    int fclose(FILE *)
    size_t getline(char **, size_t *, FILE*)
    int fprintf  (FILE *stream, const char *template, ...)


cdef class FixFile:
    def __init__(self, char* file_name):
        """ FixFile writes and reads .fix files from project integrity checks

        :param file_name:
        """
        self.file_name = file_name
        self.fp = NULL

    def __del__(self):
        """ Clear memory when deleted, close any open file pointers

        :return:
        """
        fclose(self.fp)
        free_cstring(self.file_name)

    cdef initialize_file(self):
        """ Creates fix file using template in module

        :return:
        """
        cdef FILE* cfile
        cfile = fopen(self.file_name, "w")
        if cfile == NULL:
            raise FileNotFoundError(2, "No such file or directory: %s" % self.file_name)
        cdef str py_header_path = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                               "fix_header.txt")
        cdef char* fix_header_path = to_cstring(py_header_path)
        cdef FILE* fix_header_ptr = fopen(fix_header_path, "r")
        cdef char* line = NULL
        cdef ssize_t read
        cdef size_t l = 0
        fprintf(cfile, "@ %s\n@\n", self.file_name)
        while True:
            read = getline(&line, &l, fix_header_ptr)
            if read == -1:
                break
            fputs(line, cfile)
        self.fp = cfile

    cdef load_file(self):
        """ Loads file generated in INTEGRITY
        
        :return: 
        """
        cdef FILE* cfile
        cfile = fopen(self.file_name, "r")
        if cfile == NULL:
            raise FileNotFoundError(2, "No such file or directory: %s" % self.file_name)
        self.fp = cfile

    cdef char* read_issue(self):
        pass

    cdef write_issue(self, char* issue_id, char* data_type, char* issue_type, char* fix_type):
        """
        
        :param issue_id:
        :param data_type:
        :param issue_type: 
        :param fix_type: 
        :return: 
        """
        fprintf(self.fp, "ISSUE:\n%s:\t%s\n%s\t%s\n---\n", data_type, issue_id, issue_type, fix_type)
