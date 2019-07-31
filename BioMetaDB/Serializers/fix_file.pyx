# cython: language_level=3
import os

cdef extern from "stdio.h":
    FILE *fopen(const char *, const char *)
    int fclose(FILE *)
    size_t getline(char **, size_t *, FILE*)
    int fprintf  (FILE *stream, const char *template, ...)


cdef class FixFile:
    def __init__(self, object file_name):
        """ FixFile writes and reads .fix files from project integrity checks

        :param file_name:
        """
        self.file_name = file_name
        self.fp = None
        self.issues = []
        self.num_issues = 0

    cdef initialize_file(self):
        """ Creates fix file using template in module

        :return:
        """
        cdef object cfile = open(self.file_name, "w")
        if cfile is None:
            raise FileNotFoundError(2, "No such file or directory: %s" % self.file_name)
        cdef str py_header_path = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                               "fix_header.txt")
        cdef object fix_header_ptr = open(py_header_path, "rb")
        for line in fix_header_ptr:
            cfile.write(line.decode())
        self.fp = cfile
        fix_header_ptr.close()

    cdef load_file(self):
        """ Loads file generated in INTEGRITY
        
        :return: 
        """
        cdef object cfile = open(self.file_name, "r")
        if cfile is None:
            raise FileNotFoundError(2, "No such file or directory: %s" % self.file_name)
        self.fp = cfile

    cdef read_issue(self):
        cdef object line
        cdef str data_type, issue_type, fix_type, fix_data = "NONE", location = "NONE", parsed_issue
        for line in self.fp:
            while line.startswith("@"):
                line = next(self.fp)
            line = line.rstrip("\r\n")
            if line == "ISSUE:":
                line = next(self.fp)
                self.num_issues += 1
                line = line.rstrip("\r\n").split(":")
                data_type = line[0]
                _id = line[1].lstrip("\t")
                if len(line) == 3:
                    location = line[2].lstrip("\t")
                line = next(self.fp)
                line = line.rstrip("\r\n").split("\t")
                issue_type = line[0]
                fix_type = line[1]
                if len(line) == 3:
                    fix_data = line[2]
                parsed_issue = "%s|%s|%s" % (data_type, issue_type, fix_type)
                self.issues.append((_id, location, parsed_issue, fix_data,))


    def write_issue_with_location(self, str issue_id, str data_type, str issue_type, str fix_type, str location):
        """
        
        :param location: 
        :param issue_id:
        :param data_type:
        :param issue_type: 
        :param fix_type: 
        :return: 
        """
        self.fp.write("ISSUE:\n%s:\t%s:\t%s\n%s\t%s\n---\n" % (data_type, issue_id, location, issue_type, fix_type))


    def write_issue(self, str issue_id, str data_type, str issue_type, str fix_type):
        """
        
        :param issue_id:
        :param data_type:
        :param issue_type: 
        :param fix_type: 
        :return: 
        """
        self.fp.write("ISSUE:\n%s:\t%s\n%s\t%s\n---\n" % (data_type, issue_id, issue_type, fix_type))

