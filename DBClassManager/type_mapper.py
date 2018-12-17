from sqlalchemy import Float, Integer, String, VARCHAR


"""
Script holds dictionaries to map types to each other and to string representations

"""


class TypeMapper:
    py_type_to_string = {
        float:      "Float",
        int:        "Integer",
        str:        "String",
    }
    sql_type_to_string = {
        Float:      "Float",
        Integer:    "Integer",
        String:     "String",
    }
    string_to_sql_type = {
        "Float": Float,
        "Integer": Integer,
        "String": String,
    }
    string_to_loaded_sql_type = {
        "Float": Float,
        "Integer": Integer,
        "String": VARCHAR,
    }
    string_to_py_type = {
        "Float": float,
        "Integer": int,
        "String": str,
    }
    py_type_to_sql_type = {
        float:      Float,
        int:        Integer,
        str:        String
    }
    sql_type_to_py_type = {
        Float:      float,
        Integer:    int,
        String:     str,
    }
