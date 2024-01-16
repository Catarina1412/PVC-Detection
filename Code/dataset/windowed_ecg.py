def window_ecg(ecg, r, window_size=350):
    windowed_ecg = []
    for ind in r:
        qrs_start = max(0, ind - window_size // 2)
        qrs_end = min(len(ecg) - 1, ind + window_size // 2)
        if qrs_start == 0:
            windowed_ecg.append([0]*(-(ind - window_size // 2)) + ecg[qrs_start:qrs_end])
        elif qrs_end == len(ecg)-1:
            windowed_ecg.append(ecg[qrs_start:qrs_end] + [0]*int((ind + window_size // 2) - (len(ecg) - 1)))
        else:
            windowed_ecg.append(ecg[qrs_start:qrs_end])
    
    return windowed_ecg