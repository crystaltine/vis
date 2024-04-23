def validate_fields(data, name_type):
    for name, type_ in name_type.items():
        if name not in data:
            return False
        if not isinstance(data[name], type_):
            return False
    return True