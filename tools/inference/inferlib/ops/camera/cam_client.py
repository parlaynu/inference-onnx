import time
from itertools import count
import io

import zmq
# print(f"libzmq version is {zmq.zmq_version()}")
# print(f" pyzmq version is {zmq.__version__}")

import numpy as np
from PIL import Image

import inferlib.utils as utils


def cam_client(url, *, silent=True):
    
    if not silent:
        print("connecting...", flush=True)
    context = zmq.Context()
    socket = context.socket(zmq.REQ)
    socket.connect(url)

    for idx in count():

        if not silent:
            print(f"{idx:02d} requesting", flush=True)
        socket.send_string("image")
        
        if not silent:
            print(f"- receiving", flush=True)
        data = socket.recv()

        if not silent:
            print(f"- received {len(data)} bytes", flush=True)
        
        yield {
            'image_id': f'image_{idx:04d}',
            'jpeg': data
        }
    

def cam_loader(inp):
    for item in inp:
        jpeg = item['jpeg']
        item['image'] = np.array(Image.open(io.BytesIO(jpeg)))
        item['image_size'] = utils.size_from(item['image'])
        yield item

