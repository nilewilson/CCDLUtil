"""
Wrapper methods for assertions.
"""


def assert_equal(*args):
    """
    Runs assertion that everything is equal to each other and display values if assertion fails.
    """
    assert len(args) >= 2, 'Error: there should be at least two parameters!'
    for i in args:
        assert i == args[0], 'Error: %s and %s should be EQUAL!' % (str(i), str(args[0]))


def assert_not_equal(*args):
    """
    Runs assertion that everything is NOT equal to each other and display values if assertion fails.

    Warning: O(n^2) operation!
    """
    assert len(args) >= 2, 'Error: there should be at least two parameters!'
    for i in range(len(args)):
        for j in range (i + 1, len(args)):
            assert args[i] != args[j], 'Error: %s and %s should NOT be equal!' % (str(args[i]), str(args[j]))


def assert_less(*args):
    """
    Run assertion that everything is STRICTLY sorted from small to large and display values if assert fails
    """
    assert len(args) >= 2, 'Error: there should be at least two parameters!'
    for i in range(len(args) - 1):
        assert args[i] < args[i + 1], 'Error: %s should be less than %s!' % (str(args[i]), str(args[i + 1]))


def assert_less_or_equal(*args):
    """
    Run assertion that everything is sorted from small to large and display values if assert fails
    """
    assert len(args) >= 2, 'Error: there should be at least two parameters!'
    for i in range(len(args) - 1):
        assert args[i] <= args[i + 1], 'Error: %s should be less than or equal to %s' % (str(args[i]), str(args[i + 1]))


def assert_greater(*args):
    """
    Run assertion that everything is STRICTLY sorted from large to small and display values if assert fails
    """
    assert len(args) >= 2, 'Error: there should be at least two parameters!'
    for i in range(len(args) - 1):
        assert args[i] > args[i + 1], 'Error: %s should be greater than %s!' % (str(args[i]), str(args[i + 1]))


def assert_greater_or_equal(*args):
    """
    Run assertion that everything is sorted from large to small and display values if assert fails
    """
    assert len(args) >= 2, 'Error: there should be at least two parameters!'
    for i in range(len(args) - 1):
        assert args[i] >= args[i + 1], 'Error: %s should be greater than or equal to %s' % \
                                       (str(args[i]), str(args[i + 1]))


def assert_epoch_label_shape(epoched_values, labels,
                             message="The number of epochs between the density and labels don't match"):
    """
    Asserts that the number of epochs in the density has the same length as the labels
    :param epoched_values: epoched values where the first dimension is the number of epoch (such as density)
    :param labels: labels - list or 1D np array
    :param message: Message to show if assertion fails.
    """
    assert epoched_values.shape[0] == len(labels), str(message) + '-- Density: %d, Labels: %d' % \
                                                                  (epoched_values.shape[0], len(labels))


def assert_none(*args):
    """
    Runs assertion that all are None and display value if assertion fails.
    """
    for i in args:
        assert i is None, 'Error: %s is not None' % str(i)


def assert_type(dtype, *args):
    """
    Run assertion that all are type dtype and display value if assertion fails
    :param dtype: data type
    """
    for i in args:
        assert type(i) is dtype, 'Error: %s has type: %s' % (str(i), type(i))
