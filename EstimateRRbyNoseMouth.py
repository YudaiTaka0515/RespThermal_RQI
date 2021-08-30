import numpy as np
import os
from PIL import Image
from glob import glob
from LoadInputData import load_input_data
from UtilProcess import convert_tiff2numpy, convert16to8bit, resize_square
from SignalProcess import Roi2Signal
from ImageProcess import ImageProcess
from rrEstimation import rrEstimation
from rqiCalculation import rqiCalculation
from yoloV3.detect import YOLO
from GLOBAL import *


def estimateRR_usingNM(_src_dir, _dst_dir, yolo):
    # load dataset info
    _gt_rr, thermal_fps, _ = load_input_data(os.path.join(_src_dir, "info.txt"))

    # init ImageProcess class
    nose_roi = ImageProcess(dst_dir=_dst_dir)
    mouth_roi = ImageProcess(dst_dir=_dst_dir)

    # init SignalClass
    nose_signal = Roi2Signal()
    mouth_signal = Roi2Signal()

    # load thermal image(16bit)
    u16_images = convert_tiff2numpy(os.path.join(_src_dir, "video.tiff"))

    # -----------------------------------------------
    # calculate signal intensity
    for i, u16_image in enumerate(u16_images):
        # preprocess image
        u16_image = np.stack([u16_image, u16_image, u16_image], axis=-1)
        u8_image = convert16to8bit(u16_image)
        u16_resized_image = resize_square(u16_image)
        u8_resized_image = resize_square(u8_image)

        # detect nose and mouth by YOLO v3
        detection_result, nose_box, mouth_box, face_box = yolo.detect_fromConf(Image.fromarray(u8_resized_image))

        detection_image = np.asarray(detection_result)

        time = i/thermal_fps

        # calculate signal intensity for each grid
        nose_roi.load(u16_resized_image, u8_resized_image, detection_image, nose_box)
        mouth_roi.load(u16_resized_image, u8_resized_image, detection_image, mouth_box)

        nose_signal.append_signal(time, nose_roi.get_signal_intensity())
        mouth_signal.append_signal(time, mouth_roi.get_signal_intensity())

    # -----------------------------------------------
    # estimate Respiratory Rate
    # estimate RR in time domain, and frequency domain
    # estimate rqis
    resp_nose = rrEstimation(nose_signal, dst_dir=_dst_dir, sampling_rate=thermal_fps, window=False)
    resp_mouth = rrEstimation(mouth_signal, dst_dir=_dst_dir, sampling_rate=thermal_fps, window=False)
    _nose_rr = resp_nose.estimate_f_rr()
    _mouth_rr = resp_mouth.estimate_f_rr()

    return _gt_rr, _nose_rr, _mouth_rr


if __name__ == '__main__':
    _yolo = YOLO(**FLAGS)
    results = []
    src_dirs = glob(SRC_DIRS)
    i = 0
    for src_dir in src_dirs:
        base_name = os.path.basename(src_dir)
        dst_dir = os.path.join(DST_DIRS, base_name)
        # print(base_name)
        if not os.path.exists(dst_dir):
            os.mkdir(dst_dir)

        gt_rr, nose_rr, mouth_rr = estimateRR_usingNM(src_dir, dst_dir, _yolo)
        abs_error = np.round(abs(gt_rr - rr), 2)
        results.append([base_name, gt_rr, rr, index, abs_error])
        i += 1

    print("base_name, GT, rr, index, AE")
    AEs = []
    for result in results:
        print(result[0], result[1], result[2], result[3], result[4])
        AEs.append(result[4])








































