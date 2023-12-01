#!/usr/bin/env python3
from pprint import pprint

from picamera2 import Picamera2, Preview
from libcamera import Transform


def caminfo():

    cam = Picamera2()
    for idx, sensor_mode in enumerate(cam.sensor_modes):
        print(f"sensor mode {idx}:")
        pprint(sensor_mode)


def main():
    caminfo()


if __name__ == "__main__":
    main()
