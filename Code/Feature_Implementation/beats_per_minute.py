def bpms(r_peaks, time):
    total_beats = len(r_peaks)

    return round((total_beats/time),0)