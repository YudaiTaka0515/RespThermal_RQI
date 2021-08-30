# in rrEstimation
LF_THRESH = 0.10
HF_THRESH = 2

RATIO_BF = 0.25
RATIO_HF = 0.1

# -------------------------------------------
# in EstimateRRbyFaceRQI
RQI_ID = 6
PENALTY_ID = 1
NUM_WIDTH, NUM_HEIGHT = 4, 6
MV_SIZE, MV_ITER = 5, 3
OUTLIER = 100
RQI_PARAM = 5
FLAGS = {'image': False, 'input': './path2your_video', 'output': ''}
SRC_DIRS = r"I:\3.Data\RespData\yolo_src2\*"
DST_DIRS = r"I:\3.Data\RespData\yolo_dst_sqi3"

# --------------------------------------------
# in YOLOv3
CLASS_NAMES = ["face", "mouth", "nose"]
CLASS_COLORS = {"face": (255, 0, 0), "mouth": (0, 255, 0), "nose": (0, 0, 255)}
MODEL_PATH = r"weights/weights.h5"
ANCHORS_PATH = r'model_data/yolo_anchors.txt'
CLASSES_PATH = r"model_data/classes.txt"
SCORE = 0.25
IOU = 0.45
MODEL_SIZE_IMAGE = (320, 320)
GPU_NUM = 1





