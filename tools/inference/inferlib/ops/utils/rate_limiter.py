import time


def rate_limiter(pipe, *, rate):
    
    loop_time = 0.0 if rate == 0 else 1.0/rate
    loop_start = time.time()
    
    for item in pipe:
        yield item
        
        if loop_time > 0.0:
            loop_sleep = loop_time - (time.time() - loop_start)
            if loop_sleep > 0.0:
                time.sleep(loop_sleep)
        loop_start = time.time()
        
