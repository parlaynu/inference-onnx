from itertools import islice


def limiter(pipe, *, limit):
    for item in islice(pipe, limit):
        yield item

