#!/usr/bin/env python3
import argparse
import onnx

parser = argparse.ArgumentParser()
parser.add_argument('model_path', help='path to model file', type=str, default=None)
args = parser.parse_args()

# load the model file
model = onnx.load(args.model_path)
onnx.checker.check_model(model)

# print it to stdout
print(onnx.helper.printable_graph(model.graph))
