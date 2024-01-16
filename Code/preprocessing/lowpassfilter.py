from scipy.signal import butter, lfilter, lfilter_zi

def filter_parameters():
    # Define the filter parameters
    # fs = 360.0 # Sampling frequency
    cutoff = 100 # Cutoff frequency (below the Nyquist Frequency)
    order = 4 # Filter order
    return cutoff, order

def butter_lowpass(cutoff, fs, order):
    nyq = 0.5 * fs
    normal_cutoff = cutoff / nyq
    b, a = butter(order, normal_cutoff, btype='low', analog=False)
    return b, a

def filter(ecg_data,fs):
    cutoff, order = filter_parameters()

    ecg_signal = ecg_data

    # Obtain the initial conditions for the filter
    b, a = butter_lowpass(cutoff, fs, order)
    zi = lfilter_zi(b, a)

    # Pre-filter the first few samples of the ECG signal
    n_samples = 100 # Number of samples to pre-filter
    pre_filtered_ecg_signal, _ = lfilter(b, a, ecg_signal[:n_samples], zi=zi*ecg_signal[0])

    # Apply the filter to the ECG signal
    filtered_ecg_signal, _ = lfilter(b, a, ecg_signal, zi=zi*ecg_signal[0])

    return filtered_ecg_signal, fs


