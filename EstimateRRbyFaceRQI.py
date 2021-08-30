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


def estimateRR_usingRQI(_src_dir, _dst_dir, yolo):
    # load dataset info
    _gt_rr, thermal_fps, _ = load_input_data(os.path.join(_src_dir, "info.txt"))

    # init Signal class for each grid　
    signals_for_each_grid = []
    for i in range(NUM_WIDTH*NUM_HEIGHT):
        signals_for_each_grid.append(Roi2Signal())

    # init ImageProcess class
    image_process_class = ImageProcess(dst_dir=_dst_dir)

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

        # detect face by YOLO v3
        detection_result, face_box = yolo.detect_face(Image.fromarray(u8_resized_image),
                                                      display_score=False)
        detection_image = np.asarray(detection_result)

        # calculate ROI
        face_height, face_width = (face_box[2] - face_box[0], face_box[3] - face_box[1])
        grid_height, grid_width = face_height // NUM_HEIGHT, face_width // NUM_WIDTH

        # define each grid
        block_boxes = []
        for j in range(NUM_HEIGHT):
            for k in range(NUM_WIDTH):
                top, left = (grid_height * j + face_box[0], grid_width * k + face_box[1])
                bottom, right = (grid_height + top, grid_width + left)
                block_boxes.append(np.array([top, left, bottom, right]))

        time = i/thermal_fps

        # calculate signal intensity for each grid
        for j in range(NUM_WIDTH * NUM_HEIGHT):
            image_process_class.load(u16_resized_image, u8_resized_image,
                                     detection_image, block_boxes[j])
            signals_for_each_grid[j].append_signal(time, image_process_class.get_signal_intensity())

    # -----------------------------------------------
    # estimate Respiratory Rate
    f_rrs = []
    t_rrs = []
    rqis = []
    d_rrs = []
    # estimate RR in time domain, and frequency domain
    # estimate rqis
    for i in range(NUM_WIDTH*NUM_HEIGHT):
        respClass = rrEstimation(signals_for_each_grid[i], dst_dir=_dst_dir,
                                 sampling_rate=thermal_fps, window=False)
        respClass.calculate_PSD()

        f_rrs.append(respClass.estimate_f_rr())
        t_rrs.append(respClass.estimate_t_rr(size=MV_SIZE, iteration=MV_ITER))
        d_rrs.append(OUTLIER if t_rrs[-1] == OUTLIER
                     else abs(t_rrs[-1]-f_rrs[-1]))
        rqiClass = rqiCalculation(respClass, RQI_PARAM, d_rrs[-1], PENALTY_ID)
        rqis.append(rqiClass.get_rqi(rqi_id=RQI_ID))

    # select grid and rr
    estimated_place = rqis.index(max(rqis))
    print(estimated_place)
    estimated_rr = f_rrs[estimated_place]

    print(os.path.basename(_dst_dir), _gt_rr, estimated_rr)
    # ----------------------------------------------------------------
    # save result

    return _gt_rr, estimated_rr, estimated_place


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

        gt_rr, rr, index = estimateRR_usingRQI(src_dir, dst_dir, _yolo)
        abs_error = np.round(abs(gt_rr - rr), 2)
        results.append([base_name, gt_rr, rr, index, abs_error])
        i += 1

    print("base_name, GT, rr, index, AE")
    AEs = []
    for result in results:
        print(result[0], result[1], result[2], result[3], result[4])
        AEs.append(result[4])








































