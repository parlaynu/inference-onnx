#!/usr/bin/env python3
import argparse
import time

import zmq


def read_images(url, limit):
    
    context = zmq.Context()
    socket = context.socket(zmq.REQ)
    socket.connect(url)
    
    start = time.time()
    for idx in range(limit):
        socket.send_string("image")
        data = socket.recv()
        print(f"{idx:02d} received image: {len(data)} bytes")
    duration = time.time() - start
    
    with open("image.jpg", "wb") as f:
        f.write(data)
    
    return duration


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-c', '--count', help='maximum number of images to process', type=int, default=5)
    parser.add_argument('url', help='the url to connect to', type=str)
    args = parser.parse_args()
    
    duration = read_images(args.url, args.count)
    
    print(f"runtime: {duration:0.2f} seconds")
    print(f"    fps: {args.count/duration:0.2f}")


if __name__ == "__main__":
    main()
