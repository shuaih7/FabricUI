#!/usr/bin/python
# -*- coding: utf-8 -*-

'''
Created on 11.20.2020
Updated on 02.01.2021

Author: haoshaui@handaotech.com
'''

import os
import sys

abs_path = os.path.abspath(os.path.dirname(__file__))
sys.path.append(os.path.abspath(os.path.join(abs_path, "..")))
sys.path.append(abs_path)

import cv2
import numpy as np
import paddle.fluid as fluid
from base_model import BaseModel
from utils import crop_image, normalize_image, map_boxes, draw_bbox_image


class CudaModel(BaseModel):
    def __init__(self, config_matrix, messager):
        super(CudaModel, self).__init__(config_matrix=config_matrix, messager=messager)
        place = fluid.CUDAPlace(0) # Use CUDAPlace as default
        self.exe = fluid.Executor(place)
        model_path = os.path.join(abs_path, "freeze")
        [self.inference_program, self.feed_target_names, self.fetch_targets] = fluid.io.load_inference_model(dirname=model_path, executor=self.exe, model_filename='__model__', params_filename='params')
        
    def preprocess(self, image):
        offsets = self.config_matrix["Model"]["offsets"]
        input_shape = self.config_matrix["Model"]["input_shape"]
        
        if isinstance(image, str):
            image = cv2.imread(image, cv2.IMREAD_COLOR)
            if image is None: raise ValueError("Could not read image file.")
        self.input_shape = np.array(input_shape, dtype=np.int32)
        self.image_shape = np.array(image.shape[:2], dtype=np.int32)
        
        #image = crop_image(image, offsets)
        origin, image = normalize_image(image, input_shape)
        
        return origin, image
        
    def infer(self, image):
        inference_program = self.inference_program
        feed_target_names = self.feed_target_names
        fetch_targets = self.fetch_targets
        input_shape = self.input_shape
        
        batch_outputs = self.exe.run(inference_program, feed={feed_target_names[0]: image,
                            feed_target_names[1]: input_shape[np.newaxis, :]},
                            fetch_list=fetch_targets, return_numpy=False)
        return batch_outputs
        
    def postprocess(self, origin, results):
        bboxes = np.array(results[0])
        if bboxes.shape[1] != 6:
            return origin, [], [], []
        labels = bboxes[:, 0].astype('int32')
        scores = bboxes[:, 1].astype('float32')
        boxes = bboxes[:, 2:].astype('float32')
        
        boxes = map_boxes(boxes, self.input_shape, self.image_shape)
        draw_img = draw_bbox_image(origin, boxes, labels, scores)
        
        return draw_img, boxes, labels, scores
        
    def __call__(self, image):
        origin, image = self.preprocess(image)
        results = self.infer(image)
        draw_img, boxes, labels, scores = self.postprocess(origin, results)
        
        return draw_img, boxes, labels, scores
        
        
if __name__ == "__main__":
    from matplotlib import pyplot as plt
    
    img_file = r"E:\Projects\Fabric_Defect_Detection\model_dev\v1.1.0\dataset\valid\MER2-041-436U3M(FDL17100010)_2020-12-02_19_35_11_980-1.bmp"
    cfg = {"Model":{"offsets":[0,0,0,0], "input_shape":[352,352]}}
    
    model = CudaModel(cfg, None)
    draw_img, _, _, _ = model(img_file)
    plt.imshow(draw_img), plt.show()