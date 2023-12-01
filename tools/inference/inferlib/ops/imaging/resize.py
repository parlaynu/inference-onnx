import cv2


def resize(pipe, *, width, height):

    for item in pipe:
        image = item['image']
        item['image'] = cv2.resize(image, (width, height))
        yield item

