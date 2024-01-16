def total_num_beats(r_peaks):
    """
    Calculates the total number of heart beats in the dataset

    Parameters:
    ----------
    r_peaks : List
        List containing the indexes of each beat

    Returns:
    -------
    integer
        The total number of heart beats present

    Examples:
    --------
    input: [83, 125, 198, 351]
        return: 4
    """
    total_beats = len(r_peaks)
    return total_beats