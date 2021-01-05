PATH = None
f = None

def clear():
    with open(PATH, "w"):
        pass


def iLog(func):
    def wrapper(*args, **kwargs):
        global f
        if args[0].logging: # args[0] should be self
            if f is None:
                f = open(PATH, "a+")
            f.write("{};{};{}\n".format(func.__name__, args, kwargs))
        return func(*args, **kwargs)
    return wrapper