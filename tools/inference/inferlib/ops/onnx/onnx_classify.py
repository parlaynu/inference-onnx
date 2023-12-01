import time

def classify(pipe, *, session):
    
    total_time = 0
    
    for idx, item in enumerate(pipe):
        start = time.time()
        
        image = item['image']
        
        preds = session.run(None, {
            'image': image
        })
        
        # I think this will always be true... catch it just in case though
        assert len(preds) == 1
                
        item['preds'] = preds[0]
        
        total_time += (time.time() - start)
        item['inference_time'] = total_time

        yield item

