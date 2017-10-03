"""
This file contains decorators for use in various contexts

:param is_daemon: set to True to create a daemon thread
"""

import threading


# calls the given function (fn) in a new thread
def threaded(is_daemon):
    def out_wrapper(fn):
        def wrapper(*args, **kwargs):
            t = threading.Thread(target=fn, args=args, kwargs=kwargs)
            t.daemon = is_daemon
            t.start()
        return wrapper
    return out_wrapper
