import cv2
import time
import numpy as np
from PIL import Image
from model import CudaModel
from matplotlib import pyplot as plt


if __name__ == "__main__":
    
    img_file = r"E:\Projects\Fabric_Defect_Detection\model_dev\v1.1.0\dataset\valid\MER2-041-436U3M(FDL17100010)_2020-12-02_19_35_11_980-1.bmp"
    '''
    cfg = {"offsets": [0,0,0,0], "input_h": 352, "input_w": 352}
    
    model = CudaModel(cfg)
    origin, results = model(img_file)
    
    boxes = results['boxes']
    labels = results['labels']
    scores = results['scores']
    '''
    
    image = cv2.imread(img_file)
    
    image_resized = Image.fromarray(image)
    image_resized = image_resized.resize((352,352), resample=Image.BILINEAR)
    image_resized = np.array(image_resized, dtype=np.float32)
    
    print(image.shape)
    print(image_resized.shape)