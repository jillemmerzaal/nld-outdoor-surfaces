import math
import numpy as np
import statsmodels.tsa.stattools as stattools
import scipy
import pandas as pd
import numpy.polynomial.polynomial as poly
import numpy.matlib as nmp
import matplotlib.pyplot as plt
import support_functions.fnn as fnn
import support_functions.ami_stergio as ami_stergio
from support_functions.visualizations import multiple_custom_plots

MIN_DISTANCE = 30
MIN_HEIGHT = 0.10
SAMPLE_FREQUENCY = 100
TOL = 0.2
DIM = 2
WS = 10


# Create outer class
class NonLinearDynamics:
    def __init__(self, data, last_step_idx):

        self.data = data
        self.last_step = last_step_idx
        self.norm = []
        self.extract_freq()
        self.create_norm()
        self.N = len(self.norm)
        self.sample_entropy = []
        self.ad_2 = []
        self.d_2 = []
        self.ad_1 = []
        self.d_1 = []
        self.lds = []

    def create_norm(self):
        data_norm = pd.DataFrame()
        data_norm["X"] = self.data["Acc_x"]["line"][:self.last_step]
        data_norm["Y"] = self.data["Acc_y"]["line"][:self.last_step]
        data_norm["Z"] = self.data["Acc_z"]["line"][:self.last_step]

        self.norm = np.linalg.norm(data_norm, axis=1)

    def extract_freq(self):
        self.freq = self.data["zoosystem"]["Video"]["Freq"]

    def sampen(self):
        r = TOL * np.std(self.norm)
        m = DIM

        # calculate B_i
        matches = np.zeros((m, self.N)) * np.nan
        for i in range(m):
            matches[i, :self.N - i] = self.norm[i:]

        matches = matches.T
        matches_total = np.zeros((matches.shape[0] - 1))

        for i in range(matches.shape[0] - 1):
            lower_bounds = matches[i, :] - r
            upper_bounds = matches[i, :] + r

            match_is_in_range = np.sum((matches >= lower_bounds) & (matches <= upper_bounds), axis=1)
            matches_total[i] = np.sum(match_is_in_range == m) - 1

        B_i = (np.sum(matches_total) / (self.N - m)) / (self.N - m)

        del matches, matches_total

        # calculate A_i
        matches = np.zeros((m + 1, self.N)) * np.nan
        for i in range(m + 1):
            matches[i, :self.N - i] = self.norm[i:]

        matches = matches.T
        matches_total = np.zeros((matches.shape[0] - 1))

        for i in range(matches.shape[0] - 2):
            lower_bounds = matches[i, :] - r
            upper_bounds = matches[i, :] + r

            match_is_in_range = np.sum((matches >= lower_bounds) & (matches <= upper_bounds), axis=1)
            matches_total[i] = np.sum(match_is_in_range == m + 1) - 1

        A_i = (np.sum(matches_total) / (self.N - (m + 1))) / (self.N - m)

        # Calculate sample entropy
        A = (((self.N - m - 1) * (self.N - m)) / 2) * A_i
        B = (((self.N - m - 1) * (self.N - m)) / 2) * B_i
        self.sample_entropy = -math.log(A / B)

    def symmetry(self):
        _lags = len(self.norm)
        self.autocorr = stattools.acf(self.norm, nlags=_lags)
        peaks_auto, peak_properties = scipy.signal.find_peaks(self.autocorr, distance=MIN_DISTANCE, height=MIN_HEIGHT)

        try:
            self.d_1 = peaks_auto[0]
            self.ad_1 = peak_properties["peak_heights"][0]
            self.d_2 = peaks_auto[1]
            self.ad_2 = peak_properties["peak_heights"][1]
        except IndexError:
            self.d_1 = -999
            self.ad_1 = -999
            self.d_2 = -999
            self.ad_2 = -999
        else:
            if self.d_1 < 30:
                self.d_1 = peaks_auto[1]
                self.ad_1 = peak_properties["peak_heights"][1]
                self.d_2 = peaks_auto[2]
                self.ad_2 = peak_properties["peak_heights"][2]

        ax_out = multiple_custom_plots(self.autocorr, self.d_1, self.autocorr[self.d_1],
                                       self.d_2, self.autocorr[self.d_2])

        # ax_out.set(ylabel=self.data['zoosystem']["Video"]['SourceFile'], xlim=[0, 500])
        # figname = f"Subject{self.data['zoosystem']['subj_no']}_{self.data['zoosystem']['surface']}"
        # plt.savefig(f"./Figures/Autocorr/{figname}.jpeg")

        plt.close()
        # del figname



    def log_dimensionless_jerk_factors(self):
        """
        Returns the individual factors of the log dimensionless jerk metric
        used for IMU data.
        Parameters
        """
        self.accls = np.array([self.data["Acc_x"]['line'][:self.last_step],
                               self.data["Acc_y"]["line"][:self.last_step],
                               self.data["Acc_z"]["line"][:self.last_step]]).T

        self.gyros = None

        self.gravity_component(self.data["Acc_x"]['line'],
                               self.data["Acc_y"]["line"],
                               self.data["Acc_z"]["line"])

        self.grav = [self.a_Z_static, self.a_Y_static, self.a_X_static]

        # Sample time
        dt = 1. / self.freq
        # _N = len(accls)

        # Movement duration.
        mdur = self.N * dt

        # Gravity subtracted mean square ampitude
        mamp = np.power(np.linalg.norm(self.accls), 2) / self.N

        if self.gyros is not None:
            mamp = mamp - np.power(np.linalg.norm(self.grav), 2)

        # Derivative of the accelerometer signal
        _daccls = np.vstack((np.zeros((1, 3)), np.diff(self.accls, axis=0) * self.freq)).T

        # Get corrected jerk if gyroscope data is available.
        if self.gyros is not None:
            _awcross = np.array([np.cross(_as, _ws)
                                 for _as, _ws in zip(self.accls, self.gyros)]).T
        else:
            _awcross = np.zeros(np.shape(_daccls))

        # Corrected jerk
        _jsc = _daccls - _awcross
        mjerk = np.sum(np.power(np.linalg.norm(_jsc, axis=0), 2)) * dt

        self.ldlj_factor = [-np.log(mdur),
                            np.log(mamp),
                            -np.log(mjerk), ]

    def log_dimensionless_jerk_imu(self):
        self.log_dimensionless_jerk_factors()
        self.ldlj = self.ldlj_factor[0] + self.ldlj_factor[1] + self.ldlj_factor[2]

    def gravity_component(self, x, y, z):
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

        self.a_Z_static = a_z - a_Z
        self.a_Y_static = a_y - a_Y
        self.a_X_static = a_x - a_X

    def get_lye_elements(self):
        self.ami = ami_stergio.AMI_Stergiou(self.norm, 30)
        print(f"time delay with the AMI: {self.ami[1][1]}")
        # plt.plot(self.ami[1][1])
        self.TAU = int(self.ami[0][0][0])

        [self.dE, self.DIM] = fnn.FNN(self.norm, self.TAU, 12, 15, 2, 1)

    def LyE_R(self):
        self.get_lye_elements()
        fs = self.freq
        tau = self.TAU
        dim = self.DIM
        X = np.array(self.norm, ndmin=2)
        r, c = np.shape(X)
        if r > c:
            X = np.copy(X.transpose())

        # Checks if a multidimentional array was entered as X.
        if np.size(X, axis=0) > 1:
            M = np.shape(X)[1]
            Y = X
        else:
            # Calculate useful size of data
            N = np.shape(X)[1]
            M = N - (dim - 1) * tau

            Y = np.zeros((M, dim))
            for j in range(dim):
                Y[:, j] = X[:, 0 + j * tau:M + j * tau]
        # Find nearest neighbors

        IND2 = np.zeros((1, M), dtype=int)
        for i in range(M):
            # Find nearest neighbor.
            Yinit = nmp.repmat(Y[i], M, 1)
            Ydiff = (Yinit - Y[0:M, :]) ** 2
            Ydisti = np.sqrt(np.sum(Ydiff, axis=1))

            # Exclude points too close based on dominant frequency.
            range_exclude = np.arange(round((i + 1) - tau * 0.8 - 1), round((i + 1) + tau * 0.8))
            range_exclude = range_exclude[(range_exclude >= 0) & (range_exclude < M)]
            Ydisti[range_exclude] = 1e5

            # find minimum distance point for first pair
            IND2[0, i] = np.argsort(Ydisti)[0]

        out = np.vstack((np.arange(M), np.ndarray.flatten(IND2)))

        # Calculate distances between matched pairs.
        DM = np.zeros((M, M))

        IND2len = np.shape(IND2)[1]

        for i in range(IND2len):
            # The data can only be propagated so far from the matched pair.
            EndITL = M - IND2[:, i][0]
            if (M - IND2[:, i][0]) > (M - i):
                EndITL = M - i

            # Finds the distance between the matched paris and their propagated
            # points to the end of the useable data.
            DM[0:EndITL, i] = np.sqrt(
                np.sum((Y[i:EndITL + i, :] - Y[IND2[:, i][0]:EndITL + IND2[:, i][0], :]) ** 2, axis=1))

        # Calculates the average line divergence.
        r, _ = np.shape(DM)

        AveLnDiv = np.zeros(len(DM))
        # NOTE: MATLAB version does not preallocate AveLnDiv, we could preallocate that.
        for i in range(r):
            distanceM = DM[i, :]
            if np.sum(distanceM) != 0:
                AveLnDiv[i] = np.mean(np.log(distanceM[distanceM > 0]))

        out = np.vstack((out, AveLnDiv))
        self.AveLnDiv = AveLnDiv

        period = self.d_2 / fs
        ws = round(WS * fs)
        # find the least square fit
        L1 = int(0.5 * period * fs)
        self.L1 = L1

        # np.arange(1 / fs, L1, 1 / fs)
        # Ps = poly.polyfit(np.arange(1 / fs, L1 / fs, 1 / fs), AveLnDiv[1:L1], 1)
        np.arange(1 / fs, L1, 1 / fs)
        Ps = poly.polyfit(np.arange(1 / fs, L1 / fs, 1 / fs), AveLnDiv[1:L1], 1)
        if ws > 4 * period * fs:
            L2 = int(4 * period * fs)
            self.L2 = L2
            print(f"Length of x: {len(np.arange(L2 / fs, ws / fs, 1 / fs))}")
            print(f"Length of Y :{len(AveLnDiv[L2:ws])}")

            if len(np.arange(L2 / fs, ws / fs, 1 / fs)) == len(AveLnDiv[L2:ws]):
                Pl = poly.polyfit(np.arange(L2 / fs, ws / fs, 1 / fs), AveLnDiv[L2:ws], 1)
            elif len(np.arange(L2 / fs, ws / fs, 1 / fs)) - len(AveLnDiv[L2:ws]) == 1:
                Pl = poly.polyfit(np.arange(L2 / fs, ws / fs, 1 / fs), AveLnDiv[L2:ws + 1], 1)
            else:
                Pl = [np.nan, np.nan]

        self.lds = [Ps[1], Pl[1]]

        Ys = poly.polyval(np.arange(1 / self.freq, L1 / self.freq, 1 / self.freq), Ps)
        Yl = poly.polyval(np.arange(L2 / self.freq, ws / self.freq, 1 / self.freq), Pl)

        x_as = np.arange(1 / self.freq, ws / self.freq, 1 / self.freq)
        plt.plot(x_as, AveLnDiv[:ws - 1])

        plt.plot(np.arange(1 / self.freq, L1 / self.freq, 1 / self.freq), Ys, 'm')
        plt.plot(np.arange(L2 / self.freq, ws / self.freq, 1 / self.freq), Yl, 'r')

        figname = f"Subject{self.data['zoosystem']['subj_no']}_{self.data['zoosystem']['surface']}"
        plt.savefig(f"./Figures/LyE_R/{figname}.jpeg")

        plt.close()
        del figname
