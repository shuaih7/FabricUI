#!/usr/bin/python
# -*- coding: utf-8 -*-

'''
Created on 01.28.2021
Updated on 03.03.2021

Author: haoshuai@handaotech.com
'''

import os
import sys
import tensorrt as trt
import pycuda.driver as cuda
import pycuda.autoinit
from .model import Model
from .preprocess import PreprocessYOLO
from .postprocess import PostprocessYOLO

TRT_LOGGER = trt.Logger()
abs_path = os.path.abspath(os.path.dirname(__file__))


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
        
        
# Simple helper data class that's a little nicer to use than a 2-tuple.
class HostDeviceMem(object):
    def __init__(self, host_mem, device_mem):
        self.host = host_mem
        self.device = device_mem

    def __str__(self):
        return "Host:\n" + str(self.host) + "\nDevice:\n" + str(self.device)

    def __repr__(self):
        return self.__str__()
        
        
# Allocates all buffers required for an engine, i.e. host/device inputs/outputs.
def allocate_buffers(engine):
    inputs = []
    outputs = []
    bindings = []
    stream = cuda.Stream()
    for binding in engine:
        size = trt.volume(engine.get_binding_shape(binding)) * engine.max_batch_size
        dtype = trt.nptype(engine.get_binding_dtype(binding))
        # Allocate host and device buffers
        host_mem = cuda.pagelocked_empty(size, dtype)
        device_mem = cuda.mem_alloc(host_mem.nbytes)
        # Append the device buffer to device bindings.
        bindings.append(int(device_mem))
        # Append to the appropriate list.
        if engine.binding_is_input(binding):
            inputs.append(HostDeviceMem(host_mem, device_mem))
        else:
            outputs.append(HostDeviceMem(host_mem, device_mem))
    return inputs, outputs, bindings, stream


# This function is generalized for multiple inputs/outputs.
# inputs and outputs are expected to be lists of HostDeviceMem objects.
def do_inference(context, bindings, inputs, outputs, stream, batch_size=1):
    # Transfer input data to the GPU.
    [cuda.memcpy_htod_async(inp.device, inp.host, stream) for inp in inputs]
    # Run inference.
    context.execute_async(batch_size=batch_size, bindings=bindings, stream_handle=stream.handle)
    # Transfer predictions back from the GPU.
    [cuda.memcpy_dtoh_async(out.host, out.device, stream) for out in outputs]
    # Synchronize the stream
    stream.synchronize()
    # Return only the host outputs.
    return [out.host for out in outputs]


class CudaModel(Model):
    def __init__(self, params):
        super(CudaModel, self).__init__(params=params)
        onnx_file_path = os.path.join(abs_path, 'trt/fast_yolo.onnx')
        engine_file_path = os.path.join(abs_path, 'trt/fast_yolo.trt')
        
        self.updateParams(params)
        self.loadTRTEngine(onnx_file_path, engine_file_path)
        
    def updateParams(self, params):
        self.output_shapes = params["output_shapes"] # [(1, 18, 11, 11)] for the fast-yolo model
        self.preprocessor = PreprocessYOLO(params)
        self.postprocessor = PostprocessYOLO(params)
        self.params = params
        
    def loadTRTEngine(self, onnx_file_path, engine_file_path):
        self.engine = get_engine(onnx_file_path, engine_file_path)
        self.context = self.engine.create_execution_context()
        self.inputs, self.outputs, self.bindings, self.stream = allocate_buffers(self.engine)
        
    def preprocess(self, image):
        origin, image = self.preprocessor(image)
        return origin, image
  
    def infer(self, image):
        self.inputs[0].host = image
        trt_outputs = do_inference(self.context, bindings=self.bindings, inputs=self.inputs, outputs=self.outputs, stream=self.stream)

        # Before doing post-processing, we need to reshape the outputs as the common.do_inference 
        # will give us flat arrays.
        trt_outputs = [output.reshape(shape) for output, shape in zip(trt_outputs, self.output_shapes)]
        
        return trt_outputs
        
    def postprocess(self, origin, trt_outputs):
        # Run the post-processing algorithms on the TensorRT outputs and get the bounding box 
        # details of detected objects
        boxes, labels, scores = self.postprocessor(origin, trt_outputs)
        
        results = {}
        results['boxes'] = boxes
        results['labels'] = labels
        results['scores'] = scores
        
        return results
        
    def __call__(self, image):
        origin, image = self.preprocess(image)
        trt_outputs = self.infer(image)
        results = self.postprocess(origin, trt_outputs)
        
        return origin, results
