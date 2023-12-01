# Platform: Jetson Nano

| Item    | Version             |
| ------- | ------------------- |
| Hardare | Jetson Nano         |
| Memory  | 4 GBytes            |
| L4T     | 32.7.4              |
| OS      | Ubuntu 18.04.6 LTS  |
| Jetpack | 4.6.4-b39           |

An important thing to note here is that although the Jetson Nano has cuda the onnxruntime can't utilise
it so this is purely a CPU setup similar to the RaspberryPi.

## Setup

### Operating System

Install your Operating system as described in detail [here](https://developer.nvidia.com/embedded/learn/get-started-jetson-nano-devkit)

### Additional OS Setup

A few other configuration items you might want to do are listed in this section.

Update the operating system:

    $ sudo apt update
    $ sudo apt dist-upgrade
    $ sudo reboot

Turn off the GUI so you have more RAM available:

    $ sudo systemctl set-default multi-user
    $ sudo reboot

If you wish to turn it back on at any time, run this command:

    $ sudo systemctl set-default graphical

Disable In-Memory Swap

    $ sudo systemctl disable nvzramconfig.service

Setup Swap File

    $ SWAPLOCATION=/swapfile
    $ SWAPSIZE=4G
    $ sudo fallocate -l ${SWAPSIZE} ${SWAPLOCATION}
    $ sudo chmod 600 ${SWAPLOCATION}
    $ sudo mkswap ${SWAPLOCATION}
    $ sudo swapon ${SWAPLOCATION}

Add to /etc/fstab:

    /swapfile  none  swap  sw  0  0

And reboot:

    $ sudo reboot

Install the latest pip:

    $ wget https://bootstrap.pypa.io/pip/3.6/get-pip.py
    $ sudo -H python3 get-pip.py
    $ rm get-pip.py

Install jtop:

    $ sudo -H python3 -m pip install -U jetson-stats
    $ sudo reboot

### Docker

This repository uses docker to build the environments and run the tools. I've taken this approach as it can
be fully automated and isolated from the host environment - it should work reliably no matter what you have 
installed on your host.

Docker is installed and ready to use as part of the standard install.

Add your user to the docker group so you can interact with the system without being root or
running sudo all the time:

    $ sudo usermod -aG docker <username>

Log out and back in and you'll be ready to go. Test by running the hello-world example:

    $ docker run hello-world

### Camera

The camera server needs to run on the host - I haven't been able to get it to run inside a container. There
are only a few packages to install from and base OS:
 
    sudo apt install nvidia-jetpack deepstream-6.0

    pip3 install --user pyzmq==25.1.1

See the main README.md file for instructions on using the camera servers.

### Inference

The helper scripts and files needed to build the container and run inference are in the `inference` directory.

| Script        | Description                                                              |
| ------------- | ------------------------------------------------------------------------ |
| build.sh      | create a docker image with the software and models to run inference      |
| run-latest.sh | launch the latest docker image as a container running bash interactively |

See the main README.md file for instructions on running the inference tools.

## Example Inference Session

This is one way to run inference using the `picam2-server.py` as the image source.

To launch the nvargus camera server, run:

    $ cd tools/cameras
    $ ./nvargus-server.py
    listening on tcp://127.0.0.1:8089

When it starts, it will print out the url the camera is listening on - copy this as it will be needed to pass
to the inference tool.

The address above (127.0.0.1) will be accessible from within the container if you launch it with the `run-latest.sh` 
script as it starts the container with host networking.

To run the inference on 10 images, run, from within the container:

    $ ./classify-onnx.py -l 10 models/resnet18.onnx tcp://127.0.0.1:8089
    preparing session
    - available providers: ['AzureExecutionProvider', 'CPUExecutionProvider']
    - in use providers: ['CPUExecutionProvider']
    - input shape: 1 3 224 224
    - output shape: [1, 1000]
    00 image_0000 1920x1080x3
       892 @ 30.88
    01 image_0001 1920x1080x3
       892 @ 27.50
    02 image_0002 1920x1080x3
       892 @ 44.68
    03 image_0003 1920x1080x3
       892 @ 39.12
    04 image_0004 1920x1080x3
       892 @ 42.16
    05 image_0005 1920x1080x3
       892 @ 38.64
    06 image_0006 1920x1080x3
       892 @ 55.99
    07 image_0007 1920x1080x3
       892 @ 42.74
    08 image_0008 1920x1080x3
       892 @ 40.32
    09 image_0009 1920x1080x3
       892 @ 35.49
    runtime: 3 seconds
        fps: 3.09

