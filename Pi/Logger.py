def iLog(func):
    def wrapper(*args, **kwargs):
        print("{} {} {}".format(func.__name__, args, kwargs))
        return func(*args, **kwargs)
    return wrapper