import numpy as np


def postprocess(pipe):
    
    for item in pipe:
        preds = item['preds']
        
        probs = softmax(preds, axis=1)
        item['probs'] = probs
        
        tops = np.argmax(preds, axis=1)
        
        top_list = []
        for top, prob in zip(tops, probs):
            top_list.append((top, prob[top]))
        item['top'] = top_list
        
        yield item


# copied from scipy.special
# - running on jetson which has an old version of scipy without softmax included
def softmax(x, axis=None):
    x_max = np.amax(x, axis=axis, keepdims=True)
    exp_x_shifted = np.exp(x - x_max)
    return exp_x_shifted / np.sum(exp_x_shifted, axis=axis, keepdims=True)

