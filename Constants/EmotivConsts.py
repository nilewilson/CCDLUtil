"""
This files stores all related constants of Emotiv device
"""

'''About the Device'''
# sampling rate
FS = 250
# channel list
CHANNEL_LIST = ['AF3', 'F7', 'F3', 'FC5', 'T7', 'P7', 'O1', 'O2', 'P8', 'T8', 'FC6', 'F4', 'F8', 'AF4', 'GYROX', 'GYROY']
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
TIME_INDEX = -1
# header size
HEADER_SIZE = 1
# the column index of the first channel in csv file
DATA_INDEX_START = 1
# the column index of the last channel in csv file
DATA_INDEX_END = -6