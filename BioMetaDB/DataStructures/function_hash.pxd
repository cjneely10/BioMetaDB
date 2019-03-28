ctypedef int (*FUNC)(char*, void*, void*)


ctypedef struct FunctionHash_s:
    int key
    FUNC func


cdef class FunctionHash:
    cdef FunctionHash_s* function_hash
    cdef int size
    cdef int current_size
    cdef int add_item(self, char* key, FUNC func)
    cdef FUNC _find_item(self, char* key)
    cdef FUNC get(self, char* item)
