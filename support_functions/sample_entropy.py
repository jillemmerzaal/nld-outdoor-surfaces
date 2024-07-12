import numpy as np
import math
from support_functions.euclidean_norm import euclidean_norm

# some hard coded variables
# Yentes, J. M., Hunt, N., Schmid, K. K., Kaipust, J. P., McGrath, D., & Stergiou, N. (2013).
# The appropriate use of approximate entropy and sample entropy with short data sets.
# Annals of biomedical engineering, 41, 349-365.
TOL = 0.2
DIM = 2


def sample_entropy(data, ch, **kwargs):
    """
    This function calculates the sample entropy of a given signal. The tolerance is set at 0.2 with a dimension of 2.

    :param data: dictionary containing all data.
    :param data: dictionary containing all data.
    :param ch: list of strings that provide the names three acceleration direction.
    :param kwargs: "event" provides the last step index. Used as input for the Euclidean
    norm. If left empty, the entire timeseries will be analysed.
    :return: sampen; a single float of the calculated sample entropy.
            norm; the Euclidean norm of the three acceleration signals
    """

    norm = euclidean_norm(data, keys=ch)

    if kwargs:
        event = kwargs.get("event")
        norm = norm[:event]

    N = len(norm)
    r = TOL * np.std(norm)
    m = DIM

    # calculate B_i
    matches = np.zeros((m, N)) * np.nan
    for i in range(m):
        matches[i, :N - i] = norm[i:]

    matches = matches.T
    matches_total = np.zeros((matches.shape[0] - 1))

    for i in range(matches.shape[0] - 1):
        lower_bounds = matches[i, :] - r
        upper_bounds = matches[i, :] + r

        match_is_in_range = np.sum((matches >= lower_bounds) & (matches <= upper_bounds), axis=1)
        matches_total[i] = np.sum(match_is_in_range == m) - 1

    B_i = (np.sum(matches_total) / (N - m)) / (N - m)

    del matches, matches_total

    # calculate A_i
    matches = np.zeros((m + 1, N)) * np.nan
    for i in range(m + 1):
        matches[i, :N - i] = norm[i:]

    matches = matches.T
    matches_total = np.zeros((matches.shape[0] - 1))

    for i in range(matches.shape[0] - 2):
        lower_bounds = matches[i, :] - r
        upper_bounds = matches[i, :] + r

        match_is_in_range = np.sum((matches >= lower_bounds) & (matches <= upper_bounds), axis=1)
        matches_total[i] = np.sum(match_is_in_range == m + 1) - 1

    A_i = (np.sum(matches_total) / (N - (m + 1))) / (N - m)

    # Calculate sample entropy
    A = (((N - m - 1) * (N - m)) / 2) * A_i
    B = (((N - m - 1) * (N - m)) / 2) * B_i

    sampen = -math.log(A / B)

    return sampen, norm
