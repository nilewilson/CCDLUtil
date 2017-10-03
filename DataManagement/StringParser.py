"""
File for misc. string parsing functions
"""

def idempotent_append_newline(string):
    """
    Checks if there is a newline on the string.  If there is not, it appends one.

    Raises a type error if string is not a str object.
    :param string: String to append newline to.  Throws a type error if not a string.
    :return: String with a newline character at the end.
    """
    if type(string) is not str:
        raise TypeError
    if string.endswith('\n'):
        return string
    else:
        return string + '\n'