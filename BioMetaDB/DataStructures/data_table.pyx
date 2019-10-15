cdef class DataTable:
    def __init__(self, object header=None):
        if header is not None:
            self.header = set(header)
        else:
            pass

