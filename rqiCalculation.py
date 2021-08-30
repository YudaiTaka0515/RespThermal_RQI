from rrEstimation import rrEstimation
import numpy as np
from NonlinearFunction import sigmoid, arc_tan, step, tanh_01
from GLOBAL import *


class rqiCalculation:
    def __init__(self, rr_class: rrEstimation, a, d_rr, penalty_id=0):
        self._frequency = rr_class.get_frequency()
        self._spectrum = rr_class.get_spectrum()
        self.lp_index = np.abs(self._frequency - LF_THRESH).argmin()
        self.hp_index = np.abs(self._frequency - HF_THRESH).argmin()

        self._bp_spectrum = self._spectrum[self.lp_index:self.hp_index]
        self._hp_spectrum = self._spectrum[self.hp_index:]
        self.d_rr = d_rr

        if penalty_id == 0:
            self._penalty = sigmoid(a - d_rr)
        elif penalty_id == 1:
            self._penalty = tanh_01(a - d_rr)
        elif penalty_id == 2:
            self._penalty = step(a - d_rr)
        elif penalty_id == 3:
            self._penalty = arc_tan(a-d_rr)
        else:
            raise Exception("penalty関数の設定に誤りがあります")

    def get_rqi(self, rqi_id):
        if rqi_id == 0:
            return self.calculate_sqi()
        elif rqi_id == 1:
            return self.calculate_rqi1(ratio_bp=RATIO_BF)
        elif rqi_id == 2:
            return self.calculate_rqi2(ratio_bp=RATIO_BF)
        elif rqi_id == 3:
            return self.calculate_rqi3(ratio_bp=RATIO_BF, ration_hp=RATIO_HF)
        elif rqi_id == 4:
            return self.calculate_rqi4(ratio_bp=RATIO_BF, ratio_hp=RATIO_HF)
        elif rqi_id == 5:
            return self.calculate_rqi5()
        elif rqi_id == 6:
            return self.calculate_best_rqi(ratio_bp=RATIO_BF, ratio_hp=RATIO_HF)
        else:
            raise Exception("存在しないRQIが指定されました")

    def calculate_rqi1(self, ratio_bp=RATIO_BF):
        # バンド帯に存在する大きいスペクトルに着目
        Fbp = np.sum(self._bp_spectrum > np.max(self._bp_spectrum) * ratio_bp) / len(self._bp_spectrum)

        # 高周波領域のノイズに着目
        Fhp = np.mean(self._hp_spectrum) / np.max(self._hp_spectrum)

        return np.round(1 - Fbp - Fhp, 2)

    def calculate_rqi2(self, ratio_bp=RATIO_BF):
        # バンド帯に存在する大きいスペクトルに着目
        Fbp = np.sum(self._bp_spectrum > np.max(self._bp_spectrum) * ratio_bp) / len(self._bp_spectrum)

        # 高周波領域のノイズに着目
        Fhp = np.mean(self._hp_spectrum) / np.max(self._hp_spectrum)

        rqi = np.max(self._bp_spectrum) * np.round(1 - Fbp - Fhp, 2)

        return rqi

    def calculate_rqi3(self, ratio_bp=RATIO_BF, ration_hp=RATIO_HF):

        # バンド帯に存在する大きいスペクトルに着目
        Fbp = np.sum(self._bp_spectrum > np.max(self._bp_spectrum) * ratio_bp) / len(self._bp_spectrum)

        # 高周波領域のノイズに着目
        Fhp = np.sum(self._hp_spectrum > np.max(self._hp_spectrum) * ration_hp) / len(self._hp_spectrum)

        return np.round(1 - Fbp - Fhp, 2)

    # 専門ゼミのSQIを再現
    def calculate_sqi(self):
        max_spectrum = np.max(self._spectrum)

        F1 = np.max(self._spectrum[self.hp_index:]) / max_spectrum
        F2 = np.sum(self._spectrum[self.hp_index:] > max_spectrum * 0.1) / len(self._spectrum[index_2Hz:])
        F3 = (np.max(self._spectrum[:self.lp_index]) -
              np.max(self._spectrum[self.lp_index:self.hp_index]))
        F3 /= max_spectrum
        F4 = (np.max(self._spectrum[:self.lp_index]) / np.max(self._spectrum[self.lp_index:self.hp_index]))

        if F4 > 2:
            sqi = 1 - (F3 / 2 + (F1 + F2) / 4)
        else:
            sqi = 1 - (F1 + F2) / 2

        return sqi

    def calculate_rqi4(self, ratio_bp=RATIO_BF, ratio_hp=RATIO_HF):
        # バンド帯に存在する大きいスペクトルに着目
        Fbp = np.sum(self._bp_spectrum > np.max(self._bp_spectrum) * ratio_bp) / len(self._bp_spectrum)

        # 高周波領域のノイズに着目
        Fhp = np.sum(self._hp_spectrum > np.max(self._hp_spectrum) * ratio_hp) / len(self._hp_spectrum)

        return np.round(1 - (Fbp + Fhp)/2, 2)

    def calculate_best_rqi(self, ratio_bp=RATIO_BF, ratio_hp=RATIO_HF):
        # バンド帯に存在する大きいスペクトルに着目
        Fbp = np.sum(self._bp_spectrum > np.max(self._bp_spectrum) * ratio_bp) / len(self._bp_spectrum)
        # 高周波領域のノイズに着目
        Fhp = np.sum(self._hp_spectrum > np.max(self._hp_spectrum) * ratio_hp) / len(self._hp_spectrum)

        return self._penalty * np.round(1 - (Fbp + Fhp) / 2, 2)

    def calculate_rqi5(self, ration_bp=RATIO_BF, ration_hp=RATIO_HF):
        return np.max(self._bp_spectrum)







