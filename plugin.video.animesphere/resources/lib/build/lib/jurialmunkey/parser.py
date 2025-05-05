def try_int(value, fallback=0):
    """Mock implementation of try_int"""
    try:
        return int(value)
    except (ValueError, TypeError):
        return fallback
