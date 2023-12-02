#!/usr/bin/env python3
import argparse
import os, os.path
import io
import re
import torch
import torch.nn as nn
import torchvision
import onnx
import onnxsim


def parse_cmdline():
    # parse the command line
    parser = argparse.ArgumentParser()
    parser.add_argument('--simplify', help='simplify the model before saving', action='store_true')
    parser.add_argument('--bsize', help='batch size', type=int, default=1)
    parser.add_argument('--resolution', help='the image resolution for the model: WIDTHxHEIGHT', type=str, default=None)
    parser.add_argument('--channels', help='number of input channels', type=int, default=3)
    # parser.add_argument('--classes', help='number of output classes', type=int, default=None)
    # parser.add_argument('--weights', help='model weights file', type=str, default=None)
    parser.add_argument("model", help='model architecture', type=str)
    parser.add_argument("outdir", help='output directory to write models to', type=str, nargs='?', default=None)
    args = parser.parse_args()
    
    return args


def resnet_info(model):
    nchannels = model.conv1.in_channels
    nclasses = model.fc.out_features
    
    return nclasses, nchannels, None, None
    

models = {
    'resnet18': [torchvision.models.resnet18, torchvision.models.ResNet18_Weights.IMAGENET1K_V1, resnet_info],
    'resnet50': [torchvision.models.resnet50, torchvision.models.ResNet50_Weights.IMAGENET1K_V1, resnet_info]
}


def create_model(architecture):
    factory, weights, info = models[architecture]

    model = factory(weights=weights)
    classes, channels, width, height = info(model)
    
    model.in_channels = channels
    model.in_width = width
    model.in_height = height
    model.out_classes = classes
    
    return model


def run_export(outpath, model, inp, *, simplify=False):
    
    onnx_data = io.BytesIO()
    
    with torch.no_grad():
        torch.onnx.export(
            model, inp, onnx_data,
            input_names=['image'],
            output_names=['preds'],
            opset_version=15,  # need this to run on jetson
            # dynamic_axes={
            #     'image': {0: 'batch'},
            #     'preds': {0: 'batch'}
            # }
        )
    
    onnx_data.seek(0, os.SEEK_SET)
    onnx_model = onnx.load(onnx_data)
    
    if simplify:
        onnx_model, check = onnxsim.simplify(onnx_model)
        if check == False:
            raise ValueError("onnxsim check failed")
    
    onnx.save(onnx_model, outpath)


def main():
    args = parse_cmdline()
    
    # create the model
    model = create_model(args.model)
    model.eval()

    # 
    if args.outdir is None:
        outdir = os.path.dirname(args.model)
        if len(outdir) == 0:
            outdir = "./local/models"
        args.outdir = outdir
    os.makedirs(args.outdir, exist_ok=True)
    
    if args.resolution is None:
        if model.in_width is None or model.in_height is None:
            raise RuntimeError("unable to determine model input resolution: must be specified")
        args.resolution = f"{model.in_width}x{model.in_height}"
    
    res_re = re.compile('(?P<width>\d+)x(?P<height>\d+)')
    mo = res_re.match(args.resolution)
    if mo is None:
        raise ValueError(f"invalid resolution specification: {args.resolution}")
    width, height = int(mo['width']), int(mo['height'])
    
    
    print(f"  batch size: {args.bsize}")
    print(f"  image size: {width}x{height}")
    print(f"num channels: {model.in_channels}")
    print(f" num classes: {model.out_classes}")
    
    outpath = os.path.join(args.outdir, f'{args.model}-{args.bsize}x{model.in_channels}x{height}x{width}.onnx')
    print(f"exporting to {outpath}", flush=True)

    device = torch.device('cuda') if torch.cuda.is_available() else torch.device('cpu')
    dtype = torch.float32
    
    model.to(device=device, dtype=dtype)
    inp = torch.rand((args.bsize, model.in_channels, height, width), device=device, dtype=dtype)

    run_export(outpath, model, inp, simplify=args.simplify)


if __name__ == "__main__" :
    main()

