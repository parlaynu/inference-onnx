FROM nvidia/cuda:11.8.0-cudnn8-runtime-ubuntu22.04

RUN apt-get update && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y python3 git wget && \
    rm -rf /var/lib/apt/lists/*

RUN wget https://bootstrap.pypa.io/get-pip.py && \
    python3 get-pip.py && \
    rm get-pip.py && \
    rm -rf /root/.cache

RUN mkdir -p /workspace
WORKDIR /workspace

COPY files/requirements.txt requirements.txt
RUN pip3 install --no-cache-dir -r requirements.txt && rm requirements.txt

COPY local/torch2onnx /workspace/torch2onnx/

# workaround for a bug
RUN cd /usr/local/cuda/targets/x86_64-linux/lib/ && \
    ln -s libnvrtc.so.11.8.89 libnvrtc.so

ENTRYPOINT ["/bin/sh", "-c", "exec \"$0\" \"$@\""]
CMD ["/bin/bash"]
