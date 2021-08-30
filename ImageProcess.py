import numpy as np
import cv2
import os


class ImageProcess:
    def __init__(self, dst_dir):
        self.__u16_images = []
        self.__u8_images = []
        self.__detection_images = []
        self.__mask_images = []

        self.__boxes = []
        self.__dst_dir = dst_dir
        # TODO リアルタイム推定の時などに使えるように可変にする
        self.__frame_rate = 8.6

    def load(self, image_u16, image_u8, detection_result, box):
        self.__u16_images.append(image_u16)
        self.__u8_images.append(image_u8)
        self.__detection_images.append(detection_result)
        self.__boxes.append(box)

    def extract_region(self, top, left, bottom, right):
        interest_region = self.__u8_images[-1][top:bottom, left:right, :]
        ret, mask = cv2.threshold(interest_region[:, :, 0], 0, 255, cv2.THRESH_OTSU)
        mask = cv2.bitwise_not(mask)
        return mask

    def get_signal_intensity(self):
        if np.all(self.__boxes[-1] == 0):
            raise Exception("検出が正常に行われませんでした")
        mouse_box = self.__boxes[-1]
        top, left, bottom, right = np.array([int(mouse_box[i])
                                             for i in range(mouse_box.shape[0])])

        interest_region = self.__u16_images[-1][top:bottom, left:right, :]
        intensity = np.mean(interest_region)
        # mask = self.extract_region(top, left, bottom, right)
        # interest_region = interest_region[:, :, 0] * mask
        # intensity = np.sum(interest_region) / np.count_nonzero(interest_region > 0)

        return intensity

    def save_detection_result(self, file_path):
        output_path = os.path.join(self.__dst_dir, file_path)
        print(output_path)
        size = (self.__detection_images[0].shape[1], self.__detection_images[0].shape[0])

        fmt = cv2.VideoWriter_fourcc('m', 'p', '4', 'v')
        writer = cv2.VideoWriter(output_path, fmt, self.__frame_rate, size)  # ライター作成
        for frame in self.__detection_images:
            writer.write(frame)  # 画像を1フレーム分として書き込み
        # ファイルを閉じる
        writer.release()





