# Platform: AMD64 with Nvidia RTX2060

| Item    | Version                       |
| ------- | ----------------------------- |
| CPU     | AMD Ryzen 7 3700X             |
| GPU     | Nvidia GeForce RTX 2060 SUPER |
| Memory  | 32 GBytes                     |
| OS      | Ubuntu 22.04                  |

## Setup

### Docker

This repository uses docker to build the environments and run the tools. I've taken this approach as it can
be fully automated and isolated from the host environment - it should work reliably no matter what you have 
installed on your host.

Install docker following these [instructions](https://docs.docker.com/engine/install/ubuntu/)

Then install the nvidia container toolkit following these [instructions](https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/latest/install-guide.html)

Once installed, add your user to the docker group so you can interact with the system without being root or
running sudo all the time:

    $ sudo usermod -aG docker <username>

Log out and back in and you'll be ready to go. Test by running the nvidia-smi example:

    $ docker run --rm --runtime=nvidia --gpus all ubuntu nvidia-smi

### Inference

The helper scripts and files needed to build the container and run inference are in the `inference` directory.

| Script        | Description                                                              |
| ------------- | ------------------------------------------------------------------------ |
| build.sh      | create a docker image with the software and models to run inference      |
| run-latest.sh | launch the latest docker image as a container running bash interactively |

See the main README.md file for instructions on running the inference tools.

## Example Inference Session

This is one way to run inference using the `picam2-server.py` as the image source.

To launch the camera server, on a raspberry pi run:

    $ cd tools/cameras
    $ ./picam2-server.py -a
    listening on tcp://192.168.1.17:8089

When it starts, it will print out the url the camera is listening on - copy this as it will be needed to pass
to the inference tool.

The address above (127.0.0.1) will be accessible from within the container if you launch it with the `run-latest.sh` 
script as it starts the container with host networking.

To run the inference on 10 images, run, from within the container:

    $ ./classify-onnx.py -l 10 models/resnet18.onnx tcp://192.168.1.17:8089
    preparing session
    - available providers: ['TensorrtExecutionProvider', 'CUDAExecutionProvider', 'AzureExecutionProvider', 'CPUExecutionProvider']
    - in use providers: ['CUDAExecutionProvider', 'CPUExecutionProvider']
    - input shape: 1 3 224 224
    - output shape: [1, 1000]
    00 image_0000 1920x1080x3
       315 @ 32.93
    01 image_0001 1920x1080x3
       315 @ 24.47
    02 image_0002 1920x1080x3
       315 @ 30.93
    03 image_0003 1920x1080x3
       315 @ 31.36
    04 image_0004 1920x1080x3
       815 @ 24.85
    05 image_0005 1920x1080x3
       815 @ 23.27
    06 image_0006 1920x1080x3
       315 @ 30.92
    07 image_0007 1920x1080x3
       315 @ 23.07
    08 image_0008 1920x1080x3
       315 @ 24.81
    09 image_0009 1920x1080x3
       315 @ 30.66
    runtime: 1 seconds
        fps: 6.22


