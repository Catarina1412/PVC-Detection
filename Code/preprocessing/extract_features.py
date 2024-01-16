import numpy as np
from scipy import signal
import sys

def features(ecg, r_peak, fs=360):
    features = []

    for i, qrs_segment in enumerate(ecg):
        # Extract amplitude features
        mean_amplitude = np.mean(qrs_segment)

        # Extract time domain features
        slope = np.polyfit(range(len(qrs_segment)), qrs_segment, 1)[0]

        # Extract frequency domain features
        f, psd = signal.welch(qrs_segment, fs)
        dominant_frequency = f[np.argmax(psd)]
        high_frequency_power = np.sum(psd[np.where(f > 40)])

        # Extract other features
        area_under_curve = np.trapz(qrs_segment)

        features.append([mean_amplitude, slope,area_under_curve])# dominant_frequency, high_frequency_power, area_under_curve])

    return features