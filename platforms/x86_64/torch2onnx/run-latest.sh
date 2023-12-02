#!/usr/bin/env bash

mkdir -p "${HOME}/Workspace/models"

docker run -it --rm \
    --network=host --runtime=nvidia --gpus all \
    -v "${HOME}/Workspace/models":/workspace/models \
    local/torch2onnx:latest /bin/bash

