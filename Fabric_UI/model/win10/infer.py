#!/usr/bin/python
# -*- coding: utf-8 -*-

'''
Created on 11.21.2020
Updated on 11.21.2020

Author: haoshaui@handaotech.com
'''

import os, cv2, time
import numpy as np
import paddle.fluid as fluid
from PIL import Image
from PIL import ImageDraw

place = fluid.CUDAPlace(0) # Use CUDAPlace as default
exe = fluid.Executor(place)
path = r"E:\Projects\Fabric_Defect_Detection\model_proto\MobileNet_YOLO\Fast_YOLO\freeze_model" 
[inference_program, feed_target_names, fetch_targets] = fluid.io.load_inference_model(dirname=path, executor=exe, model_filename='__model__', params_filename='params')


def draw_bbox_image(img, boxes, scores, gt=False):
    '''
    给图片画上外接矩形框
    :param img:
    :param boxes:
    :param save_name:
    :param labels
    :return:
    '''
    color = ['red', 'blue']
    if gt:
        c = color[1]
    else:
        c = color[0]
    img = Image.fromarray(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
    draw = ImageDraw.Draw(img)
    for box, score in zip(boxes, scores):
        xmin, ymin, xmax, ymax = box[0], box[1], box[2], box[3]
        draw.rectangle((xmin, ymin, xmax, ymax), None, c, width=3)
        draw.text((xmin, ymin), str(score), (255, 255, 0))
    return img
    

def resize_img(img, target_size):
    """
    保持比例的缩放图片
    :param img:
    :param target_size:
    :return:
    """
    h, w = target_size
    img = cv2.resize(img, (w, h), interpolation = cv2.INTER_LINEAR)

    return img


def read_image(img, input_size): # image is an numpy array
    """
    读取图片
    :param img_path:
    :return:
    """
    origin = img
    img = resize_img(origin, input_size)
    resized_img = img.copy()
    img = np.array(img).astype('float32').transpose((2, 0, 1))  # HWC to CHW
    img -= 127.5
    img *= 0.007843
    img = img[np.newaxis, :]
    return origin, img, resized_img
    
    
class inferModel(object):
    def __init__(self, config_matrix, logger):
        self.config_matrix = config_matrix
        self.logger = logger
        
        self.input_resolution_yolov3_HW = (config_matrix["Model"]["input_h"], config_matrix["Model"]["input_w"])
        self.preprocessor = read_image
        
    def infer(self, image): # image is an numpy array
        origin, tensor_img, resized_img = self.preprocessor(image, self.input_resolution_yolov3_HW)
        input_w, input_h = origin.shape[:2]
        image_shape = np.array([input_h, input_w], dtype='int32')
        
        batch_outputs = exe.run(inference_program,
                                feed={feed_target_names[0]: tensor_img,
                                      feed_target_names[1]: image_shape[np.newaxis, :]},
                                fetch_list=fetch_targets,
                                return_numpy=False)
        bboxes = np.array(batch_outputs[0])
        #print(bboxes)
        if bboxes.shape[1] != 6:
            # print("No object found")
            return [], [], []
        labels = bboxes[:, 0].astype('int32')
        scores = bboxes[:, 1].astype('float32')
        boxes = bboxes[:, 2:].astype('float32')
        return boxes, labels, scores


if __name__ == '__main__':
    import sys
    import glob as gb
    """
    image_path = r'E:\Projects\Fabric_Defect_Detection\model_proto\ShuffleNetV2_YOLOv3\v1.1\dataset\valid'
    label_path = r'E:\Projects\Fabric_Defect_Detection\model_proto\ShuffleNetV2_YOLOv3\v1.1\dataset\valid'
    save_path  = r"E:\Projects\Fabric_Defect_Detection\model_proto\MobileNet_YOLO\Fast_YOLO\valid_output"
    image_list = gb.glob(image_path + r"/*.png")
    total_time = 0.
    
    pvoc = PascalVocXmlParser()
    
    for image_file in image_list:
        img = cv2.imread(image_file)
        _, filename = os.path.split(image_file)
        fname, _ = os.path.splitext(filename)
        save_name = os.path.join(save_path, filename)
        #label_file = os.path.join(label_path, fname+".xml")
        
        flag, box, label, scores, bboxes, period = infer(img)
        total_time += period
        
        if flag:
            img = draw_bbox_image(img, box, scores)
            img = cv2.cvtColor(np.asarray(img), cv2.COLOR_RGB2BGR)
            print('Defect detected at image', image_file)
            cv2.imwrite(save_name, img)
        else:
            print(image_path, "No defect detected.")
            shutil.copy(image_file, save_name)
        #print('infer one picture cost {} ms'.format(period))
        
    average_time = total_time / len(image_list)
    fps = int(1000/average_time)
    print("The avergae processing time for one image is", average_time)
    print("The fps is", fps)
    """
    
    # Check the result of a single image
    image_file = r"E:\Projects\Fabric_Defect_Detection\model_proto\ShuffleNetV2_YOLOv3\v1.1\dataset\valid\valid_gray_1_1600.png"
    img = cv2.imread(image_file)
    flag, box, label, scores, bboxes, period = infer(img)
    print("The boxes are", box)
    print("The scores are", scores)
    