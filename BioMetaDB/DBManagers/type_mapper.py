import operator
import random
from sqlalchemy import Float, Integer, String, VARCHAR, Boolean

from BioMetaDB.Serializers.count_table import CountTable

"""
Class holds dictionaries to map types to each other and to string representations

"""


class TypeMapper:
    py_type_to_string = {
        float:      "Float",
        int:        "Integer",
        str:        "String",
        bool:       "Boolean",
    }
    sql_type_to_string = {
        Float:      "Float",
        Integer:    "Integer",
        String:     "String",
        Boolean:    "Boolean",
    }
    string_to_sql_type = {
        "Float": Float,
        "Integer": Integer,
        "String": String,
        "Boolean": Boolean,
    }
    string_to_loaded_sql_type = {
        "Float": Float,
        "Integer": Integer,
        "String": VARCHAR,
        "Boolean": Boolean,
    }
    string_to_py_type = {
        "Float": float,
        "Integer": int,
        "String": str,
        "Boolean": bool,
    }
    py_type_to_sql_type = {
        float:      Float,
        int:        Integer,
        str:        String,
        bool:       Boolean,
    }
    sql_type_to_py_type = {
        Float:      float,
        Integer:    int,
        String:     str,
        Boolean:    bool,
    }
    py_bool_to_sql_bool = {
        "True": "TRUE",
        "False": "FALSE",
    }

    @staticmethod
    def get_translated_types(counttable_object, dict_to_reference):
        if dict_to_reference == TypeMapper.py_type_to_string:
            return {
                counttable_object.header[i]:
                    dict_to_reference[TypeMapper.determine_column_type(counttable_object, i)]
                for i in range(len(counttable_object.header))
            }
        return {
            counttable_object.header[i]:
                dict_to_reference[
                    type(counttable_object.get_at(random.sample(counttable_object.file_contents.keys(), 1)[0], i))
                ]
            for i in range(len(counttable_object.header))
        }

    @staticmethod
    def determine_column_type(counttable_object, column_idx):
        values = {
            int: 0,
            bool: 0,
            float: 0,
            str: 0,
            # None: 0
        }
        for value_list in counttable_object.file_contents.values():
            if value_list[column_idx] != 'None':
                values[
                    CountTable._try_return_type(value_list[column_idx])
                ] += 1
        return (max(values.items(), key=lambda x: x[1]) if values.items() else (str,))[0]
