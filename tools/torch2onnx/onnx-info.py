#!/usr/bin/env python3
import argparse
import onnxruntime as ort

parser = argparse.ArgumentParser()
parser.add_argument('model_path', help='path to model file', type=str, default=None)
args = parser.parse_args()

session = ort.InferenceSession(args.model_path)

inputs = session.get_inputs()
print("inputs:")
for idx, i in enumerate(inputs):
    print(f"- {idx:02d}: {i.name} {i.shape} {i.type}")

outputs = session.get_outputs()
print("outputs:")
for idx, o in enumerate(outputs):
    print(f"- {idx:02d}: {o.name} {o.shape} {o.type}")

