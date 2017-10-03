import platform
import CCDLUtil.Utility.Constants as CCDLConstants

def is_linux():
    return get_os_type().startswith('linux')


def is_windows():
    return get_os_type().startswith('windows')


def get_os_type():
    """
    returns 'windows' or 'linux' depending which os you're running.
    """
    return platform.system().lower()

def get_eeg_sampling_rate(eeg_system, return_channel_info=False):
    """
    Gives the specs for each of the eeg systems.
    :param eeg_system: str - what eeg system are we using?
    """
    if eeg_system == CCDLConstants.EEGSystemNames.GUSB_AMP:
        fs = 512
    elif eeg_system == CCDLConstants.EEGSystemNames.BRAIN_AMP:
        fs = 500
    elif eeg_system == CCDLConstants.EEGSystemNames.OpenBCI:
        fs = 250
    elif eeg_system == CCDLConstants.EEGSystemNames.NO_BCI:
        fs = None
    else:
        raise ValueError('Invalid or unimplemented eeg system')
    return fs