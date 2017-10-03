"""
This file is for generic operations related to matrix and dictionary manipulations.
"""

import numpy as np
import CCDLUtil.Utility.AssertVal as AV
import CCDLUtil.DataManagement.ArrayParser as CCDLArrayParser
import time
import bisect
import ast

def epoch_data(eeg_indexes, raw_data, trial_starts, trial_stops, trim=False):
    """
    Takes raw data of shape [sample, channel] and returns epoched data of shape [epoch, sample channel].
    The epoches are taken according to the indexing of the start and stop values in the eeg indexes

    :param eeg_indexes: epoch index for each sample in raw data (eeg index or time)
    :param raw_data: data shape [sample, channel]
    :param trial_starts: lst of trial start values (eeg index or time)
    :param trial_stops: lst of trial start values (eeg index or time)
    :param trim: if trim, we will cut the end of one axis to make the concat work.
    :return:
    """
    AV.assert_equal(len(eeg_indexes), raw_data.shape[0])
    AV.assert_equal(len(trial_starts), len(trial_stops))
    epoched_data = None
    for start_stop_index in xrange(len(trial_starts)):
        start_packet_index = bisect.bisect_right(eeg_indexes, trial_starts[start_stop_index])
        end_packet_index = bisect.bisect_left(eeg_indexes, trial_stops[start_stop_index])
        AV.assert_less(start_packet_index, end_packet_index)
        trial_epoched_data = np.expand_dims(raw_data[start_packet_index:end_packet_index], axis=0)
        try:
            epoched_data = trial_epoched_data if epoched_data is None else np.concatenate((epoched_data, trial_epoched_data), axis=0)
        except ValueError:
            if trim:
                min_shape = min(epoched_data.shape[1], trial_epoched_data.shape[1])
                epoched_data = epoched_data[:, :min_shape, :]
                trial_epoched_data = trial_epoched_data[:, :min_shape, :]
                epoched_data = np.concatenate((epoched_data, trial_epoched_data), axis=0)
            else:
                raise ValueError('Epoched data shape', epoched_data.shape, 'Trial Epoched data shape', trial_epoched_data.shape)
    AV.assert_equal(len(trial_stops), epoched_data.shape[0])
    return epoched_data


def cut_epoches_to_same_number_of_samples(epoched_data_list):
    """
    Takes a list of epoched data, (ie a list of data sets, each with the shape (epoch, num_samples, channel)) and trims each data set to have
    the same number of samples.  This is done by finding the data_set with the fewest number of samples and slicing time off the end of all other
    data sets to match.  This method is intended to be used with data sets that are simular in the number of samples, thus trimming the data sets
    does not effect the data much, but allows them to be concatenated. 
    :param epoched_data_list: list of data sets, each with the shape (epoch, num_samples, channel).
    :return: list of data sets, each with the shape (epoch, min_num_samples, channel), where min_num_samples is the same value for all data_sets.
    """
    # Trim our data so it is the same number of samples
    smallest_duration = min([xx.shape[1] for xx in epoched_data_list])
    for index in range(len(epoched_data_list)):
        epoched_data_list[index] = epoched_data_list[index][:, :smallest_duration, :]
    return epoched_data_list


def epoch_data_from_key(eeg_data_indexes, eeg_data, trial_list, start_key_list, end_key_list):
    """
    Takes the list of eeg_data_indexes, eeg_data, trial_list, start_key_list, end_key_list and returns a list
    of epoched data, epoched according to those parameters.  Note that each element of the returned epoched data has the shape
    (epoch, sample, channel), however each element may or may not have the same shape as all other elements.
    
    If you desire all elements to have the same shape, consider calling cut_epoches_to_same_number_of_samples(epoch_data_from_key(args)).
    
    :param eeg_data_indexes: A list of nondecreasing markers for each trial, this can be either time or eeg_indexes.
    :param eeg_data: Unepoched EEG data
    :param trial_list: List of trial dictionaries, as extracted from a log file.
    :param start_key_list: List of start keys
    :param end_key_list: List of corresponding end keys. Must be same length as start_key_list
    :return: List of epoched eeg data, epoched according to the values provided in the trial_list and the start and end key_lists.
    """

    epoched_data_list = []
    for start_key, end_key in zip(start_key_list, end_key_list):
        start_indexes = extract_value_from_list_of_dicts(dictionary_list=trial_list, key=start_key)
        end_indexes = extract_value_from_list_of_dicts(dictionary_list=trial_list, key=end_key)
        end_indexes = convert_start_end_index_lists_to_single_duration_trials(start_trial_index=start_indexes, end_trial_index=end_indexes)
        epoched_data_list.append(epoch_data(eeg_indexes=eeg_data_indexes, trial_starts=start_indexes, trial_stops=end_indexes, raw_data=eeg_data, trim=True))
    return epoched_data_list


