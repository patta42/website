"""
Some useful functions
"""

def update_if_not_defined(dct, key, default):
    """
    performs dct.update({key : default}) if key not in dct or dct[key] is None
    """
    val = dct.get(key, None)
    if val is None:
        dct.update({key:default})

    return dct
