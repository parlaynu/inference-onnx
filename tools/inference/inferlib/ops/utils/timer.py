import time


def timer(pipe, *, label):
    upstream = 0
    
    start = time.time()
    for item in pipe:
        upstream += time.time() - start
        yield item
        start = time.time()

    # fill in the time tracking
    sub = item.get('items', None)
    if sub is not None:
        item = sub[-1]
    
    uptimes = item.get('upstream_times', [])
    uptimes.append({'label': label, 'time': upstream})
    item['upstream_times'] = uptimes

