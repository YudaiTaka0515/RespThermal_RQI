import cv2
import numpy as np
from scipy.fftpack import fft
from scipy import signal
import matplotlib.pyplot as plt
from statistics import mean, median, variance, stdev
import matplotlib.pyplot as plt
import statistics
from SignalProcess import Roi2Signal
from GLOBAL import *

import os
from math import e, tanh, atan, pi
# sampling rate = 8.6, RR分解能 = 0.1にするためのpadding
FREQUENCY_RESOLUTION = 0.1


class rrEstimation:
    def __init__(self, __signal: Roi2Signal, dst_dir, sampling_rate, window=False):
        self._signal = __signal.get_signal(window)
        self._time = __signal.get_times(window)
        self._dst_dir = dst_dir
        self._sampling_rate = sampling_rate

        self._dt = self._time[-1] - self._time[-2]
        self._N = len(self._time)
        self._frequency = np.linspace(0, 1.0 / self._dt, self._N)

        self._spectrum = 0

        # 分解能をあげるためにpaddingを設定
        self._n_padding = int(60*self._sampling_rate/FREQUENCY_RESOLUTION)

    def get_frequency(self):
        return self._frequency

    def get_spectrum(self):
        return self._spectrum

    def get_preprocessed_signal(self):
        return signal.detrend(self._signal)

    # TODO 周波数解析の他クラス化
    def calculate_FFT(self):
        preprocessed_signal = self.get_preprocessed_signal()
        self._frequency = np.linspace(0, 1.0 / self._dt, self._N)
        self._spectrum = np.abs(fft(preprocessed_signal) / (self._N / 2))

    def calculate_PSD(self):
        # TODO:PSDの前にナイキスト周波数以上の高周波を除去する必要あり?

        # preprocessed_signal = self.get_preprocessed_signal()
        self. _frequency, self._spectrum = signal.welch(self._signal, 1 / self._dt,
                                                        detrend='linear',
                                                        nfft=self._n_padding)

    def calculate_PSD_Welch(self, window='boxcar', per_seg=2, det='linear'):
        self._frequency, self._spectrum = signal.welch(self._signal, 1 / self._dt,
                                                       window=window, detrend=det,
                                                       nperseg=self._N // per_seg)

    def estimate_f_rr(self):
        lp_index = np.abs(self._frequency - LF_THRESH).argmin()
        hp_index = np.abs(self._frequency - HF_THRESH).argmin()

        # BP域最大スペクトルに対応する周波数を呼吸周波数とする
        rr_index = np.argmax(self._spectrum[lp_index:hp_index]) + lp_index

        return round(self._frequency[rr_index] * 60, 2)

    def estimate_t_rr(self, size=5, iteration=3):
        signalClass = Roi2Signal()
        preprocessed_signal = self.get_preprocessed_signal()
        signalClass.load_signals(self._time, preprocessed_signal)

        smoothed_signal = []
        # 平滑化
        for i in range(iteration):
            smoothed_signal = signalClass.apply_moving_average_filter(num=size, window=False)
            signalClass.load_signals(self._time, smoothed_signal)

        # zero-cross点の取得
        zero_cross_points = []
        for i in range(1, len(smoothed_signal)):
            if smoothed_signal[i - 1] * smoothed_signal[i] < 0:
                zero_cross_point = (self._time[i - 1] + self._time[i]) / 2
                zero_cross_points.append(zero_cross_point)

        # 呼吸周期候補の算出
        rr_candidate = []
        for i in range(1, len(zero_cross_points)):
            periodic_time = (zero_cross_points[i] - zero_cross_points[i - 1]) * 2
            rr = 60 / periodic_time
            # 算出されたrrがBP域の時のみ呼吸数の候補としてみなす
            if (rr > LF_THRESH * 60) and (rr < HF_THRESH * 60):
                rr_candidate.append(rr)

        # 呼吸数の算出
        # 0.1Hz~2Hzの場合のzero-cross点の数と合わない場合，エラー判定
        t_window = len(self._time)/self._sampling_rate
        if (int(LF_THRESH * t_window * 2 + 0.5) < len(rr_candidate)) and (len(rr_candidate) < int(HF_THRESH * t_window * 2 + 0.5)):
            rr = statistics.median(rr_candidate)
        else:
            rr = OUTLIER

        print("t_rr :", rr)
        return rr














