def ecg_to_list(qrs_segments):
    QRS_segment = qrs_segments.apply(lambda x: x.strip('][').split(','))
    QRS_segment = QRS_segment.apply(lambda x: [int(i) for i in x])

    return QRS_segment

def rpeak_to_list(r_peaks):
    R_peaks = r_peaks.apply(lambda x: x.strip('][').split(', '))
    R_peaks = R_peaks.apply(lambda x: [int(i) for i in x])

    return R_peaks

def pvcs_to_list(pvcs):
    PVCs = pvcs.apply(lambda x: x.strip('][').split(', '))
    PVCs = PVCs.apply(lambda x: [int(i) for i in x])

    return PVCs
