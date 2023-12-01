#!/usr/bin/env python3.6
import sys
import argparse

import gi
gi.require_version('Gst', '1.0')
gi.require_version('GstApp', '1.0')
from gi.repository import GLib, Gst, GstApp


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
    Gst.util_set_object_arg(node, "caps", f"video/x-raw(memory:NVMM), width=(int){cam_width}, height=(int){cam_height}")
    
    node = Gst.ElementFactory.make('autovideosink')
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
            return None

    print(f"  -> {n1.name}: {len(n1.sinkpads)} {len(n1.srcpads)}")
    
    return pipe


def run(pipe):

    try:
        pipe.set_state(Gst.State.PLAYING)

        loop = GLib.MainLoop()
        loop.run()

    except KeyboardInterrupt:
        pass
    
    finally:
        pipe.set_state(Gst.State.NULL)
        pipe.get_state(Gst.CLOCK_TIME_NONE)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--hflip', help='flip the image horizontally', action='store_true')
    parser.add_argument('--vflip', help='flip the image vertically', action='store_true')
    parser.add_argument('-c', '--centre', help='crop the centre square of the image', action='store_true')    
    args = parser.parse_args()
    
    pipe = build_pipeline(args.hflip, args.vflip, args.centre)
    run(pipe)


if __name__ == "__main__":
    main()
