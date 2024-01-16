import sys
import plotly
import statistics

sys.path.append('./Code/dataset')

from windowed_ecg import window_ecg
import plotly.graph_objs as go

def avg_graph(ecg,r):
    window=window_ecg(ecg,r)
    mean_list = [statistics.mean(sublist) for sublist in zip(*window)]
    # Create a layout for the plot
    layout = go.Layout(
    margin=dict(l=0, r=0, t=0, b=0),
    yaxis = dict(title = 'mV'),
    height=200 ,
    width=400,
    )

    # Create a figure object and add the trace and layout
    # Create a trace object with 'x' and 'y' as keys and mean_list as values
    trace = go.Scatter(x=list(range(len(mean_list))), y=mean_list, line_color='#5A58D7')

# Create a figure object and add the trace and layout
    fig = go.Figure(data=[trace], layout=layout)
    return fig 
        
