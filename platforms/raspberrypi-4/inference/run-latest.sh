#!/usr/bin/env bash

mkdir -p "${HOME}/Workspace/models"

docker run -it --rm -v "${HOME}/Workspace/models":/workspace/models --network=host rpi4/inference-onnx:latest /bin/bash
