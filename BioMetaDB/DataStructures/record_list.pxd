cdef class RecordList:
    cdef object sess
    cdef object TableClass
    cdef object cfg
    cdef dict _summary
    cdef int num_records
    cdef list results
    cdef bint has_text
