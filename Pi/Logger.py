ACTIVE = True

def clear():
    with open("out/log.txt", "w"):
        pass

def iLog(func):
    def wrapper(*args, **kwargs):
        if ACTIVE:
            with open("out/log.txt", "a+") as f:
                f.write("{};{};{}\n".format(func.__name__, args, kwargs))
        return func(*args, **kwargs)
    return wrapper