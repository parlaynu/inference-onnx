#!/usr/bin/env python3.6
import sys
import argparse
import tempfile
from itertools import count

import zmq

import gi
gi.require_version('Gst', '1.0')
gi.require_version('GstApp', '1.0')
from gi.repository import GLib, Gst, GstApp

from helpers import get_connect_url


print(f"libzmq version is {zmq.zmq_version()}")
print(f" pyzmq version is {zmq.__version__}")


def build_pipeline(hflip, vflip, crop):
    # initialise the system
    Gst.init(sys.argv)
    
    # hard coded for now
    camera_mode, cam_width, cam_height = 2, 1920, 1080
    
    print("Display Settings")
    print(f"  -> cam mode: {camera_mode}")
    print(f"  -> cam res: {cam_width} {cam_height}")

    # build the pipeline
    nodes = []    
    
    node = Gst.ElementFactory.make('nvarguscamerasrc')
    nodes.append(node)
    Gst.util_set_object_arg(node, "sensor-id", "0")
    Gst.util_set_object_arg(node, "bufapi-version", "true")
    Gst.util_set_object_arg(node, "sensor-mode", f"{camera_mode}")
    
    node = Gst.ElementFactory.make('nvvideoconvert')
    nodes.append(node)
    
    if hflip and vflip:
        Gst.util_set_object_arg(node, "flip-method", "2")
    elif hflip:
        Gst.util_set_object_arg(node, "flip-method", "4")
    elif vflip:
        Gst.util_set_object_arg(node, "flip-method", "6")
        
    if crop:
        cam_width = 1080
        Gst.util_set_object_arg(node, "src-crop", "420:0:1080:1080")

    node = Gst.ElementFactory.make('capsfilter')
    nodes.append(node)
    Gst.util_set_object_arg(node, "caps", f"video/x-raw, width=(int){cam_width}, height=(int){cam_height}")
    
    node = Gst.ElementFactory.make('nvjpegenc')
    nodes.append(node)
    Gst.util_set_object_arg(node, "quality", "100")

    appsink = node = Gst.ElementFactory.make('appsink')
    nodes.append(node)

    pipe = Gst.Pipeline.new('pipe')
    for node in nodes:
        pipe.add(node)
    
    print("Linking nodes:")
    for n0, n1 in zip(nodes, nodes[1:]):
        print(f"  -> {n0.name}: {len(n0.sinkpads)} {len(n0.srcpads)}")
        r = n0.link(n1)
        if r == False:
            print(f"failed to link nodes {n0.name} and {n1.name}")
            return None, None

    print(f"  -> {n1.name}: {len(n1.sinkpads)} {len(n1.srcpads)}")
    
    return pipe, appsink


def loop(appsink, socket):

    for idx in count():
        # read an image sample
        sample = appsink.pull_sample()
        if sample is None:
            raise RuntimeError("pipeline stopped")
            
        #  check for client request
        to = socket.poll(timeout=1)
        if to == 0:
            # no client request so just read the next sample
            continue
        
        print(f"{idx:04d} receiving", flush=True)
        message = socket.recv()

        print("- get buffer", flush=True)
        buffer = sample.get_buffer()
        if buffer is None:
            raise RuntimeError("sample has no buffer")

        print("- extract data", flush=True)
        data = buffer.extract_dup(0, buffer.get_size())
        
        print(f"- send image...", flush=True)
        socket.send(data, copy=False)


def run(pipe, appsink, socket):

    try:
        pipe.set_state(Gst.State.PLAYING)
        loop(appsink, socket)

    except KeyboardInterrupt:
        pass
    
    finally:
        pipe.set_state(Gst.State.NULL)
        pipe.get_state(Gst.CLOCK_TIME_NONE)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--ipc', help='use the IPC transport', action='store_true')
    parser.add_argument('-a', '--all', help='listen on all interfaces', action='store_true')
    parser.add_argument('-p', '--port', help='port to listen on', type=int, default=8089)
    parser.add_argument('-r', '--fps', help='camera frame rate', type=int, default=None)
    parser.add_argument('--hflip', help='flip the image horizontally', action='store_true')
    parser.add_argument('--vflip', help='flip the image vertically', action='store_true')
    parser.add_argument('-c', '--centre', help='crop the centre square of the image', action='store_true')    
    args = parser.parse_args()
    
    # the URL to bind to
    if args.ipc:
        tempdir = tempfile.TemporaryDirectory()
        url = f"ipc://{tempdir.name}/socket"
    else:
        address = "0.0.0.0" if args.all else "127.0.0.1"
        url = f"tcp://{address}:{args.port}"
    
    context = zmq.Context()
    socket = context.socket(zmq.REP)
    socket.bind(url)
    
    url = socket.getsockopt(zmq.LAST_ENDPOINT).decode('utf-8')
    url = get_connect_url(url)
    print(f"listening on {url}")
    
    pipe, appsink = build_pipeline(args.hflip, args.vflip, args.centre)
    run(pipe, appsink, socket)


if __name__ == "__main__":
    main()
