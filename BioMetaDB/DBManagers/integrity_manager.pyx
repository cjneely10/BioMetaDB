from BioMetaDB.Accessories.ops cimport to_cstring_array
from BioMetaDB.Accessories.ops cimport free_cstring_array
from BioMetaDB.Serializers.fix_file cimport FixFile
from random import randint
from datetime import datetime


cdef class IntegrityManager:
    def __init__(self, object config, list tables=["ALL",]):
        self.tables = to_cstring_array(tables)
        self.config = config
        cdef str py_fixfile_name = "{}.{}.{}.fix".format(datetime.today().strftime("%Y%m%d"),
                                                str(randint(1,1001)), "_".join(tables))
        self.fix_file = FixFile(py_fixfile_name)
        self._initial_project_check()

    def __del__(self):
        """ Free all allocated memory

        :return:
        """
        free_cstring_array(self.tables)

    cdef _initial_project_check(self):
        pass
