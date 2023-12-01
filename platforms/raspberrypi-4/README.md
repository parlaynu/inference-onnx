# Platform: RaspberryPi 4 Bookworm

| Item    | Version             |
| ------- | ------------------- |
| Hardare | RaspberryPi 4b      |
| Memory  | 8 GBytes            |
| OS      | Bookworm Lite 64bit |

## Setup

### Operating System

Install your Operating system as described in detail [here](https://www.raspberrypi.com/documentation/computers/getting-started.html#install-using-imager)

I use the 'RaspberryPi OS Bookworm Lite 64bit' version to keep the system as simple as possible.

Once installed and you have network access and can remotely log in with ssh, update the OS:

    $ sudo apt update
    $ sudp apt dist-upgrade
    $ sudo reboot

### Docker

This repository uses docker to build the environments and run the tools. I've taken this approach as it can
be fully automated and isolated from the host environment - it should work reliably no matter what you have 
installed on your host.

Follow the instructions [here](https://docs.docker.com/engine/install/debian/) to install docker.

I used the instructions from the section "Install using the apt repository".

Once installed, add your user to the docker group so you can interact with the system without being root or
running sudo all the time:

    $ sudo usermod -aG docker pi

Log out and back in and you'll be ready to go. Test by running the hello-world example:

    $ docker run hello-world

### Camera

The camera server needs to run on the host - I haven't been able to get it to run inside a container. There
are only a few packages to install:

    sudo apt install python3-pip python3-picamera2

    pip3 install --user --break-system-packages pyzmq==25.1.1

See the main README.md file for instructions on using the camera servers.

### Inference

The helper scripts and files needed to build the container and run inference are in the `inference` directory.

| Script        | Description                                                              |
| ------------- | ------------------------------------------------------------------------ |
| build.sh      | create a docker image with the software and models to run inference      |
| run-latest.sh | launch the latest docker image as a container running bash interactively |

See the main README.md file for instructions on running the inference tools.

### Exporting PyTorch to Onnx

The helper scripts and files needed to build the container and run inference are in the `torch2onnx` directory.

| Script        | Description                                                              |
| ------------- | ------------------------------------------------------------------------ |
| build.sh      | create a docker image with the software and models to run exporting      |
| run-latest.sh | launch the latest docker image as a container running bash interactively |

See the main README.md file for instructions on running the export.

## Example Inference Session

This is one way to run inference using the `picam2-server.py` as the image source.

To launch the camera server, run:

    $ cd tools/cameras
    $ ./picam2-server.py
    listening on tcp://127.0.0.1:8089

When it starts, it will print out the url the camera is listening on - copy this as it will be needed to pass
to the inference tool.

To run the inference on 10 images, run, from within the container:

    $ ./classify-onnx.py -l 10 models/resnet18.onnx tcp://127.0.0.1:8089
    preparing session
    - available providers: ['AzureExecutionProvider', 'CPUExecutionProvider']
    - in use providers: ['CPUExecutionProvider']
    - input shape: 1 3 224 224
    - output shape: [1, 1000]
    00 image_0000 1920x1080x3
       815 @ 18.11
    01 image_0001 1920x1080x3
       489 @ 15.68
    02 image_0002 1920x1080x3
       489 @ 15.68
    03 image_0003 1920x1080x3
       489 @ 10.36
    04 image_0004 1920x1080x3
       815 @ 21.04
    05 image_0005 1920x1080x3
       815 @ 27.07
    06 image_0006 1920x1080x3
       815 @ 16.40
    07 image_0007 1920x1080x3
       815 @ 22.43
    08 image_0008 1920x1080x3
       489 @ 17.34
    09 image_0009 1920x1080x3
       489 @ 20.92
    runtime: 2 seconds
        fps: 3.57


