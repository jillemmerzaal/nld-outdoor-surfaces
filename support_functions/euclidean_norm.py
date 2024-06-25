import pandas as pd
import numpy as np


def euclidean_norm(data, keys):
    data_norm = pd.DataFrame()
    data_norm["X"] = data[keys[0]]["line"]
    data_norm["Y"] = data[keys[1]]["line"]
    data_norm["Z"] = data[keys[2]]["line"]

    return np.linalg.norm(data_norm, axis=1)
