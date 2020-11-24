import numpy as np
import cv2, os, sys, json
from PIL import Image
from matplotlib import pyplot as plt

# 首先以灰色读取一张照片
img_path = r"E:\Projects\Fabric_Defect_Detection\model_proto\ShuffleNetV2_YOLOv3\v1.1\dataset\valid\valid_gray_1_1600.png"
"""
src = cv2.imread(img_path, 0)
# 然后用ctvcolor（）函数，进行图像变换。
src_RGB = cv2.cvtColor(src, cv2.COLOR_GRAY2BGR)
"""

# src = Image.open(img_path)
# src_RGB = src.convert("RGB")
# plt.imshow(src_RGB)
# plt.show()

# src_RGB = np.array(src_RGB)
# print(sum(sum(src_RGB[:,:,0]-src_RGB[:,:,1])))
# print(sum(sum(src_RGB[:,:,1]-src_RGB[:,:,2])))
# print(sum(sum(src_RGB[:,:,0]-src_RGB[:,:,2])))

json_file = os.path.join(os.path.abspath(os.path.dirname(__file__)), "config.json")
#with open (config_file, "r") as f: 
#    self.config_matrix = json.load(f)

js_obj = {
    "Camera": {
        "DeviceSerialNumber": "NR0190090349",
        "ExposureTime": 1000,
        "Gain": 20,
        "Binning": 4
    },

    "Lighting": {
	
    },

    "Model": {
        "offsets": [0, 0, 0, 0],
        "image_raw_h": 352,
        "image_raw_w": 352,
        "input_h": 352,
        "input_w": 352,
        "channel": 3,
        "yolo_anchors": [(188,15), (351,16), (351,30)],
        "yolo_masks": [(0, 1, 2)],
        "output_shapes": [(1, 18, 11, 11)],
        "obj_threshold": 0.5,
        "nms_threshold": 0.2
    },

    "valid_dir": r"E:\Projects\Fabric_Defect_Detection\model_proto\ShuffleNetV2_YOLOv3\v1.1\dataset\valid",
    "valid_suffix": ".png"
}


with open(json_file, "w", encoding="utf-8") as ff:
    res = json.dumps(js_obj, indent=4)
    ff.write(res)
    ff.close()




