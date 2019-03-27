from BioMetaDB.Serializers.fix_file cimport FixFile


cdef class IntegrityManager:
    cdef object config
    cdef char **tables
    cdef FixFile fix_file
    cdef _initial_project_check(self)
