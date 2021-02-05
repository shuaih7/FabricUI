import time
from model import CudaModel
from model.utils import draw_bbox_image
from matplotlib import pyplot as plt


if __name__ == "__main__":
    
    img_file = r"E:\Projects\Fabric_Defect_Detection\model_dev\v1.1.0\dataset\valid\MER2-041-436U3M(FDL17100010)_2020-12-02_19_35_11_980-1.bmp"
    cfg = {"offsets": [0,0,0,0], "input_h": 352, "input_w": 352}
    
    model = CudaModel(cfg)
    origin, results = model(img_file)
    
    boxes = results['boxes']
    labels = results['labels']
    scores = results['scores']
    
    start = time.time()
    image = draw_bbox_image(origin, boxes, labels, scores)
    end = time.time()
    print("The drawing time is", end-start)
    plt.imshow(image), plt.show()