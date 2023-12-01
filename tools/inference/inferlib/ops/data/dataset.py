import os
import os.path


def dataset(imagedir):

    for idx, image_path in enumerate(_scandir(imagedir)):
        image_id = os.path.splitext(os.path.basename(image_path))[0]
        item = {
            'image_id': image_id,
            'image_path': image_path,
            'logs': [
                f"{idx:04d} processing {image_id}"
            ]
        }
        yield item


def _scandir(imagedir):
    imagedir = os.path.expanduser(imagedir)
    contents = os.scandir(imagedir)
    for c in contents:
        if c.name.startswith('.'):
            continue
        if c.is_file():
            yield c.path
        elif c.is_dir():
            yield from _scandir(c.path)

