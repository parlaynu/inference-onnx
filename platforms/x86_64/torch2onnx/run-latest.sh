#!/usr/bin/env bash

mkdir -p "${HOME}/Workspace/models"

docker run -it --rm -v "${HOME}/Workspace/models":/workspace/models local/torch2onnx:latest /bin/bash

