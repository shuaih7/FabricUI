#!/usr/bin/env python2

from __future__ import print_function
import time
import glob as gb
import numpy as np
import tensorrt as trt
import pycuda.driver as cuda
import pycuda.autoinit
from PIL import Image, ImageDraw

#from yolov3_to_onnx import download_file
from .data_processing import PreprocessYOLO, PostprocessYOLO, ALL_CATEGORIES

import sys, os
sys.path.insert(1, os.path.join(sys.path[0], ".."))
import .common

TRT_LOGGER = trt.Logger()

def draw_bboxes(image_raw, bboxes, confidences, categories, all_categories, bbox_color='blue'):
    """Draw the bounding boxes on the original input image and return it.
    Keyword arguments:
    image_raw -- a raw PIL Image
    bboxes -- NumPy array containing the bounding box coordinates of N objects, with shape (N,4).
    categories -- NumPy array containing the corresponding category for each object,
    with shape (N,)
    confidences -- NumPy array containing the corresponding confidence for each object,
    with shape (N,)
    all_categories -- a list of all categories in the correct ordered (required for looking up
    the category name)
    bbox_color -- an optional string specifying the color of the bounding boxes (default: 'blue')
    """
    draw = ImageDraw.Draw(image_raw)
    print(bboxes, confidences, categories)
    if bboxes is None: return image_raw

    for box, score, category in zip(bboxes, confidences, categories):
        x_coord, y_coord, width, height = box
        left = max(0, np.floor(x_coord + 0.5).astype(int))
        top = max(0, np.floor(y_coord + 0.5).astype(int))
        right = min(image_raw.width, np.floor(x_coord + width + 0.5).astype(int))
        bottom = min(image_raw.height, np.floor(y_coord + height + 0.5).astype(int))

        draw.rectangle(((left, top), (right, bottom)), outline=bbox_color)
        draw.text((left, top - 12), '{0} {1:.2f}'.format(all_categories[category], score), fill=bbox_color)

    return image_raw

def get_engine(onnx_file_path, engine_file_path=""):
    """Attempts to load a serialized engine if available, otherwise builds a new TensorRT engine and saves it."""
    def build_engine():
        """Takes an ONNX file and creates a TensorRT engine to run inference with"""
        with trt.Builder(TRT_LOGGER) as builder, builder.create_network() as network, trt.OnnxParser(network, TRT_LOGGER) as parser:
            builder.max_workspace_size = 1 << 30 # 1GB
            builder.max_batch_size = 1
            builder.fp16_mode = True
            # Parse model file
            if not os.path.exists(onnx_file_path):
                print('ONNX file {} not found, please run yolov3_to_onnx.py first to generate it.'.format(onnx_file_path))
                exit(0)
            print('Loading ONNX file from path {}...'.format(onnx_file_path))
            with open(onnx_file_path, 'rb') as model:
                print('Beginning ONNX file parsing')
                parser.parse(model.read())
            print('Completed parsing of ONNX file')
            print('Building an engine from file {}; this may take a while...'.format(onnx_file_path))
            engine = builder.build_cuda_engine(network)
            print("Completed creating Engine")
            with open(engine_file_path, "wb") as f:
                f.write(engine.serialize())
            return engine

    if os.path.exists(engine_file_path):
        # If a serialized engine exists, use it instead of building an engine.
        print("Reading engine from file {}".format(engine_file_path))
        with open(engine_file_path, "rb") as f, trt.Runtime(TRT_LOGGER) as runtime:
            return runtime.deserialize_cuda_engine(f.read())
    else:
        return build_engine()
        
        
class cudaModel(object):
    def __init__(self, config_matrix, logger):
        # Try to load a previously generated YOLOv3-608 network graph in ONNX format:
        onnx_file_path = '/home/nvidia/Documents/Projects/Fabric_defect_detection/YOLO/fast_yolo.onnx'
        engine_file_path = "./fast_yolo.trt"
        self.config_matrix = config_matrix
        self.logger = logger

        # Config the pre-processor arguments. Two-dimensional tuple with the target network's (spatial) input resolution in HW ordered 
        input_resolution_yolov3_HW = (config_matrix["Model"]["input_h"], config_matrix["Model"]["input_w"])
        self.preprocessor = PreprocessYOLO(input_resolution_yolov3_HW)

        # Load an image from the specified input path, and return it together with  a pre-processed version
        # image_raw, image = preprocessor.process(input_image_path)
        # Store the shape of the original input image in WH format, we will need it for later
        # self.shape_orig_WH = image_raw.size
        
        # Config the post-processor arguments
        self.shape_orig_WH = (config_matrix["Model"]["original_h"], config_matrix["Model"]["original_w"])
        self.postprocessor_args = {"yolo_masks": config_matrix["Model"]["yolo_masks"],  # A list of 3 three-dimensional tuples for the YOLO masks
                              "yolo_anchors": config_matrix["Model"]["yolo_anchors"],   # A list of 9 two-dimensional tuples for the YOLO anchors],
                              "obj_threshold": config_matrix["Model"]["obj_threshold"], # Threshold for object coverage, float value between 0 and 1
                              "nms_threshold": config_matrix["Model"]["nms_threshold"], # Threshold for non-max suppression algorithm, float value between 0 and 1
                              "yolo_input_resolution": self.input_resolution_yolov3_HW}
        self.postprocessor = PostprocessYOLO(**postprocessor_args)

        # Output shapes expected by the post-processor
        self.output_shapes = [config_matrix["Model"]["output_shapes"] # [(1, 18, 11, 11)] for the fast-yolo model
        
        self.engine = get_engine(self.onnx_file_path, self.engine_file_path)
        self.context = self.engine.create_execution_context()
        self.inputs, self.outputs, self.bindings, self.stream = common.allocate_buffers(self.engine)
        logger.info("Successfully load the detection model.")
  
    def infer(self, image, mode="run"): # image is a numpy array
        _, image = self.preprocessor.process(image, mode=mode)
        self.inputs[0].host = image
        trt_outputs = common.do_inference(self.context, bindings=self.bindings, inputs=self.inputs, outputs=self.outputs, stream=self.stream)

        # Before doing post-processing, we need to reshape the outputs as the common.do_inference will give us flat arrays.
        trt_outputs = [output.reshape(shape) for output, shape in zip(trt_outputs, self.output_shapes)]
        
        # Run the post-processing algorithms on the TensorRT outputs and get the bounding box details of detected objects
        boxes, classes, scores = self.postprocessor.process(trt_outputs, (self.shape_orig_WH))
        
        return boxes, classes, scroes

