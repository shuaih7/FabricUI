import os
import sys
import cv2
import time
from PyQt5.QtCore import QThread


def write_image(image, save_dir):
    index = 0
    
    for i in range(10):
        save_name = os.path.join(save_dir, str(i)+'.png')
        cv2.imwrite(save_name, image)
        index += 1
    print('Done')
    
    
class Writer(QThread):
    def __init__(self, image, save_dir, parent=None):
        super(Writer, self).__init__(parent)
        self.image = image
        self.save_dir = save_dir
    
    def run(self):
        for i in range(10):
            save_name = os.path.join(self.save_dir, str(i)+'.png')
            cv2.imwrite(save_name, self.image)
        print('Done')
        
        
if __name__ == '__main__':
    img_file = r'E:\Projects\Fabric_Defect_Detection\model_dev\v1.1.0\dataset\train\MER2-041-436U3M(FDL17100010)_2020-12-02_19_38_12_050-0.bmp'
    save_dir = r''
    image = cv2.imread(img_file, -1)
    writer = Writer(image, save_dir)
    
    start = time.time()
    index = 0
    write_image(image, save_dir)
    #writer.run()
    for i in range(200000):
        index += 1
    end = time.time()
    print('The total time is', end-start, 'seconds.')
