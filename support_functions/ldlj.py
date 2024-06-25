import numpy as np
import math


def log_dimensionless_jerk_imu(data, ch, **kwargs):
    """
    Calculates the log dimensionless jerk for a given acceleration signal.

    Code adapted from:
    Melendez-Calderon, A., Shirota, C., & Balasubramanian, S. (2021). Estimating movement smoothness
    from inertial measurement units. Frontiers in bioengineering and biotechnology, 8, 558771.

    :param data: dictionary containing all data.
    :param ch: list of strings that provide the names three acceleration direction.
    :param kwargs: "event" provides the last step index. Used as input for the Euclidean
    norm. If left empty, the entire timeseries will be analysed.
    :return:
    """
    if kwargs:
        event = kwargs.get("event")

    ldlj_factor = log_dimensionless_jerk_factors(data, ch, event)
    ldlj = ldlj_factor[0] + ldlj_factor[1] + ldlj_factor[2]

    return ldlj


# embedded functions
def log_dimensionless_jerk_factors(data, ch, last_step):
    """
    Returns the individual factors of the log dimensionless jerk metric
    used for IMU data.
    :param data: dictionary containing all data.
    :param ch: list of strings that provide the names three acceleration direction.
    :param last_step: int the index for the last step
    ":return: factors to calculate the LDLJ
    """
    accls = np.array([data[ch[0]]['line'][:last_step],
                      data[ch[1]]["line"][:last_step],
                      data[ch[2]]["line"][:last_step]]).T

    N = len(accls)

    gyros = None

    a_Z_static, a_Y_static, a_X_static = gravity_component(np.array(data[ch[0]]['line']),
                                                           np.array(data[ch[1]]["line"]),
                                                           np.array(data[ch[2]]["line"]))

    grav = [a_Z_static, a_Y_static, a_X_static]

    # Sample time
    freq = data["zoosystem"]["Video"]["Freq"]
    dt = 1. / freq
    # _N = len(accls)

    # Movement duration.
    mdur = N * dt

    # Gravity subtracted mean square ampitude
    mamp = np.power(np.linalg.norm(accls), 2) / N

    if gyros is not None:
        mamp = mamp - np.power(np.linalg.norm(grav), 2)

    # Derivative of the accelerometer signal
    _daccls = np.vstack((np.zeros((1, 3)), np.diff(accls, axis=0) * freq)).T

    # Get corrected jerk if gyroscope data is available.
    if gyros is not None:
        _awcross = np.array([np.cross(_as, _ws)
                             for _as, _ws in zip(accls, gyros)]).T
    else:
        _awcross = np.zeros(np.shape(_daccls))

    # Corrected jerk
    _jsc = _daccls - _awcross
    mjerk = np.sum(np.power(np.linalg.norm(_jsc, axis=0), 2)) * dt

    ldlj_factor = [-np.log(mdur),
                   np.log(mamp),
                   -np.log(mjerk), ]

    return ldlj_factor

def gravity_component(x, y, z):
    """
    Determines the gravity compnent of the x, y, and z direction of the acceleration signal using trigonomitry.
    :param x:
    :param y:
    :param z:
    :return:
    """
    a_x = x.mean()
    a_y = y.mean()
    a_z = z.mean()

    # Anterior tilt
    TiltAngle_z_rad = np.arcsin(a_z)
    TiltAngle_z_deg = math.degrees(TiltAngle_z_rad)

    # mediolateral tilt
    TiltAngle_y_rad = np.arcsin(a_y)
    TiltAngle_y_deg = math.degrees(TiltAngle_y_rad)

    # Anterior posterior
    a_Z = (a_z * np.cos(TiltAngle_z_rad)) - (a_x * np.sin(TiltAngle_z_rad))
    # AMediolateral
    a_Y = (a_y * np.cos(TiltAngle_y_rad)) - (a_x * np.sin(TiltAngle_y_rad))

    # a_vt_prov = a_ap*Sin(theta_ap) + a_vt*Cos(theta_ap)
    a_z_prov = (a_z * np.sin(TiltAngle_z_rad)) + (a_x * np.cos(TiltAngle_z_rad))

    # a_VT = a_ml*sin(theta_ml) + a_vt_prov*cos(theta_ml) - 1
    a_X = (a_y * np.sin(TiltAngle_y_rad)) + (a_z_prov * np.cos(TiltAngle_y_rad)) - 1

    a_z_static = a_z - a_Z
    a_y_static = a_y - a_Y
    a_x_static = a_x - a_X

    return a_z_static, a_y_static, a_x_static
