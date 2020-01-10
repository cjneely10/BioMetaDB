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
        cfile.write("""@ All header lines are statically generated and are preceded by '@'
            @
            @   This file was created by using `dbdm INTEGRITY`
            @   .fix file structure identifies issues in your project and displays them as:
            @
            @       ISSUE
            @       <DATA_TYPE>:    <ID>
            @       <ISSUE_TYPE>  <FIX_TYPE>
            @       ---
            @   Note that all .fix files are tab delimited
            @
            @
            @ Depending on the issues identified, your .fix file may contain the following:
            @
            @       PROJECT:    <PROJECT_NAME>
            @       INVALID_PATH    NONE
            @
            @
            @       RECORD:    <RECORD_ID>:  <TABLE_NAME>
            @       BAD_TYPE    NONE
            @
            @       RECORD:    <RECORD_ID>:  <TABLE_NAME>
            @       BAD_LOCATION    DELETE
            @
            @
            @       FILE:    <FILE_ID>:  <TABLE_NAME>
            @       BAD_RECORD    NONE
            @
            @       Each issue is defined as:
            @
            @       PROJECT INVALID_PATH:   working_dir path stored in config file is invalid
            @       RECORD  BAD_TYPE:       data type for record could not be determined
            @       RECORD  BAD_LOCATION:       stored file path for record does not exist
            @       FILE    BAD_RECORD:     file exists in project directory with no assigned database id
            @
            @   For each issue, default actions are presented. The following fixes are available:
            @
            @       PROJECT:    <PROJECT_NAME>
            @       INVALID_PATH    PATH    /path/to/project_directory
            @
            @
            @       RECORD:    <RECORD_ID>: <TABLE_NAME>
            @       BAD_TYPE    SET     data_type(e.g. fasta/fastq)
            @
            @       RECORD:    <RECORD_ID>: <TABLE_NAME>
            @       BAD_LOCATION    FILE    /path/to/data_file.fna
            @
            @
            @       FILE:    <FILE_ID>: <TABLE_NAME>
            @       BAD_RECORD    RECORD    record_id_in_database
            @
            @   If you do not wish to fix a particular issue, simple delete the entire entry,
            @   starting from "ISSUE" until "---"
            @
            @   Do NOT add additional characters, newline or otherwise
            @
            """)
        # for line in fix_header_ptr:
        #     cfile.write(line.decode())
        self.fp = cfile
        # fix_header_ptr.close()

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

