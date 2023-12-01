import numpy as np


def preprocess(pipe, *, mean=[0.485, 0.456, 0.406], stddev=[0.229, 0.224, 0.225]):
    
    mean = np.asarray(mean, dtype=np.float32)
    stddev = np.asarray(stddev, dtype=np.float32)
    
    for item in pipe:
        image = (item['image'].astype(np.float32) / 255.0 - mean) / stddev
        image = np.transpose(image, (2, 0, 1))
        image = np.expand_dims(image, axis=0)
        
        # tensorrt needs a contiguous array
        item['image'] = np.ascontiguousarray(image)

        yield item


def quicktest():    
    data = np.ones((224, 224, 3), dtype=np.float32)
    data[:, :, 0] = data[:, :, 0] * 255
    data[:, :, 1] = data[:, :, 1] * 2 * 255
    data[:, :, 2] = data[:, :, 2] * 3 * 255

    pipe = [{'image': data}]
    
    mean = [1, 2, 3]
    
    for item in preprocess(pipe, mean=mean):
        data = item['image']
        assert (data==0.0).all()
        print("passed")
        

if __name__ == "__main__":
    quicktest()
