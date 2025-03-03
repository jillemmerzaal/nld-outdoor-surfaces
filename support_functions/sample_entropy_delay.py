import numpy as np
import math
from support_functions.euclidean_norm import euclidean_norm
import EntropyHub as EH
import statsmodels.tsa.stattools as stattools


# some hard coded variables
# Yentes, J. M., Hunt, N., Schmid, K. K., Kaipust, J. P., McGrath, D., & Stergiou, N. (2013).
# The appropriate use of approximate entropy and sample entropy with short data sets.
# Annals of biomedical engineering, 41, 349-365.
TOL = 0.2
DIM = 2

def sample_entropy_delay(data, ch, **kwargs):
    norm = euclidean_norm(data, keys=ch)

    if kwargs:
        event = kwargs.get("event")
        norm = norm[:event]

    _lags = len(norm)
    autocorr = stattools.acf(norm, nlags=_lags)
    drop_value = 1 / np.exp(1)
    TAU = np.argmax(autocorr < drop_value)
    Samp, A, B = EH.SampEn(Sig=norm, m=DIM, tau=int(TAU), r=None)

    return Samp, norm
