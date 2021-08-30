import numpy as np


def load_input_data(path):
    """
    実験データの読み込み
    :param path: ぱす
    :return: RR(Ground Truth), サーモグラフィのfps, Bitalinoのfps
    """
    gt_rr = None
    thermal_fps = None
    bitalino_fps = None

    with open(path, 'r') as f:
        s = f.read()
        split_sentence = s.split('\n')
    for i in range(len(split_sentence)):
        temp = split_sentence[i].split('=')
        if len(temp) < 2:
            continue
        if temp[0] in 'estimated fps':
            thermal_fps = float(temp[1])
        elif temp[0] in 'revised_RR':
            gt_rr = float(temp[1])
        elif temp[0] in 'Sampling Rate':
            bitalino_fps = float(temp[1])

    if (gt_rr is None) or (thermal_fps is None) or (bitalino_fps is None):
        raise Exception("入力データセットが異なります")

    else:
        return gt_rr, thermal_fps, bitalino_fps


def load_signals_fromCSV(csv_path):
    csv_list = []
    with open(csv_path, 'r') as f:
        line = f.readline()
        while line:
            if not line == '\n':
                csv_list.append(line.replace('\n', ''))
            line = f.readline()

    times = np.zeros(len(csv_list))
    signals = np.zeros(len(csv_list))

    for i in range(len(csv_list)):
        split_csv = csv_list[i].split(',')
        times[i] = split_csv[0]
        signals[i] = split_csv[1]

    return times, signals






