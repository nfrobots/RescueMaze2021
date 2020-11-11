ACTIVE = False
PATH = None

def clear():
    with open(PATH, "w"):
        pass

def iLog(func):
    def wrapper(*args, **kwargs):
        if ACTIVE:
            with open(PATH, "a+") as f:
                f.write("{};{};{}\n".format(func.__name__, args, kwargs))
        return func(*args, **kwargs)
    return wrapper