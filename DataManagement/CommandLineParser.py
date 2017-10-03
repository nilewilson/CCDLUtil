"""
This file is for functions related to taking information from the user via the command line.
"""

import argparse
import os
import time

from CCDLUtil.DataManagement import FileParser as FP


def command_line_with_default_values(default_val_dict):
    """
    This file is to take values from the command line, while preserving default values to run the file script from pycharm
    with hardcoded arguments.

    Default val dict is of the form
        {"var_name": value}
    :param default_val_dict:
    :return: Takes command line arguments and modifies the default val dict to contain those arguments.
    """

    for default_val_name in default_val_dict.keys():
        parser = argparse.ArgumentParser(description='')
        parser.add_argument('--%s' % default_val_name, dest=default_val_dict[default_val_name], nargs='?', type=type(default_val_dict[default_val_name]),
                            default=default_val_dict[default_val_name])
    return default_val_dict


def get_experiment_info_from_user(experiment_name, simple_subject_number=None, condition=None, tms_experiment_tracker_number=None, tms_subject_tracker_number=None, create_subject_folder=True, path_to_data_folder=None,
                                  gen_readme=False):
    """
    If subject number or condition is None, these values will be taken from the user.

    :param experiment_name: Name of the experiment "For example, "PhosChar"

    :param simple_subject_number: The subject identifier for the current experiment.  If None, we'll get this value from the user. Will be converted to a str. Defaults to None.  This usually a number <20.

    :param condition: The condition for the current experiment.  If None, we'll get this value from the user. Will be converted to a str. Defaults to None.

    :param tms_experiment_tracker_number: The TMS group experiment number tracker

    :param tms_subject_tracker_number: The TMS subject number tracker.  This is usually a larger number and is used in the CCDL database.

    :param create_subject_folder:  If true, we'll create the subject folder.

    :param path_to_data_folder: The path to the data folder for this experiment.  If create_subject_folder is True, this value cannot be None. Defaults to none.

    :param gen_readme: If true, will automatically gen a readme file in the subject folder.

    :return: subject_folder path -- Path to the subject folder

             appendable_subject_file_path -- All data should follow the same condition.  We return a value where we should append the desired condition onto the end of the
             string to find our file name.
                     For example
                        log_file_path = appendable_subject_file_path + '.txt'

            subject_file_name -- File name (not path) for the subject  (of the form <experiment>_SubjectX_ConditionY_<File_Format>_<time>)
    """
    if gen_readme:
        assert create_subject_folder
    if create_subject_folder:
        assert path_to_data_folder is not None

    if simple_subject_number is None:
        simple_subject_number = raw_input("Enter Subject Identifier: ")
    if condition is None:
        condition = raw_input("Enter Experiment Condition: ")
    if tms_experiment_tracker_number is None:
        condition = raw_input("Enter TMS Experiment Tracker Number: ")
    if tms_subject_tracker_number is None:
        condition = raw_input("Enter TMS Subject Tracker Number: ")

    time_of_creation = str(int(time.time()))
    subject_file_name = 'Experiment_%s_Subject%s_Condition%s_ExpTracker%s_SubjectTracker%s_Time%s' % (experiment_name, simple_subject_number, condition, tms_experiment_tracker_number, tms_subject_tracker_number, time_of_creation)
    subject_folder_path = path_to_data_folder + '/' + subject_file_name

    appendable_subject_file_path = subject_folder_path + subject_file_name

    if create_subject_folder:
        os.mkdir(subject_folder_path)
    if gen_readme:
        FP.gen_readme_file(appendable_subject_file_path + '_README.txt', experiment_name, simple_subject_number, condition, tms_experiment_tracker_number, tms_subject_tracker_number)

    return subject_folder_path, appendable_subject_file_path, subject_file_name

