import io

import numpy as np
from PIL import Image

import inferlib.utils as utils


def imageloader(pipe, *, resize=None):
    for item in pipe:
        image_path = item['image_path']
        
        image = Image.open(image_path)
        if resize is not None:
            image = image.resize(resize)
        
        item['image'] = np.array(image)
        item['image_size'] = utils.size_from(item['image'])
        
        yield item

