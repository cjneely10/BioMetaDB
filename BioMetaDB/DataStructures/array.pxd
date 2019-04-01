ctypedef struct Array_s:
    void **values
    int capacity
    int current_size


cdef class Array:
    cdef Array_s array
    cdef add(self, void* item)
    cdef void* get(self, int index)
    cdef set(self, int index, void* value)
    cdef int buffer_size
    @staticmethod
    cdef Array split(char* line, const char* delim)
    cdef int current_size
