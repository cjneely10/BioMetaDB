from BioMetaDB.Serializers.fix_file cimport FixFile

ctypedef int (*FUNC)(char*, void*, void*, char*)

cdef class IntegrityManager:
    cdef object config
    cdef FixFile fix_file
    cdef char** tables
    cdef dict _create_function_hash(self)
    cdef dict function_hash
    cdef public int issues_found


# cdef int record_bad_file_delete(char* arg, void* sess, void* UserClass, char* fix_data)
# cdef int record_bad_file_file(char* arg, void* sess, void* UserClass, char* fix_data)
# cdef int file_bad_record_delete(char* arg, void* sess, void* UserClass, char* fix_data)
# cdef int file_bad_record_record(char* arg, void* sess, void* UserClass, char* fix_data)
# cdef int record_bad_type_none(char* arg, void* sess, void* UserClass, char* fix_data)
# cdef int record_bad_type_set(char* arg, void* sess, void* UserClass, char* fix_data)
# cdef int table_bad_table_delete(char* arg, void* sess, void* UserClass, char* fix_data)
# cdef int table_bad_table_tsv(char* arg, void* sess, void* UserClass, char* fix_data)
# cdef int table_bad_table_mgt(char* arg, void* sess, void* UserClass, char* fix_data)
# cdef int project_invalid_path_none(char* arg, void* sess, void* UserClass, char* fix_data)
# cdef int project_invalid_path_path(char* arg, void* sess, void* UserClass, char* fix_data)
