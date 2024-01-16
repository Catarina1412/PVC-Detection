import pandas as pd

def save_as_dataframe(ecg_list, r_list, pvc_list):

    data = {'ecg': ecg_list, 'r_peaks ind': r_list, 'pvc': pvc_list}

    df = pd.DataFrame(data)

    return df