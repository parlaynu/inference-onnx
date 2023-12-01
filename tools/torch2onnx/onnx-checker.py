#!/usr/bin/env python3
import argparse
import onnx

parser = argparse.ArgumentParser()
parser.add_argument('model_path', help='path to model file', type=str, default=None)
args = parser.parse_args()

print("loading the model", flush=True)
onnx_model = onnx.load(args.model_path)

print("running the checker", flush=True)
onnx.checker.check_model(onnx_model)

