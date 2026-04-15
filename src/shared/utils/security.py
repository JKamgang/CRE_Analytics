def sanitize_query_param(val):
    if val is None:
        return ""
    return str(val).replace("'", "''")