def extract_value_from_list_of_dicts(dictionary_list, key):
    """
    Iterates through a given dictionary for key in key order and returns a list of values for that key order
    :param dictionary_list: Dictionary list to extract values for (in order)
    :param key: Key to access in the dictionary
    :return: List of values extracted from the dictionary of length len(key_order).
    """
    return [dictionary[key] for dictionary in dictionary_list]


def stack_epochs(existing, new_trial, axis=0):
    """
    Takes existing epoch epoched data (shape epoch, sample trial) and concats a new trial along the first axis.
    If existing is none, returns new trial.
    """
    return new_trial if existing is None else np.concatenate((existing, new_trial), axis=axis)

def stack_data_values(existing, value_to_stack, axis):
    """
    A general case of stack_epochs, where we stack along the specified axis
    
    If existing is none, we return value_to_stack
    
    :param existing: Our existing numpy array
    :param stacked_value: Our value we want to stack.  Must match in the axis dimension to existing
    :param axis: Axis to stack on
    :return: Our stacked data
    """
    return value_to_stack if existing is None else np.concatenate((existing, value_to_stack), axis=axis)

def average_density_over_epochs(density):
    """
    Takes our densioty of shape (epoch, sample, channel) and averages over all trials.

    :param density: Spectral density of the form (epoch, sample, channel)
    :return: New density of the form (1, sample, channel), where the sample dimension is averaged over epoch
    """

    # Assert density is of the form (epoch, sample, channel)
    assert len(density.shape) == 3

    num_samples = density.shape[1]
    num_channles = density.shape[2]
    averaged = np.average(density, axis=0)

    # restore our epoch dim.
    averaged = np.expand_dims(averaged, axis=0)

    # Ensure we didn't change any unwanted dims.  Only num_epochs (dim 0) should change.
    AV.assert_equal(num_samples, averaged.shape[1])
    AV.assert_equal(num_channles, averaged.shape[2])
    return averaged


def trim_freqs(freqs, density, high=None, low=None):
    """
    Takes freqs and density and trims them according to the high and low values.
    
    if freqs = [ 10.  11.  12.  13.  14. 15. 16]
    and trim freqs is called on this list with high=15 and low=10,
    the result would be [ 10.  11.  12.  13.  14.]
    
    :param freqs: freqs (numpy array)
    :param density: density -- Shape: (epoch, sample, channel) OR (epoch, sample)
    :param high: removes all freqs above and equal to this val . Cast to int if passed a float.
    :param low: removes all freqs below this val.  Cast to int if passed a float.
    :return: freqs, density
            Both elements are modified. Lenght of freqs is equal to the size of the first axis of density (samples).
    """
    original_num_samples = density.shape[1]
    if high is None and low is None:
        raise ValueError('High or low must be an int')

    if high is not None:
        high = int(high)

        index_of_high = bisect.bisect_left(a=freqs, x=high)
        freqs = freqs[:index_of_high]
        try:
            density = density[:, :index_of_high, :]
        except IndexError:
            density = density[:, :index_of_high]
    if low is not None:
        low = int(low)
        index_of_low = bisect.bisect_left(a=freqs, x=low)
        freqs = freqs[index_of_low:]
        try:
            density = density[:, index_of_low:, :]
        except IndexError:
            density = density[:, index_of_low:]
    # Assure we trimmed something
    AV.assert_not_equal(original_num_samples, density.shape[1])
    # Ensure each density pos has a corresponding freq.
    AV.assert_equal(len(freqs), density.shape[1])

    # return the trimmed freqs and trimmed density.
    return freqs, density

