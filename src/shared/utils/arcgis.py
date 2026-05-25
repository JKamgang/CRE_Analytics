from src.shared.utils.security import sanitize_query_param

def build_where_clause(**kwargs) -> str:
    """Builds a sanitized WHERE clause for ArcGIS queries."""
    where_clauses = ["1=1"]

    if "state" in kwargs and kwargs["state"]:
        where_clauses.append(f"STATE = '{sanitize_query_param(kwargs['state'])}'")
    if "county" in kwargs and kwargs["county"]:
        where_clauses.append(f"COUNTY LIKE '%{sanitize_query_param(kwargs['county'])}%'")
    if "zip_code" in kwargs and kwargs["zip_code"]:
        where_clauses.append(f"ZIPCODE = '{sanitize_query_param(kwargs['zip_code'])}'")
    if "street" in kwargs and kwargs["street"]:
        where_clauses.append(f"ADDRESS LIKE '%{sanitize_query_param(kwargs['street'])}%'")

    return " AND ".join(where_clauses)
