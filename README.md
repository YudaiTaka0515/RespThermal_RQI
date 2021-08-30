
# What is RespThermal : 
- [Estimation of Respiratory Rate from Thermography Using Respiratory Likelihood Index(Sensors)](https://www.mdpi.com/1424-8220/21/13/4406)
- サーモグラフィ画像から呼吸数を推定するシステム
    - 顔領域から呼吸数を推定 : ```EstimateRRbyFaceRQI.py```
    - 口・鼻領域から呼吸数を推定(Respiratory Quality Index) : ```EstimateRRbyNoseMouth.py```

- ```GLOBAL.py```でパラメタを管理. 適宜変更してください. 
- 重み```weights.weights.h5```は共有ファイルからダウンロードしてください.
# Environment : 
- 基本的には[keras-yolov3](https://github.com/qqwweee/keras-yolo3) が動く環境がベース. 自分はanacondaで環境構築.
- その他細かいライブラリはrequirement.yamlを参照. ただ別プロジェクト用のパッケージも入ってるのであしからず．
    - サーモグラフィ用ライブラリ : ```pip install flirpy```


# Demonstration : 
- サーモグラフィカメラはBoson320を使用
- リアルタイム推論モード : ```BuildGUI.py```

![RespCompress2](https://user-images.githubusercontent.com/65318542/131355387-3ffcab52-21b5-43e2-8fdc-89e42d60ec2d.gif)


