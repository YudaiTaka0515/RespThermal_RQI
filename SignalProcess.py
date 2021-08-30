import numpy as np
from GLOBAL import *


class Roi2Signal:
    def __init__(self):
        self._times = []
        self._signals = []

    def append_signal(self, time, signal):
        """
        Detection結果から算出された信号強度を保存
        (Detection失敗により)信号強度が算出されなかった場合, 0-paddingするか前回の信号強度を参照
        :param time: 時間
        :param signal: 信号強度
        :return: None
        """
        if len(self._times) == 0:
            self._signals.append(signal if signal is not None else 0)
        else:
            self._signals.append(signal if signal is not None
                                 else self._signals[-1])

        self._times.append(time)

    def get_size(self):
        return len(self._times)

    def load_signals(self, times, signals):
        """
        時系列の信号を読み込み
        :param times: 時間データ
        :param signals: 信号強度データ
        :return: None
        """
        self._times = times
        self._signals = signals

    def get_times(self, window=False):
        """
        時間データをNumpyに変換してreturn
        window=Falseの時すべてreturn, window=intの時窓の長さ分return
        :param window: 窓の長さ
        :return: 時間データ(Numpy)
        """
        if window:
            return np.array(self._times[-window:])
        else:
            return np.array(self._times)

    def get_signal(self, window=False):
        """
        信号データをNumpyに変換してreturn
        window=Falseの時すべてreturn, window=intの時窓の長さ分return
        :param window: 窓の長さ
        :return: 信号データ
        """
        if window:
            return np.array(self._signals[-window:])
        else:
            return np.array(self._signals)

    def apply_moving_average_filter(self, num=5, window=False):
        """
        移動平均
        :param num:移動平均
        :param window: 窓の長さ
        :return: 平滑化された信号
        """
        b = np.ones(num)/float(num)

        if window:
            windowed_signals = np.array(self._signals[-window:])
        else:
            windowed_signals = np.array(self._signals)
        filtered_signals = np.convolve(windowed_signals, b, mode="same")

        return filtered_signals
