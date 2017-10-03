import pyaml
import yaml
import pickle
import os
import argparse
import numpy as np
import CCDLUtil.Utility.AssertVal as AV
import time
import bisect
import ast
import scipy.io
import CCDLUtil.Utility.Constants as CCDLConstants


def load_yaml_file(config_file_path):
    """
    Loads a yaml file and returns the results
    """
    with open(config_file_path, 'r') as stream:
        d = yaml.load(stream)
    return d


def save_yaml_file(yaml_file_path, data, default_flow_style=True):
    """
    Gets a configuration dictionary for this experiment
    """
    with open(yaml_file_path, 'w') as outfile:
        pyaml.dump(data, outfile, default_flow_style)


def save_pickle_file(pickle_file_path, data, protocol=pickle.HIGHEST_PROTOCOL):
    """
    Save a pickle file in binary mode
    """
    with open(pickle_file_path, 'wb') as fp:
        pickle.dump(data, fp, protocol)


def load_pickle_file(pickle_file_path, binary=True):
    """
    Loads a pickle file and returns the results
    """
    binary = 'b' if binary else ''
    with open(pickle_file_path, 'r' + binary) as fp:
        return pickle.load(fp)


def save_matlab_file(mat_file_path, data, appendmat=True):
    """
    Saves a python dictionary (data) as a .mat file.
        :param mat_file_path : str or file-like object
            Name of the .mat file (.mat extension not needed if appendmat is True). Can also pass open file_like object.
        :param data : dict - Dictionary from which to save matfile variables.
    """
    scipy.io.savemat(file_name=mat_file_path, mdict=data, appendmat=appendmat)


def load_matlab_file(mat_file_path):
    """
    Loads a .mat file to a python dictionary
    :param mat_file_path: The path to the matlab file.
    """
    return scipy.io.savemat(file_name=mat_file_path)


def get_standard_mat_format(eeg_system, unepoched_eeg_data, event_markers, channel_names, experiment_description, date_collected, fs, time_stamps, packet_indexes, aux_data=None, subject_name=None):
    """
    Returns a dictionary that can be saved in our standard .mat format.  (See readme for more information on this formatting).  If save_location_path is not None, it will also be saved to this location.

    time_stamps or packet_indexes can be None.  If it is None, it will not be included in our returned dictionary.  This method raises a Value error if both are None.

    :param eeg_system: string - The EEG System must be a valid system as shown in CCDLUtil.Utility.Constants.EEGSystemNames.ALL_VALID_NAMES
    :param unepoched_eeg_data: Our unepoched EEG with shape (sample, channel)
    :param event_markers: Our event markers that could be used for epoching our eeg
    :param channel_names: list or numpy array - The names of our channels. The length of this list should be equal to unepoched_eeg_data.shape[1].
    :param experiment_description: sting - A written description of what occurred during the experiment.
    :param date_collected: string - Denoting the date in which the data was collected.
    :param fs: int - Our sampling rate in Hz.
    :param time_stamps: numpy array or None. - The packet arrival times for our data.  This value is usually recorded alongside our eeg data.
    :param packet_indexes: numpy array or None. - The packet indexes times for our data.  This value is usually recorded alongside our eeg data.
    :param aux_data: Numpy array or None (defaults to None)
    :param subject_name: String, Number, or None - The name or number of our subject.
    :param save_location_path: String or None (defaults to None) - The location in which to save the mat formatted dictionary.  If None, it will not be saved.
    :return: A dictionary that fits our standard .mat formatting.
    """
    if eeg_system not in CCDLConstants.EEGSystemNames.ALL_VALID_NAMES:
        raise ValueError('The EEG System must be a valid system as shown in CCDLUtil.Utility.Constants.EEGSystemNames.ALL_VALID_NAMES')
    if unepoched_eeg_data.shape[1] != len(list(channel_names)):
        raise ValueError('There are not the same number of channel names as channels given: %d Channels, %d Channel Names' % (unepoched_eeg_data.shape[1], len(channel_names)))
    if time_stamps is None and packet_indexes is None:
        raise ValueError('time_stamps and packet_indexes cannot both be None.')
    mdict = {'description': experiment_description, 'date_collected': date_collected, 'unepoched_eeg_data': unepoched_eeg_data,
             'channel_names': channel_names, "fs": fs, "event_markers": event_markers, 'eeg_system': eeg_system}
    if aux_data is not None:
        mdict['aux_data'] = aux_data
    if subject_name is not None:
        mdict['subject_name'] = subject_name
    return mdict

def save_standard_mat_format(save_path, eeg_system, unepoched_eeg_data, event_markers, channel_names, experiment_description, date_collected, fs, time_stamps, packet_indexes, aux_data=None, subject_name=None, verbose=True):
    """
    Returns a dictionary that can be saved in our standard .mat format.  (See readme for more information on this formatting).  If save_location_path is not None, it will also be saved to this location.

    time_stamps or packet_indexes can be None.  If it is None, it will not be included in our returned dictionary.  This method raises a Value error if both are None.

    :param save_path: Where to save the mat file
    :param eeg_system: string - The EEG System must be a valid system as shown in CCDLUtil.Utility.Constants.EEGSystemNames.ALL_VALID_NAMES
    :param unepoched_eeg_data: Our unepoched EEG with shape (sample, channel)
    :param event_markers: Our event markers that could be used for epoching our eeg
    :param channel_names: list or numpy array - The names of our channels. The length of this list should be equal to unepoched_eeg_data.shape[1].
    :param experiment_description: sting - A written description of what occurred during the experiment.
    :param date_collected: string - Denoting the date in which the data was collected.
    :param fs: int - Our sampling rate in Hz.
    :param time_stamps: numpy array or None. - The packet arrival times for our data.  This value is usually recorded alongside our eeg data.
    :param packet_indexes: numpy array or None. - The packet indexes times for our data.  This value is usually recorded alongside our eeg data.
    :param aux_data: Numpy array or None (defaults to None)
    :param subject_name: String, Number, or None - The name or number of our subject.
    :param save_location_path: String or None (defaults to None) - The location in which to save the mat formatted dictionary.  If None, it will not be saved.
    :return: A dictionary that fits our standard .mat formatting.
    """
    mdict = get_standard_mat_format(eeg_system, unepoched_eeg_data, event_markers, channel_names, experiment_description, date_collected, fs, time_stamps, packet_indexes, aux_data=aux_data, subject_name=subject_name)

    save_matlab_file(mat_file_path=save_path, data=mdict)
    if verbose:
        print 'Saved mat file to:', save_path
    return mdict

