"""
This file is for List and 1D np array Manipulations.

For matrix manipulation and dict manipulation, see DataParser.py.
"""

import numpy as np
import CCDLUtil.Utility.AssertVal as AV


def extract_min_difference_in_list(lst):
    """
    Takes a list and extracts the minimum difference between consecutive items.
    For example
        [3, 5, 125, 23543]
    Would return 2
    :param lst: List of numbers to be examined. List must be in nonmonitonic ascending order
    """
    min_val = float('inf')
    for index in xrange(len(lst) - 1):
        diff = lst[index + 1] - lst[index]
        min_val = min(diff, min_val)
    return min_val

def extract_min_difference_between_lists(lst_large, lst_small):
    """
    Takes a list and extracts the minimum difference between two lists.
    For example
        [3, 5, 125, 23543]
        [1, 4, 120, 2354]
    Would return 1
    """
    AV.assert_equal(len(lst_large), len(lst_small))
    return min([a_i - b_i for a_i, b_i in zip(lst_large, lst_small)])

def convert_ununiform_start_stop_lists_to_uniform_start_stop_lists(start_lst, stop_lst):
    """
    Takes a list of start indexes and a list of end indexes a returns a new end index list such that trial_dur = stop_lst[i] - start_lst[i] and trial dur is the same for
    each list (set to the minimum trial dur contained in the list)
    :param start_lst: list of floats denoting starts of trials
    :param stop_lst: list of floats denoting end of trials
    :return: new stop list
    """
    AV.assert_equal(len(start_lst), len(stop_lst))
    dur = extract_min_difference_between_lists(stop_lst, start_lst)
    return [start_lst_val + dur for start_lst_val in start_lst]

def stack_lists(existing, new_list):
    """
    Takes existing epoch list and concats a new list to the end.
    If existing is none, returns new list.
    """
    return new_list if existing is None else existing + new_list


def convert_to_binary_labels_by_median(continous_labels):
    """
    Converts continuous labels to binary

    Example: labels -> [1, 4, 5, 2]
             convert_to_binary_labels(labels) -> [0, 1, 1, 0]

    :return: "Binaryerized" labels (list of length num_labels)
    """
    # get the middle of the list
    median = np.median(continous_labels)

    # if above the middle, 1 else 0
    binary_labels = np.asarray([1 if x > median else 0 for x in continous_labels])
    return binary_labels


def convert_to_binary_labels_by_value(continous_labels, eq_is_lower_value):
    """
    Converts continuous labels to binary

    Example: labels -> [1, 4, 5, 2]
             convert_to_binary_labels(labels) -> [0, 1, 1, 0]

    :return: "Binaryerized" labels (list of length num_labels)
    """

    # if above the middle, 1 else 0
    binary_labels = np.asarray([1 if x > eq_is_lower_value else 0 for x in continous_labels])
    return binary_labels


def amalgamate_predictions(list_of_predictions):
    """
    Takes a list of predictions (list of lists) and returns a new prediction (list) based on a majority
    rules paradigm.  Ties go to the first list.

    :param list_of_predictions: An odd length list of predictions, where predictions are a list.  All
           predictions must be of the same size
    :return: A list where each prediction represents the highest voted prediction - lenght is the number of original
             predictions
    """
    assert len(list_of_predictions) % 2 == 1

    num_predictions = len(list_of_predictions[0])
    # Assert that all prediction lists are of the same length and have the same element types
    compare = set(list_of_predictions[0])
    for lst in list_of_predictions:
        assert len(lst) == num_predictions
        assert all(ii == 1 or ii == 0 for ii in lst)

    # zip up or predictions list for easy access
    preds = zip(*list_of_predictions)

    # Assert that we didn't change the length of the list
    assert len(preds) == num_predictions

    # Keep track of our new predictions
    new_predictions = []
    for pred in preds:
        most_common = max(set(pred), key=pred.count)
        new_predictions.append(most_common)

    # Ensure that our new list contains the same number of predictions
    assert len(new_predictions) == num_predictions

    # return our new predictions list - length is number of predictions
    return new_predictions


def filter_true_false_none(arr, none_is_true):
    """
    Takes an array with the values {True, False, None} and converts it to an array of {True, False}

    Value error raised if invalid list is passed
    :param arr: array lik - 1D list or np array with shape (len,)  (modified)
    :param none_is_true: If True, convert all Nones to True
    :return: list with all None type converted to True or False (modifies arr)
    """
    possibles = {True, False, None}
    for i, x in enumerate(arr):
        # check to make sure our list is in valid form
        if x not in possibles:
            raise ValueError('List contains invalid values')
        # switch our None entry if needed.
        if x is None:
            arr[i] = none_is_true
    return arr


def filter_list_by_label(lst, labels):
    positive_list = [i for (i, v) in zip(lst, labels) if v == 1]
    negative_list = [i for (i, v) in zip(lst, labels) if v == 0]
    return positive_list, negative_list

