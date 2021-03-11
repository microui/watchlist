from uuid import uuid4


def get_id():
    return str(uuid4())


def column_name_list(cls):
    column_collection_str_list = cls.__table__.__dict__['columns'].__str__().split("'")
    column_list = []
    for a in range(0, len(column_collection_str_list)):
        if a % 2 != 0:
            column_list.append(column_collection_str_list[a].split('.')[1])
    return column_list








