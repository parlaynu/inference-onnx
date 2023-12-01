import numpy as np


def imagefaker(pipe, *, image_size):

    fakeimage = np.zeros(image_size, dtype=np.uint8)

    for idx, item in enumerate(pipe):
        item['image'] = fakeimage 
        yield item

