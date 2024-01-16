import scipy.io

def mat_tolists(mat_file_path):
    # load the .mat file
    mat = scipy.io.loadmat(mat_file_path)

    # get the data from the .mat file
    data = mat['DAT']
    

    ecg = data[0][0][0].squeeze().tolist()
    r_peak_ind = data[0][0][1].squeeze().tolist()
    pvc = data[0][0][2].squeeze().tolist()

    return ecg, r_peak_ind, pvc