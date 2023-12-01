import io

import numpy as np
from PIL import Image

import inferlib.utils as utils


def imageloader(pipe):
    for item in pipe:
        image_path = item['image_path']
        
        item['image'] = np.array(Image.open(image_path))
        item['image_size'] = utils.size_from(item['image'])
        
        yield item

