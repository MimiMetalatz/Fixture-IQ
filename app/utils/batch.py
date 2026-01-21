def batch(iterable, batch_size=1000):
    for i in range(0, len(iterable), batch_size):
        yield iterable[i:i + batch_size]