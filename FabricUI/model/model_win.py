#!/usr/bin/python
# -*- coding: utf-8 -*-

'''
Created on 11.20.2020
Updated on 02.08.2021

Author: haoshuai@handaotech.com
'''

import os
import cv2
import copy
import numpy as np
import paddle.fluid as fluid
from .model import Model
from .preprocess import PreprocessYOLO
from .postprocess import map_boxes

abs_path = os.path.abspath(os.path.dirname(__file__))


class CudaModel(Model):
    """ CudaModel for inference on Windows 10 OS
        Note: The major postprocess for model outputs are freezed 
    
    Attributes:
        params: Model parameters
    
    Raises:
    
    """
    def __init__(self, params):
        super(CudaModel, self).__init__(params=params)
        place = fluid.CUDAPlace(0) # Use CUDAPlace as default
        self.exe = fluid.Executor(place)
        model_path = os.path.join(abs_path, "win")
        self.updateParams(params)
        
        [self.inference_program, self.feed_target_names, self.fetch_targets] = fluid.io.load_inference_model(dirname=model_path, executor=self.exe, model_filename='__model__', params_filename='params')
        
    def updateParams(self, params):
        input_h = params['input_h']
        input_w = params['input_w']
        
        self.params = params
        self.input_shape = np.array([input_h, input_w], dtype=np.int32)
        self.preprocessor = PreprocessYOLO(params)
        
    def preprocess(self, image):
        origin, image = self.preprocessor(image)
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
        
    def postprocess(self, origin, outputs):
        results = {}
        bboxes = np.array(outputs[0])
        if bboxes.shape[1] != 6:
            return {}
        labels = bboxes[:, 0].astype('int32')
        scores = bboxes[:, 1].astype('float32')
        boxes = bboxes[:, 2:].astype('float32')
        
        boxes = map_boxes(boxes, self.input_shape, origin.shape[:2])
        results['boxes'] = boxes
        results['labels'] = labels
        results['scores'] = scores
        
        return results
        
    def __call__(self, image):
        origin, image = self.preprocess(image)
        outputs = self.infer(image)
        results = self.postprocess(origin, outputs)
        
        return origin, results
        
        
if __name__ == "__main__":
    from matplotlib import pyplot as plt
    
    img_file = r"E:\Projects\Fabric_Defect_Detection\model_dev\v1.1.0\dataset\valid\MER2-041-436U3M(FDL17100010)_2020-12-02_19_35_11_980-1.bmp"
    cfg = {"offsets":[0,0,0,0], "input_shape":[352,352]}
    
    model = CudaModel(cfg)
    origin, results = model(img_file)
    
    boxes = results['boxes']
    labels = results['labels']
    scores = results['scores']
    image = draw_bbox_image(origin, boxes, labels, scores)
    plt.imshow(image), plt.show()