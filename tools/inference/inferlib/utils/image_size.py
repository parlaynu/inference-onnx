from PIL import Image
import numpy as np

# images: size
#      width x height x channels
# numpy: shape
#      rows x columns x channels
# torch: shape
#       channels x rows x columns


class ImageSize:
    def __init__(self, width, height=0, channels=0):
        self.width = width
        self.height = height if height > 0 else width
        self.channels = channels
    
    def __str__(self):
        return f"{self.width}x{self.height}x{self.channels}"


def size_from(arg):
    if isinstance(arg, np.ndarray):
        height, width = arg.shape[:2]
        channels = arg.shape[2] if arg.ndim == 3 else 1
    
    elif isinstance(arg, Image.Image):
        width, height = arg.size
        channels = len(arg.getbands())
    
    else:
        raise ValueError(f"don't know how to get image size from {type(arg)}")
    
    return ImageSize(width, height, channels)


