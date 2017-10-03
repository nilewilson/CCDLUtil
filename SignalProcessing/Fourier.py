"""
Functions related to the fourier transform.
"""

import scipy.signal as scisig
import bisect
import matplotlib.pyplot as plt
import numpy as np
import CCDLUtil.DataManagement.DataParser as CCDLDataParser


def get_channel_fft(single_channel_signal, fs, nperseg, noverlap, filter_sig=False, filter_above=40, filter_below=1):
    """ Returns frequencies and densities from the welch algorithm filtered as appropriate
    """
    freqs, density = scisig.welch(single_channel_signal, fs=fs, nperseg=nperseg, noverlap=noverlap)
    if filter_sig:
        low_index = bisect.bisect_left(freqs, filter_below)
        high_index = bisect.bisect_right(freqs, filter_above)
        freqs = freqs[low_index:high_index]
        density = density[low_index:high_index]
    return freqs, density


def get_fft_all_channels(data, fs, nperseg, noverlap):
    """
    Returns a np array of densities - shape(epoch, density, channel) and the frequency list

    data is shape (epoch, sample, channel)

    :param data: Must be of the form (epoch, sample, channel)
    :param fs: sampling rate
    :param nperseg: nperseg for welch
    :param noverlap: noverlap for welch
    :return: freqs, np array of densities - shape(epoch, density, channel)
    """
    if len(data.shape) != 3:
        raise ValueError("Must be shape (epoch, sample, channel).  Actual Shape %s" % str(data.shape))
    num_channels = data.shape[2]
    dens, freqs = [], None
    for chan in range(num_channels):
        freqs, density = scisig.welch(data[:, :, chan], fs=fs, nperseg=nperseg, noverlap=noverlap, axis=1)
        dens.append(density)
    return freqs, np.swapaxes(np.swapaxes(np.asarray(dens), 0, 1), 1, 2)


def band_power(freqs, density, inclusive_range):
    """
    Calculates the band power for the passed frequency spectrum
    :param freqs: List of frequencies
    :param density: Densities of the corresponding frequencies
    :param inclusive_range: Inclusive range to calculate the band power over
    :return: Unnormalized Band power over the given range - shape -> (epoch, channel)
    """
    low, high = inclusive_range
    low_index = bisect.bisect_left(freqs, low)
    high_index = bisect.bisect_right(freqs, high)
    # density -> shape (epoch, density)
    # high index is noninclusive when indexing a np array, add 1 to account for this.
    # Square the density
    powers = np.square(density[:, low_index:high_index + 1])  # density[:, low_index:high_index + 1] #
    # Sum up the power
    power = np.sum(powers, axis=1)
    # power.shape -> (epoch, channel)
    return power


def get_typical_channel_band_power(freqs, density):
    """
    Returns the band power of standard frequencies
    :param freqs: frequencies
    :param density: Frequency densities
    :return: delta, theta, alpha, low_beta, high_beta
    """
    # Get the band powers of delta, theta, alpha, low_beta, high_beta
    # delta is a np array of shape [epoch, channel]
    delta = band_power(freqs, density, (1, 4))
    theta = band_power(freqs, density, (4, 8))
    alpha = band_power(freqs, density, (8, 12))
    low_beta = band_power(freqs, density, (12, 20))
    high_beta = band_power(freqs, density, (30, 40))
    # Return the values as a tuple.
    return delta, theta, alpha, low_beta, high_beta


def extract_band_features(freqs, density, inclusive_exclusive_bands, channels=None):
    """
    Extracts the power from a given band from the channels.
    :param freqs: Frequencies of the density matrix
    :param density: Shape - (epoch, spectral density, channel)
    :param inclusive_exclusive_bands: Tuple -- band to extract the power for. example: (15, 18) extracts frequencies greater than or equal to 15 and less than
            18 hertz
    :param channels: List of channel indexes to extract from.  If None, all channels are used. Defaults to None.
    :return: Features -- np array of shape (epoch, feature)
    """

    features = None
    for band in inclusive_exclusive_bands:
        try:

            temp_freqs, temp_density = CCDLDataParser.trim_freqs(density=density, freqs=freqs, low=band[0], high=band[1])
        except TypeError:
            raise TypeError("'int' object has no attribute '__getitem__' -- Ensure inclusive_exclusive_bands is a list of tuples")
        if channels is not None:
            temp_density = temp_density[:, :, channels]
        band_density = np.sum(temp_density, axis=1)
        features = CCDLDataParser.stack_data_values(existing=features, value_to_stack=band_density, axis=1)
    return features