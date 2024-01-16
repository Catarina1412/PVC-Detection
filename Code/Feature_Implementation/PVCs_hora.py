def total_num_pvcs(pvcs):
    """
    Calculates the total number os PVCs occurances in the dataset

    Parameters:
    ----------
    pvcs : List
        List containing the classification of each beat

    Returns:
    -------
    integer
        The total number of PVCs occurances

    Examples:
    --------
    input: [0, 0, 0, 1, 0, 1, 0]
        returns: 2
    """
    total_pvcs = sum([1 for x in pvcs if x == 1])
    return total_pvcs

def PVCs_hour(total_pvcs, time_interval):
    """
    Calculates number of PVCs/hour

    Parameters:
    ----------
    total_pvcs : integer
        Number of total PVCs occurances
    time_interval=30 : integer
        30min time interval
    
    Returns:
    -------
    integer
        The total number of PVCs/hour for that registry

    Examples:
    --------
    input: 2
        returns: int(2/30) (=0)
    """
    pvcs_hour = round((total_pvcs/time_interval)*60,0)
    return pvcs_hour
