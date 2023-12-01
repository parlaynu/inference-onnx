#!/usr/bin/env bash

mkdir -p "${HOME}/Workspace/models"

docker run -it --rm -v "${HOME}/Workspace/models":/workspace/models --network=host --runtime=nvidia --gpus all local/inference-onnx:latest /bin/bash

