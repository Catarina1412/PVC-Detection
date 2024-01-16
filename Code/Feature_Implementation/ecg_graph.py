import numpy as np
import sys
import os
import plotly.graph_objs as go
from plotly.subplots import make_subplots

sys.path.append('./Code/preprocessing')
sys.path.append('./Code/dataset')

from lowpassfilter import filter

def ecg_plot(ecg, r_peaks, pvcs, minute, fs):
    # Filter the ECG signal
    filtered_ecg_signal, fs = filter(ecg, fs)

    # Divide the filtered signal into 10-second intervals
    window_size = 10 * fs  # 10 seconds
    num_windows = 6
    windowed_signals = np.array_split(filtered_ecg_signal[int((minute-1)*fs*60):int(minute*fs*60)], num_windows)

    fig = make_subplots(rows=num_windows, cols=1, shared_xaxes=True, vertical_spacing=0.05)


    start_ind = (minute-1) * fs * 60
    end_ind = start_ind + len(windowed_signals[0])
    
    for i, windowed_signal in enumerate(windowed_signals):
        t = np.linspace(0, len(windowed_signal)/fs, len(windowed_signal))
        t_r_axs=[]
        ecg_r_axs=[]
        for x in range(len(r_peaks)):
            if int(r_peaks[x]) >= start_ind:
                if int(r_peaks[x]) < end_ind:
                    if pvcs[x] == 1:
                        k = int(r_peaks[x]-start_ind)

                        t_r_axs.append(t[k])
                        ecg_r_axs.append(filtered_ecg_signal[r_peaks[x]])
                else:
                    break
            
        if i==0:
            fig.add_trace(go.Scatter(x=t, y=windowed_signal, mode='lines', line_color='#5A58D7', name='ECG Signal'), row=i+1, col=1)
            fig.add_trace(go.Scatter(x=t_r_axs, y=ecg_r_axs, mode='markers', marker_color='#ff512f', marker_symbol='circle', name='PVC'), row=i+1, col=1)
        fig.add_trace(go.Scatter(x=t, y=windowed_signal, mode='lines', line_color='#5A58D7', name='ECG Signal',showlegend=False), row=i+1, col=1)
        fig.add_trace(go.Scatter(x=t_r_axs, y=ecg_r_axs, mode='markers', marker_color='#ff512f', marker_symbol='circle', name='PVC',showlegend=False), row=i+1, col=1)
        fig.update_xaxes(title_text='Seconds', row=num_windows, col=1)
        fig.update_yaxes(title_text='mV', row=i+1, col=1, side="left")

        start_ind += len(windowed_signal)
        end_ind += len(windowed_signal)
    
    return fig