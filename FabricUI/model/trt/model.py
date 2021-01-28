#!/usr/bin/python
# -*- coding: utf-8 -*-

'''
Created on 01.28.2021
Updated on 01.28.2021

Author: haoshaui@handaotech.com
'''

import os
import sys
import common
from .onnx_to_tensorrt import *


abs_path = os.path.abspath(os.path.dirname(__file__))
sys.path.append(abs_path)


class cudaModel(object):
    def __init__(self, config_matrix, messager):
        # Try to load a previously generated YOLOv3-608 network graph in ONNX format:
        onnx_file_path = '/home/nvidia/Documents/Projects/Fabric_defect_detection/YOLO/fast_yolo.onnx'
        engine_file_path = "./fast_yolo.trt"
        self.config_matrix = config_matrix
        self.messager = messager

        # Config the pre-processor arguments. Two-dimensional tuple with the target network's (spatial) input resolution in HW ordered 
        input_resolution_yolov3_HW = (config_matrix["Model"]["input_h"], config_matrix["Model"]["input_w"])
        self.preprocessor = PreprocessYOLO(input_resolution_yolov3_HW, offsets=[0,0,0,0]) #offsets=config_matrix["Model"]["offsets"])

        # Load an image from the specified input path, and return it together with  a pre-processed version
        # image_raw, image = preprocessor.process(input_image_path)
        # Store the shape of the original input image in WH format, we will need it for later
        # self.shape_orig_WH = image_raw.size
        
        # Config the post-processor arguments
        self.shape_orig_WH = (config_matrix["Model"]["image_raw_h"], config_matrix["Model"]["image_raw_w"])
        postprocessor_args = {"yolo_masks": config_matrix["Model"]["yolo_masks"],  # A list of 3 three-dimensional tuples for the YOLO masks
                              "yolo_anchors": config_matrix["Model"]["yolo_anchors"],   # A list of 9 two-dimensional tuples for the YOLO anchors],
                              "obj_threshold": config_matrix["Model"]["obj_threshold"], # Threshold for object coverage, float value between 0 and 1
                              "nms_threshold": config_matrix["Model"]["nms_threshold"], # Threshold for non-max suppression algorithm, float value between 0 and 1
                              "yolo_input_resolution": input_resolution_yolov3_HW}
        self.postprocessor = PostprocessYOLO(**postprocessor_args)

        # Output shapes expected by the post-processor
        self.output_shapes = config_matrix["Model"]["output_shapes"] # [(1, 18, 11, 11)] for the fast-yolo model
    
        onnx_file_path = os.path.join(abs_path, "fast_yolo.onnx")
        engine_file_path = os.path.join(abs_path, "fast_yolo.trt")
        self.engine = get_engine(onnx_file_path, engine_file_path)
        self.context = self.engine.create_execution_context()
        self.inputs, self.outputs, self.bindings, self.stream = common.allocate_buffers(self.engine)
        messager.info("Successfully load the detection model.")
  
    def infer(self, image): # image is a numpy array
        image_crop, image = self.preprocessor.process(image)
        self.inputs[0].host = image
        trt_outputs = common.do_inference(self.context, bindings=self.bindings, inputs=self.inputs, outputs=self.outputs, stream=self.stream)

        # Before doing post-processing, we need to reshape the outputs as the common.do_inference will give us flat arrays.
        trt_outputs = [output.reshape(shape) for output, shape in zip(trt_outputs, self.output_shapes)]
        
        # Run the post-processing algorithms on the TensorRT outputs and get the bounding box details of detected objects
        boxes, classes, scores = self.postprocessor.process(trt_outputs, (self.shape_orig_WH))
        
        return image_crop, boxes, classes, scores