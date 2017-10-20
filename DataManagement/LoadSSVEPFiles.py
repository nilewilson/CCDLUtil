import CCDLUtil.DataManagement.FileParser as FileParser
import CCDLUtil.DataManagement.DataParser as DataParser
import importlib


def epoch_data(clock_times, eeg_data, trial_list, start_keys, end_keys):
    """
    Epoch data to left, rest2, right, rest1 groups 
    
    :param clock_times: time stamp
    :param eeg_data: the raw eeg data
    :param trial_list: trial list from log file
    :param start_keys: the start key strings used in log file
    :param end_keys: the end key strings used in log file 
    :return: a list of epoch data in order of [left, rest2, right, rest1]
    """
    # extract epoched data
    epoched_data = []
    # start epoch
    for start_key, end_key in zip(start_keys, end_keys):
        start_indices = DataParser.extract_value_from_list_of_dicts(dictionary_list=trial_list, key=start_key)
        end_indices = DataParser.extract_value_from_list_of_dicts(dictionary_list=trial_list, key=end_key)
        # load data into one trial
        indices = DataParser.convert_start_end_index_lists_to_single_duration_trials(start_trial_index=start_indices,
                                                                                     end_trial_index=end_indices)
        # load data
        epoched_data.append(DataParser.epoch_data(eeg_indexes=clock_times, trial_starts=start_indices,
                                                  trial_stops=end_indices, raw_data=eeg_data, trim=True))

    # Trim the data based on the smallest duration
    smallest_duration = min([i.shape[1] for i in epoched_data])
    for i in range(len(epoched_data)):
        epoched_data[i] = epoched_data[i][:, :smallest_duration, :]
    return epoched_data


def load_ssvep_file(log_path, eeg_path, rec_method):
    """
    Load the log file, raw eeg data file and return epoch eeg data in order of [left, rest2, right, rest1]
    
    :param log_path: the path of the log file
    :param eeg_path: the path of the eeg file
	:param rec_method: name of recording equipment used
    :return: epoch eeg data in order of [left, rest2, right, rest1]
    """
    # import constants for the specified recording method
    Constants = importlib.import_module('CCDLUtil.Constants.'+rec_method+'Consts', package=None)
    # read log file
    trial_list, header_list = FileParser.load_ast_dictionary_by_trial(file_path=log_path, header_size=1)
    # read csv file
    eeg_data = FileParser.iter_loadtxt(filename=eeg_path, skiprows=Constants.HEADER_SIZE)
    # only write this w.r.t BrainAmp now
    clock_times = eeg_data[:, Constants.TIME_INDEX]
    # trim data
    eeg_data = eeg_data[:, Constants.DATA_INDEX_START:Constants.DATA_INDEX_END]
    # epoch data
    epoched_data = epoch_data(clock_times, eeg_data, trial_list, Constants.START_KEYS, Constants.END_KEYS)
    left_data, rest2_data, right_data, rest1_data = epoched_data
    return left_data, rest2_data, right_data, rest1_data


if __name__ == '__main__':
    # change this to your own file path
    # LOG_PATH = 'EEG_Data/BrainAmp/test/Subject01__log.txt'
    # EEG_PATH = 'EEG_Data/BrainAmp/test/Subject01__eeg.csv'
	# REC_METHOD = 'BrainAmp'
    # load_ssvep_file(log_path=LOG_PATH, eeg_path=EEG_PATH, rec_method=REC_METHOD)
	print "Dont use this as a primary function or script to run"
