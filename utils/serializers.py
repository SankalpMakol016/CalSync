def serialize_datetimes(row, keys):
    """
    Converts any datetime/date/timestamp values in `row` (a dict-style
    DB result row) to ISO 8601 strings, in place, for the given keys.
    Mirrors the inline conversion previously duplicated in the
    events and invitations routes.
    """
    for key in keys:
        if row.get(key) and hasattr(row[key], "isoformat"):
            row[key] = row[key].isoformat()
