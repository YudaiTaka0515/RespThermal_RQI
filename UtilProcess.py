import tifffile
import numpy as np
import cv2


def convert_tiff2numpy(_src_path):
    """[frame, height, width]の形であることに注意"""
    np_images = tifffile.imread(_src_path)
    # print(np_images.shape)
    # print(np_images.dtype)

    return np_images


def convert16to8bit(images_u16):
    maxV, minV = np.amax(images_u16), np.amin(images_u16)
    # maxV, minV = (60000, 50000)
    # print(maxV, minV)
    alpha = 255.0 / (maxV - minV)
    images_u8 = np.add(images_u16, -minV)
    images_u8 = images_u8 * alpha
    images_u8 = images_u8.astype(np.uint8)
    return images_u8


def resize_square(img, size=(320, 320)):
    height, width, _ = img.shape
    if height < width:
        margin = (width-height) // 2
        reshaped_img = img[:, margin:-margin, :]
    else:
        margin = (height - width) // 2
        reshaped_img = img[margin:-margin, :, :]

    reshaped_img = cv2.resize(reshaped_img, dsize=size)

    return reshaped_img
