from libc.stdlib cimport calloc, free

cdef class FunctionHash:
    def __init__(self, int size):
        cdef FunctionHash_s* function_hash_s = <FunctionHash_s* >calloc(size, sizeof(FunctionHash_s))
        self.function_hash = function_hash_s
        self.size = size
        self.current_size = 0

    def __del__(self):
        free(self.function_hash)

    cdef FUNC get(self, char* item):
        return self._find_item(item)

    cdef int add_item(self, char* key, FUNC func):
        assert self.current_size + 1 <= self.size, "FunctionHash is at max capacity"
        cdef FunctionHash_s function_hash
        cdef int hashIndex = id(key) % self.size
        if self._find_item(key) == NULL:
            function_hash.key = hashIndex
            function_hash.func = func
            self.function_hash[self.current_size] = function_hash
            self.current_size += 1
            return 0
        return 1

    cdef FUNC _find_item(self, char* key):
        cdef int hashIndex = id(key) % self.size
        cdef int i
        for i in range(self.current_size):
            if self.function_hash[i].key == hashIndex:
                return self.function_hash[i].func
        return NULL
