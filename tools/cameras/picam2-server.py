#!/usr/bin/env python3
import argparse
from itertools import count
import io
from datetime import datetime
from pprint import pprint
import tempfile

import socket
import zmq

import piexif
from PIL import Image

from picamera2 import Picamera2, Preview
from libcamera import Transform

from helpers import get_connect_url


print(f"libzmq version is {zmq.zmq_version()}")
print(f" pyzmq version is {zmq.__version__}")


def camerasrc(socket, *, mode=1, fps=None, preview=False, vflip=False, hflip=False):

    print(f"running with sensor mode {mode}")

    cam = Picamera2()
    for idx, sensor_mode in enumerate(cam.sensor_modes):
        print(f"sensor mode {idx}:")
        pprint(sensor_mode)
    
    sensor_mode = cam.sensor_modes[mode]
    sensor_format = sensor_mode['format']
    sensor_size = sensor_mode['size']
    
    main_size = sensor_size

    # take special care with size if we're previewing
    preview_size = None
    if preview:
        preview_size = (1920, 1080)
        if main_size[0] < preview_size[0] or main_size[1] < preview_size[1]:
            main_size = preview_size

    kwargs = {
        'buffer_count': 2,
        'controls': {
            'FrameDurationLimits': (33333, 500000),
        },
        'main': {
            'size': main_size,
            'format': 'BGR888'
        },
        'queue': False
    }
    if fps is not None:
        kwargs['controls']['FrameRate'] = fps
    
    if preview:
        kwargs['lores'] = {
            'size': preview_size
        }
        kwargs['display'] = 'lores'

    if vflip or hflip:
        kwargs['transform'] = Transform(vflip=vflip, hflip=hflip)
    
    config = cam.create_still_configuration(**kwargs)
    cam.align_configuration(config)
    cam.configure(config)
    
    print("camera config:")
    pprint(cam.camera_config)
    
    if preview:
        cam.start_preview(Preview.DRM, width=1920, height=1080)
    cam.start()

    for idx in count():
        # do nothing until there's a request pending
        to = socket.poll(timeout=None)
        if to == 0:
            continue
        
        # capture the image and metadata
        images, metadata = cam.capture_arrays(['main'])
        
        item = {
            'camera_id': cam.camera.id,
            'camera_mode': mode,
            'image_id': idx,
            'image':images[0],
            'metadata': metadata
        }
        yield item


def generate_exif(pipe):
    
    for item in pipe:
        camera_id = item['camera_id']
        metadata = item['metadata']
        
        datetime_now = datetime.now().strftime("%Y:%m:%d %H:%M:%S")
        zero_ifd = {
            piexif.ImageIFD.Make: "Raspberry Pi",
            piexif.ImageIFD.Model: camera_id,
            piexif.ImageIFD.Software: "Picamera2",
            piexif.ImageIFD.DateTime: datetime_now
        }
        total_gain = metadata["AnalogueGain"] * metadata["DigitalGain"]
        exif_ifd = {
            piexif.ExifIFD.DateTimeOriginal: datetime_now,
            piexif.ExifIFD.ExposureTime: (metadata["ExposureTime"], 1000000),
            piexif.ExifIFD.ISOSpeedRatings: int(total_gain * 100)
        }
        exif = piexif.dump({"0th": zero_ifd, "Exif": exif_ifd})
        
        item['exif'] = exif
        
        yield item

    
def encode_jpeg(pipe):
    
    for item in pipe:
        image = item['image']
        exif = item.get('exif', None)

        image = Image.fromarray(image)
        
        jpeg = io.BytesIO()
        image.save(jpeg, format='jpeg', quality=95, exif=exif)
        jpeg.seek(0, io.SEEK_SET)
        
        item['jpeg'] = jpeg.getvalue()
        
        yield item
        

def run(pipe, socket):
    
    for idx, item in enumerate(pipe):
        # wait for a request... 
        # note: polling is performed upstream
        message = socket.recv()

        # send the current image
        jpeg = item['jpeg']
        
        print(f"{idx:04d} sending image", flush=True)
        
        socket.send(jpeg, copy=False)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--ipc', help='use the IPC transport', action='store_true')
    parser.add_argument('-a', '--all', help='listen on all interfaces', action='store_true')
    parser.add_argument('-p', '--port', help='port to listen on', type=int, default=8089)
    parser.add_argument('-r', '--fps', help='camera frame rate', type=int, default=None)
    parser.add_argument('-m', '--mode', help='the camera mode', type=int, default=6)
    parser.add_argument('-v', '--preview', help='enable previewing', action='store_true')
    parser.add_argument('--hflip', help='flip the image horizontally', action='store_true')
    parser.add_argument('--vflip', help='flip the image vertically', action='store_true')
    args = parser.parse_args()
    
    # create the socket
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
    
    # build the pipeline
    pipe = camerasrc(socket, mode=args.mode, fps=args.fps, preview=args.preview, vflip=args.vflip, hflip=args.hflip)
    pipe = generate_exif(pipe)
    pipe = encode_jpeg(pipe)
    
    run(pipe, socket)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        pass


