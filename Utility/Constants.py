# TODO: when free, integrate this file into CCDLUtil.Constants

class EEGSystemNames(object):
    """
    These are string flags for the EEG systems.
    This is intended to be used to specify the specific eeg data collection system at work.

    for example:

    import CCDLUtil.Utility.Constants as CCDLConstants

    if eeg_system == CCDLConstants.EEGSystemNames.BRAIN_AMP:
        // <brain amp code>
    elif eeg_system == CCDLConstants.EEGSystemNames.GUSB_AMP:
        // <gusb amp code>
    etc.
    """
    BRAIN_AMP = 'brain_amp'
    GUSB_AMP = 'g_usb_amp'
    EMOTIV = 'emotiv'
    OpenBCI = 'open_bci'

    NO_BCI = None  # For testing

    ALL_VALID_NAMES = {BRAIN_AMP, GUSB_AMP, OpenBCI, EMOTIV}
