import numpy as np
import cv2
from matplotlib import pyplot as plt

# 首先以灰色读取一张照片
src = cv2.imread(r"E:\Projects\Fabric_Defect_Detection\model_proto\ShuffleNetV2_YOLOv3\v1.1\dataset\valid\valid_gray_1_1600.png", 0)
# 然后用ctvcolor（）函数，进行图像变换。
src_RGB = cv2.cvtColor(src, cv2.COLOR_GRAY2BGR)

print(sum(sum(src_RGB[:,:,0]-src_RGB[:,:,1])))
print(sum(sum(src_RGB[:,:,1]-src_RGB[:,:,2])))
print(sum(sum(src_RGB[:,:,0]-src_RGB[:,:,2])))

plt.imshow(src_RGB)
plt.show()
