# Inference Using ONNX

This repository has tools and guidelines for exporting PyTorch models to ONNX and running classification inference using the exported model. 

The tools include:

* exporting from pytorch to onnx
* running inference using the exported onnx model
* camera image servers for RaspberryPi and Jetson Nano

It also has tools for building docker images to run the applications in various platforms. The available combinations of platform
and tool are shown in the table below.

| Tool           |  x86_64  | Jetson Nano  | RaspberryPi4 |
| -------------- | -------- | -------------| ------------ |
| torch2onnx     |   X      |              |              |
| infer-onnx     |   X      |   X          |   X          |
| nvargus-server |          |   X          |              |
| picam2-server  |          |              |   X          |

The `tools` directory contains the source code in python for the tools and the `platforms` directory has the tools
to build the docker images and environments for each of the supported platforms.

I wasn't able to run the camera software within a container as there are a lot of system dependencies. It might be
possible to make it work, but I gave up and instead created them as servers which can be connected to from within
an containerised environment to access images. This also means that these camera servers can serve images to processes
that are on other machines. ZeroMQ, specifically pyzmq, is used for the networking.

## The Tools

### Exporting PyTorch to ONNX

This is currently a very simple script. It downloads pretrained PyTorch models and exports to ONNX. It currently
doesn't even support loading custom model weights, but that will come soon... probably.

To run it:

    $ ./torch2onnx.py -h
    usage: torch2onnx.py [-h] [--bsize BSIZE] [--resolution RESOLUTION] [--channels CHANNELS] model [outdir]
    
    positional arguments:
      model                 model architecture
      outdir                output directory to write models to
      
    options:
      -h, --help            show this help message and exit
      --bsize BSIZE         batch size
      --resolution RESOLUTION
                            the image resolution for the model: WIDTHxHEIGHT
      --channels CHANNELS   number of input channels

A minimal run of the tools is:

    $ ./torch2onnx.py --resolution 224x224 resnet18
    Downloading: "https://download.pytorch.org/models/resnet18-f37072fd.pth" to /root/.cache/torch/hub/checkpoints/resnet18-f37072fd.pth
    100.0%
      batch size: 1
      image size: 224x224
    num channels: 3
     num classes: 1000
    exporting to ./local/models/resnet18.onnx

This defaults to a batch size of 1, extracts the number of channels and classes from the model itself, but requires
the input image resolution to be specified on the command line.

There are no dynamic axes in the exported model, only static. Although, it would be a simple thing to change if you
wanted to.

### Running Inference

The tool `classify-onnx.py` runs inference on the exported ONNX model. The full usage is:

    $ ./classify-onnx.py -h
    usage: classify-onnx.py [-h] [-l LIMIT] [-r RATE] [-c] model dataspec
    
    positional arguments:
      model                 path to the onnx model file to load
      dataspec              the data source specification
      
    options:
      -h, --help            show this help message and exit
      -l LIMIT, --limit LIMIT
                            maximum number of images to process
      -r RATE, --rate RATE  requests per second
      -c, --force-cpu       force use the cpu even if there is a gpu

The `model` parameter is the path to the ONNX model to load and use for inference. Check the platform
specific notes for instructions on how to access a model from within the container.

The dataspec can be a filesystem path to a directory of images or a URL to a camera server. The camera
server URL that the server is listening on printed out when the server starts and can be used directly 
here. See the camera server sections for details.

Note that if you use the scripts provided to run the inference container, you can access these servers
if they are bound to 127.0.0.1 as the containers are started with host networking.

### RaspberryPi Camera Server

The RaspberryPi camera server runs like this:

    $ ./picam2-server.py -h
    usage: picam2-server.py [-h] [-i] [-a] [-p PORT] [-r FPS] [-m MODE] [-v] [--hflip] [--vflip]
    
    options:
      -h, --help            show this help message and exit
      -i, --ipc             use the IPC transport
      -a, --all             listen on all interfaces
      -p PORT, --port PORT  port to listen on
      -r FPS, --fps FPS     camera frame rate
      -m MODE, --mode MODE  the camera mode
      -v, --preview         enable previewing
      --hflip               flip the image horizontally
      --vflip               flip the image vertically

To find the available modes for your camera, run the `picam2-info.py` tool. It is possible to run
using 'ipc' as the protocol, however, this won't be accessible from other hosts or within the container as they are
currently launched.

The simplest run is:

    $ ./picam2-server.py 
    listening on tcp://127.0.0.1:8089

To listen on all addresses on the server:

    $ ./picam2-server.py -a
    listening on tcp://192.168.1.31:8089

