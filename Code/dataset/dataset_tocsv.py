import pandas as pd
import sys
sys.path.append('./Code/dataset')
from read_mat_file import mat_tolists
from windowed_ecg import window_ecg
import os
from lists_to_dataframe import save_as_dataframe

#data_dir = os.path.join('../Data/matlab_data')
data_path = os.path.abspath('./Data/matlab_data')

files = [file for file in os.listdir(data_path) if file.endswith(".mat")]

ecg_to_df = []
r_to_df = []
pvc_to_df= []
for file in files:
    print(file)
    ecg, r, pvc = mat_tolists(data_path+'/'+file)
    wdw_ecg = window_ecg(ecg, r, window_size=350)
    ecg_to_df = ecg_to_df + wdw_ecg
    r_to_df = r_to_df + r
    pvc_to_df = pvc_to_df + pvc
    
df = save_as_dataframe(ecg_to_df, r_to_df, pvc_to_df)

df.to_csv('./Data/dataPVC.csv')