def convert_start_end_index_lists_to_single_duration_trials(start_trial_index, end_trial_index):
    """
    Takes two lists of start and end indexes and returns a new end trial index list that ensures
    that all epochs will be the same duration. The duration used is the minimum duration between
    corresponding entries in the lists
    
    Example:
        start_trial_index = [0, 50, 100] 
        end_trial_index = [10, 60, 109]
        
        returns -> [9, 59, 109]
    
    :param start_trial_index: Indexes marking the start of trials
    :param end_trial_index: Indexes marking the end of trials.
    :return: List of new end trial indexes that is equal to the start index list + the minimum duration
    """
    AV.assert_equal(len(start_trial_index), len(end_trial_index))
    return CCDLArrayParser.convert_ununiform_start_stop_lists_to_uniform_start_stop_lists(start_lst=start_trial_index, stop_lst=end_trial_index)


def reepoch_data_with_fixed_window_size(epoched_data, labels, window_size):
    """
    For especially long epochs, we can make them into multiple smaller epochs - and thus have more data to play with
    This takes an np array of epoched data - shape (epoch, sample, channel) and returnes a new np array of shape
    (epoch, sample -- of len window_size, channel) where the num epochs and num samples are different than epoched_data
    Number of channels is unaffected. This transformation is determined by window size.

    A new np array is returned. epoched_data is unmodified.

    Additionally, as we are altering the data array, we will need to change the size of the labels to accommodate.

    :param epoched_data: Original epoched data - shape (epoch, sample, channel)
    :param labels: np array of labels for our data - shape (epoch,)
    :param window_size: Size of desired window (samples)
    :return: transformed epoch data of - shape (new epoch num, new num sample, channel)
    """

    # Get some initial parameters
    original_num_epoch = epoched_data.shape[0]
    block_dur = epoched_data.shape[1]
    num_channels = epoched_data.shape[2]
    # epoched_data.shape -> (num epoch, samples, channels), ie. (32, 4514, 31)

    windows_per_epoch = int(block_dur / window_size)
    # pre allocate space for our new epochs (This is to save time from multiple np concats).
    # Shape is (num new epochs, epoch samples, num channels)  ie. (1184, 120, 31)
    new_data = np.zeros(shape=(windows_per_epoch * original_num_epoch, window_size, num_channels))
    for epoch_index in xrange(0, epoched_data.shape[0]):
        for sample_offset, sample_index in enumerate(xrange(0, block_dur, window_size)):
            # We ran off the edge of our data.  Move onto the next epoch
            if sample_index + window_size >= block_dur: continue

            # Get the new epoch
            new_epoch = epoched_data[epoch_index, sample_index:sample_index + window_size, :]
            assert new_epoch.shape[0] == window_size, '%d, %d' % (new_epoch.shape[0], window_size)

            new_data[epoch_index * windows_per_epoch + sample_offset, :, :] = new_epoch

    # Reshape our labels
    if labels is not None:
        new_labels = []
        for label in labels:
            new_labels += [label] * windows_per_epoch
        labels = np.asarray(new_labels)

    # Return our newly reepoched data - shape (epoch, sample, channel)
    return new_data, labels, windows_per_epoch


def idempotent_add_channel_dimension(data):
    """
    Takes data np array of shape (epoch, channel, channel) or (epoch, sample).  If shape is (epoch, sample), we'll convert it to shape
     (epoch, channel, 1).  If shape is already (epoch, channel, channel), we'll return data without doing anything
    :param data: shape (epoch, channel, channel) or (epoch, sample)
    :return: data with shape (epoch, channel, channel)
    """
    if len(data.shape) != 3:
        return np.expand_dims(data, axis=2)
    else:
        return data


def idempotent_add_epoch_dimension(data):
    """
    Takes data np array of shape (epoch, channel, channel) or (sample, channel).  If shape is (sample, channel), we'll convert it to shape
     (1, channel, channel).  If shape is already (epoch, channel, channel), we'll return data without doing anything
    :param data: shape (epoch, channel, channel) or (sample, channel)
    :return: data with shape (epoch, channel, channel)
    """
    if len(data.shape) != 3:
        return np.expand_dims(data, axis=0)
    else:
        return data
