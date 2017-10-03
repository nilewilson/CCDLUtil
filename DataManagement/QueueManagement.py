"""
For the use of multithreading and multiprocessing queues.

See https://docs.python.org/3/library/queue.html for Queue api.

"""

import Queue
import multiprocessing

def clear_queue(q):
    """Clears a queue in a thread-safe manner"""
    with q.mutex:
        q.queue.clear()

def clear_mutiprocess_queue(q):
    """ clears a mutliprocess queue"""
    while not q.empty():
        q.get()

def get_queue_dict(all_queues, thread=True):
    """
    Gets a queue dictionary with keys equal to all queues names in ALL_QUEUES
    :param all_queues: A list of queue names (strings).  These will be the keys of the returned dict.
    :param thread: If True, this will be using the Queue.Queue() class, else the multiprocessing queue will
                    be used.
    :return: Returns a queue dictionary of the the form:
     queue_dict['queue name'] -> Python Queue
    """
    queue_dict = dict()
    for q in all_queues:
        if thread:
            queue_dict[q] = Queue.Queue()
        else:
            queue_dict[q] = multiprocessing.Queue()
    return queue_dict
