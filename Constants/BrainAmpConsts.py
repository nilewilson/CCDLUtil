"""
This files stores all related constants of BrainAmp device
"""

'''About the Device'''
# name
NAME = 'brain_amp'
# sampling rate
FS = 500
# channel list
CHANNEL_LIST = ['Fp1', 'Fp2', 'F3', 'F4', 'C3', 'C4', 'P3', 'P4', 'O1', 'O2', 'F7', 'F8', 'T7', 'T8', 'P7', 'P8',
                'Fz', 'Cz', 'Pz', 'Oz', 'FC1', 'FC2', 'CP1', 'CP2', 'FC5', 'FC6', 'CP5', 'CP6', 'TP9', 'TP10', 'POz']
# channel dictionary
CHANNEL_DICT = dict(zip(CHANNEL_LIST, range(len(CHANNEL_LIST))))

'''About the CSV File'''
###############
#  for SSVEP  #
###############
# start keys used in log file
START_KEYS= ['start_left_time', 'start_rest2_time', 'start_right_time', 'start_rest1_time']
# end keys used in log file
END_KEYS = ['end_left_time', 'end_rest2_time', 'end_right_time', 'end_rest1_time']
# the column index in csv file that stores time stamps
TIME_INDEX = 1
# header size
HEADER_SIZE = 9
# the column index of the first channel in csv file
DATA_INDEX_START = 2
# the column index of the last channel in csv file
DATA_INDEX_END = -1

