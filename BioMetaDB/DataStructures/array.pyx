from libc.stdlib cimport malloc, free, realloc
from libc.string cimport strlen, strtok


cdef class Array:
    def __init__(self, int size, int buffer_size=1):
        """ Data Structure is sized-array with length component

        :param size:
        """
        self.array.values = <void **>malloc((size + buffer_size) * sizeof(void*))
        self.array.capacity = size + buffer_size
        self.buffer_size = buffer_size
        self.array.current_size = 0

    def __del__(self):
        free(self.array.values)

    cdef add(self, void* item):
        if self.array.current_size == self.array.capacity:
            self.array.values = <void** >realloc(self.array.values, (self.array.current_size + self.buffer_size) * sizeof(void*))
            self.array.capacity = self.current_size + self.buffer_size
        self.array.values[self.array.current_size] = item
        self.array.current_size += 1

    cdef void* get(self, int index):
        assert index < self.array.current_size, "Index exceeds current ArrayList capacity"
        return self.array.values[index]

    cdef set(self, int index, void* value):
        assert index < self.array.current_size, "Index exceeds current ArrayList capacity"
        self.array.values[index] = value

    @staticmethod
    cdef Array split(char* line, const char* delim):
        """ Split string based on location of delimiter
    
        :param line: (str)	Line to read
        :param delim: (str)	Break at char (non-inclusive)
        :return str:
        """
        cdef size_t line_len = strlen(line)
        cdef int num_locs_found = 0
        cdef int i
        for i in range(line_len):
            if line[i] == delim[0]:
                num_locs_found += 1
        cdef Array array = Array(num_locs_found + 1)
        cdef char* p = strtok(line, delim)
        array.add(<void *>p)
        for i in range(num_locs_found):
            p = strtok(NULL, delim)
            array.add(<void *>p)
        return array