def iter_loadtxt(filename, delimiter=',', skiprows=0, dtype=float):
    """
    Loads a txt file to a 2D numpy array. This is effectively equivalent to np.loadtxt() - but more efficient.

    Ignores incomplete rows and trailing delimiters.
    :param filename: Name of file to load
    :param delimiter: Delimiter (such as ',')
    :param skiprows: Skip rows in header.
    :param dtype: type of data.
    :return: np array of data.
    """
    def iter_func():
        line_len = None
        with open(filename, 'r') as infile:
            for _ in range(skiprows):
                next(infile)
            for line in infile:
                line = line.strip()
                # Remove deliminator if needed.
                if line.endswith(delimiter):
                    line = line[:-1] + '\n'
                line = line.rstrip().split(delimiter)
                line_len = len(line) if line_len is None else line_len
                if len(line) != line_len:
                    continue
                for item in line:
                    try:
                        yield dtype(item)
                    except ValueError:
                        # Most likely cause of an error here is a problem with a trailing deliniator.
                        print item, type(item)
                        raise
        iter_loadtxt.rowlength = line_len
    data = np.fromiter(iter_func(), dtype=dtype)
    try:
        data = data.reshape((-1, iter_loadtxt.rowlength))
    except AttributeError:
        print "Check to ensure file is not blank"
        time.sleep(2)
        raise
    return data


def manage_storage(data_storage_location, take_init):
    """
    Deals with the file system to init all files

    Data storage location is the data file, not a particular subject folder.  The subject folder will be created, along with a subject id,
    and the path returned to the user.
    """
    if not os.path.exists(data_storage_location):
        os.mkdir(data_storage_location)
    if not data_storage_location.endswith('/'):
        data_storage_location += '/'
    subject_id = raw_input("Enter Subject Number: ") if take_init else str(0)
    subject_data_foler_path = data_storage_location + 'Subject' + str(subject_id) + '__timestamp_' + str(time.time()) + '/'
    os.mkdir(subject_data_foler_path)
    
    # subject_data_folder_path ends with /
    return subject_id, subject_data_foler_path


def load_ast_dictionary_by_trial(file_path, header_size=0, record_header=True):
    """
    Takes an experiment log file and reads it in line by line with ast.literal eval.  See readme file for more information.
    Ignores blank lines.

    This method does not epoch EEG data.

    :param file_path: Path to file to be read
    :param header_size: Size of header
    :return: (trial_list, header_list).  The trial list is a list of dictionaries, each representing a trial. The header is a list of dicts
    for each line in header_size. If header_size = 0, will return header_size=[]
    """
    header_list = []
    trial_list = []
    with open(file_path, 'r') as f:
        for line_index, line in enumerate(f):
            if len(line) > 0:
                if line_index < header_size:
                    if record_header:
                        header_list.append(ast.literal_eval(line[:-1]))  # -1 is to remove newline character.
                else:
                    if line.endswith('\n'):
                        trial_list.append(ast.literal_eval(line[:-1]))
                    else:
                        trial_list.append(ast.literal_eval(line))
    return trial_list, header_list


def gen_readme_file(readme_file_path, experiment_name, simple_subject_number, condition, tms_experiment_tracker_number, tms_subject_tracker_number):
    """
    Generates a readme file (located at readme_file_path) that includes the passed information
    """
    with open(readme_file_path, 'r') as f:
        readme_dict = {'Experiment Name' : experiment_name,
                       'Subject Number' : str(simple_subject_number),
                       'Experimental Condition' : str(condition),
                       'Experiment Tracking Number' : str(tms_experiment_tracker_number),
                       'Subject Tracking Number' : str(tms_subject_tracker_number)}

        f.write('\n'.join([str(readme_dict),
                           'Experiment Name' + str(experiment_name),
                           'Subject Number' + str(simple_subject_number),
                           'Experimental Condition' + str(condition),
                           'Experiment Tracking Number' + str(tms_experiment_tracker_number),
                           'Subject Tracking Number' + str(tms_subject_tracker_number)]))


def idempotent_dir_creation(new_dir_path):
    """
    Checks if new_path exists. If it doesn't exist, it will make a new folder at that location.
    :param new_dir_path: Desired location of new directory.
    :return new_dir_path.  Returns new path (unmodified)
    """
    if not os.path.exists(new_dir_path):
        os.mkdir(new_dir_path)
    return new_dir_path


def convert_to_windows_path(path_str):
    """
    Converts a path, such as 'C:/Users/eeglab/PycharmProjects' to 'C:\Users\eeglab\PycharmProjects'
    :param path_str:
    :return:
    """
    return path_str.replace('/', '\\')


# if __name__ == '__main__':
#     linx_path = 'C:/Users/Experimenter/PycharmProjects'
#     xxx = convert_to_windows_path(linx_path)
#     print xxx
#     print os.path.exists(convert_to_windows_path(linx_path))
#     print os.path.join(xxx, 'cat')