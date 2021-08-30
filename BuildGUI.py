import numpy as np
import os
from PIL import Image
import cvui
from UtilProcess import convert_tiff2numpy, convert16to8bit, resize_square
import cv2

from UtilsGUI import DisplayClock
from SignalProcess import Roi2Signal
from ImageProcess import ImageProcess
from rrEstimation import rrEstimation
from timeit import default_timer as timer
from rqiCalculation import rqiCalculation
from yoloV3.detect import YOLO
from GLOBAL import *
from flirpy.camera.boson import Boson


WINDOW_NAME = "RespThermal"
time_for_analysis = 15

cycle = 60/RR

dt = cycle/8


class PositionInGUI:
    def __init__(self, x, y, width=0, height=0, size=0.0):
        self.x = x
        self.y = y
        self.w = width
        self.h = height
        self.size = size


def EstimateRespiratoryRate(yolo):
    camera = Boson()

    # GUI上のパーツのPositionを定義
    p_fps_text = PositionInGUI(90, 15)
    p_detection_frame = PositionInGUI(40, 60)
    p_start_button = PositionInGUI(10, 10)
    p_rr_text = PositionInGUI(80, 20, 0, 0, 0.7)

    # cvuiの初期化
    window_frame = np.zeros((400, 500, 3), np.uint8)
    cvui.init(WINDOW_NAME)

    is_on = False
    accum_time = 0
    curr_fps = 0
    fps = "FPS: ??"
    rr_text = "Resp. rate = ??"
    mouse_rr_text = "Resp. rate = ??"
    prev_time = timer()

    respiration_count = 0

    # init Signal class for each grid　
    signals_for_each_grid = []
    for i in range(NUM_WIDTH * NUM_HEIGHT):
        signals_for_each_grid.append(Roi2Signal())

    # init ImageProcess class
    image_process_class = ImageProcess(dst_dir=None)

    estimated_rrs = []

    while True:
        window_frame[:] = (49, 52, 49)  # フレームの色を指定(BGR)

        if cvui.button(window_frame, p_start_button.x, p_start_button.y, "Start"):
            # ON/OFFを切り替える
            is_on = not is_on
            start_time = timer()

        # ボタンが押されたら、鼻の検出を開始
        if is_on:
            curr_time = timer()
            exec_time = curr_time - prev_time
            prev_time = curr_time
            accum_time = accum_time + exec_time
            curr_fps = curr_fps + 1
            if accum_time > 1:
                accum_time = accum_time - 1
                fps = curr_fps
                curr_fps = 0

            if curr_time-start_time > 60:
                break

            if curr_time-start_time > cycle * respiration_count:
                respiration_count = respiration_count + 1

            # preprocess image
            u16_image = camera.grab(0)
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

            time = curr_time-start_time

            # calculate signal intensity for each grid
            for j in range(NUM_WIDTH * NUM_HEIGHT):
                image_process_class.load(u16_resized_image, u8_resized_image,
                                         detection_image, block_boxes[j])
                signals_for_each_grid[j].append_signal(time, image_process_class.get_signal_intensity())

            # 一定時間(15s)以上信号がたまったら，呼吸数を計算
            signal_size = signals_for_each_grid[0].get_size()
            window_size = int(fps*time_for_analysis)
            if fps > 7 and signal_size > window_size:
                f_rrs = []
                t_rrs = []
                rqis = []
                d_rrs = []
                for i in range(NUM_WIDTH * NUM_HEIGHT):
                    respClass = rrEstimation(signals_for_each_grid[i], dst_dir=None,
                                             sampling_rate=fps, window=False)
                    respClass.calculate_PSD()

                    f_rrs.append(respClass.estimate_f_rr())
                    t_rrs.append(respClass.estimate_t_rr(size=MV_SIZE, iteration=MV_ITER))
                    d_rrs.append(OUTLIER if t_rrs[-1] == OUTLIER
                                 else abs(t_rrs[-1] - f_rrs[-1]))
                    rqiClass = rqiCalculation(respClass, RQI_PARAM, d_rrs[-1], PENALTY_ID)
                    rqis.append(rqiClass.get_rqi(rqi_id=RQI_ID))

                # select grid and rr
                estimated_place = rqis.index(max(rqis))
                estimated_rr = f_rrs[estimated_place]

                if signal_size % 18 == 0:
                    rr_text = "Resp. rate = " + str(round(estimated_rr)) + " bpm"
                    estimated_rrs.append(estimated_rr)

            cvui.text(window_frame, p_fps_text.x, p_fps_text.y, "FPS:" + str(fps), p_fps_text.size)
            cvui.image(window_frame, p_detection_frame.x, p_detection_frame.y, detection_image)
            cvui.text(window_frame, p_rr_text.x, p_rr_text.y, rr_text, p_rr_text.size)

        cvui.imshow(WINDOW_NAME, window_frame)

        if cv2.waitKey(20) == 27:
            break


if __name__ == '__main__':
    EstimateRespiratoryRate(YOLO(**FLAGS))