You can use the listening URLs directly in the inference application to specify a data source.

A lot of debug information is printed out, some of which is from the libcamera subsystem and can't be
controlled. It prints out the running configuration of the camera and then sits and waits for a request for
an image.

    {'buffer_count': 2,
     'colour_space': <libcamera.ColorSpace 'sYCC'>,
     'controls': {'FrameDurationLimits': (33333, 500000),
                  'NoiseReductionMode': <NoiseReductionModeEnum.HighQuality: 2>},
     'display': None,
     'encode': None,
     'lores': None,
     'main': {'format': 'BGR888',
              'framesize': 6220800,
              'size': (1920, 1080),
              'stride': 5760},
     'queue': False,
     'raw': {'format': 'SBGGR10_CSI2P',
             'framesize': 2592000,
             'size': (1920, 1080),
             'stride': 2400},
     'sensor': {'bit_depth': 10, 'output_size': (1920, 1080)},
     'transform': <libcamera.Transform 'identity'>,
     'use_case': 'still'}


### Jetson Nano Camera Server

The NvArgus camera server runs like this:

    $ ./nvargus-server.py -h
    usage: nvargus-server.py [-h] [-i] [-a] [-p PORT] [-r FPS] [--hflip] [--vflip]
                             [-c]
                             
    optional arguments:
      -h, --help            show this help message and exit
      -i, --ipc             use the IPC transport
      -a, --all             listen on all interfaces
      -p PORT, --port PORT  port to listen on
      -r FPS, --fps FPS     camera frame rate
      --hflip               flip the image horizontally
      --vflip               flip the image vertically
      -c, --centre          crop the centre square of the image

The simplest run is:

    $ ./nvargus-server.py 
    listening on tcp://127.0.0.1:8089

To listen on all addresses on the server:

    ./nvargus-server.py -a
    listening on tcp://192.168.1.39:8089

You can use the listening URLs directly in the inference application to specify a data source.

A lot of debug information is printed out, some of which is from the argus subsystem and can't be
controlled. One useful thing it does print is the available modes for your camera. If you run it once
with just the defaults, you will get this information and then be able to choose the mode you want
to use in a subsequent run.

The modes for my camera are like this (first one is mode 0):

    GST_ARGUS: 3264 x 2464 FR = 21.000000 fps Duration = 47619048 ; Analog Gain range min 1.000000, max 10.625000; Exposure Range min 13000, max 683709000;
    GST_ARGUS: 3264 x 1848 FR = 28.000001 fps Duration = 35714284 ; Analog Gain range min 1.000000, max 10.625000; Exposure Range min 13000, max 683709000;
    GST_ARGUS: 1920 x 1080 FR = 29.999999 fps Duration = 33333334 ; Analog Gain range min 1.000000, max 10.625000; Exposure Range min 13000, max 683709000;
    GST_ARGUS: 1640 x 1232 FR = 29.999999 fps Duration = 33333334 ; Analog Gain range min 1.000000, max 10.625000; Exposure Range min 13000, max 683709000;
    GST_ARGUS: 1280 x 720 FR = 59.999999 fps Duration = 16666667 ; Analog Gain range min 1.000000, max 10.625000; Exposure Range min 13000, max 683709000;
    GST_ARGUS: 1280 x 720 FR = 120.000005 fps Duration = 8333333 ; Analog Gain range min 1.000000, max 10.625000; Exposure Range min 13000, max 683709000;

It prints out the running configuration of the camera and then sits and waits for a request for
an image.

    GST_ARGUS: Running with following settings:
       Camera index = 0 
       Camera mode  = 2 
       Output Stream W = 1920 H = 1080 
       seconds to Run    = 0 
       Frame Rate = 29.999999 
    GST_ARGUS: Setup Complete, Starting captures for 0 seconds

There is also a `nvargus-preview.py` that will run the camera and display the output on the jetson's
monitor output.

## The Platforms

Under the `platform` directory, there is a directory for each platform supported, and inside each platform,
there is a directory for each tool for that platform.

The README.md has platform specific setup notes and also includes instructions for building and launching the
container. Each has a `build.sh` script that builds the docker image, and a `run-latest.sh` which launches 
the latest image as a container and starts an interactive bash session from which you can run the tools.

The script launches the container with all the correct options needed to run the tools inside it.

The scripts are all very simple and along with the Dockerfiles, should be very easy to follow and see what's
happening.

The exception to the above are the camera servers on the RaspberryPi and Jetson Nano as these can't run in 
a containerized environment. The platform specific README.md files have full instructions on how to setup the
environment for these cameras.





