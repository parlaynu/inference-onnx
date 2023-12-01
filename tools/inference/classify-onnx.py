#!/usr/bin/env python3
import argparse
import time

import inferlib.ops as ops
import inferlib.ops.onnx as onnx_ops
import inferlib.ops.classify as classify
import inferlib.ops.imaging as imaging
import inferlib.ops.utils as utils


def build_pipeline(session, dataspec, rate, limit):
    
    # get the shape of the input
    batch_size, nchans, height, width = session.get_inputs()[0].shape
    
    print(f"- input shape: {batch_size} {nchans} {height} {width}")
    print(f"- output shape: {session.get_outputs()[0].shape}")
    
    pipe = ops.datasource(dataspec, resize=(width, height), silent=True)
    if rate > 0:
        pipe = utils.rate_limiter(pipe, rate=rate)
    if limit > 0:
        pipe = utils.limiter(pipe, limit=limit)
    pipe = utils.worker(pipe)

    # pipe = imaging.resize(pipe, width=width, height=height)
    pipe = classify.preprocess(pipe)
    pipe = onnx_ops.classify(pipe, session=session)
    pipe = classify.postprocess(pipe)
    
    return pipe


def run(pipe):
    start = time.time()
    
    for idx, item in enumerate(pipe):
        image_id = item['image_id']
        image_size = item['image_size']
        tops = item['top']
        
        print(f"{idx:02d} {image_id} {image_size}")
        for top, prob in tops:
            print(f"   {top} @ {prob*100.0:0.2f}")
    
    duration = time.time() - start
    
    if item.get('jpeg', None):
        with open("image.jpg", "wb") as f:
            f.write(item['jpeg'])
    
    return duration, idx+1


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-l', '--limit', help='maximum number of images to process', type=int, default=0)
    parser.add_argument('-r', '--rate', help='requests per second', type=int, default=0)
    parser.add_argument('-c', '--force-cpu', help='force use the cpu even if there is a gpu', action='store_true')
    parser.add_argument('model', help='path to the onnx model file to load', type=str)
    parser.add_argument('dataspec', help='the data source specification', type=str)
    args = parser.parse_args()
    
    session = onnx_ops.prepare_session(args.model, force_cpu=args.force_cpu)
    
    pipe = build_pipeline(session, args.dataspec, args.rate, args.limit)
    duration, count = run(pipe)
    
    print(f"runtime: {int(duration)} seconds")
    print(f"    fps: {count/duration:0.2f}")


if __name__ == "__main__":
    main()

