"""
This files stores all related constants of OpenBCI device
"""

'''About the Device'''
# name
NAME = 'open_bci'
# sampling rate
FS = 250

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
HEADER_SIZE = 0
# the column index of the first channel in csv file
DATA_INDEX_START = 2
# the column index of the last channel in csv file
DATA_INDEX_END = 10
