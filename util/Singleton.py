
class Singleton:
    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, '_instance'):
            cls._instance = super(Singleton, cls).__new__(cls)
            
            if hasattr(cls, '_init'):
                cls._instance._init(*args, **kwargs)
        
        return cls._instance




if __name__ == '__main__':
    class SingletonTest(Singleton):
        def _init(self):
            print("only init")

    class SingletonTest2(Singleton):
        pass

    class SingletonBase(Singleton):
        pass

    class SingletonWithInheritanceTest(SingletonBase):
        pass

    
    SingletonTest()
    SingletonTest()
    SingletonTest()

    SingletonTest2()
    SingletonTest2()

    print("Should be False:", SingletonTest() is SingletonTest2())
    print("Should be True:", SingletonTest() is SingletonTest())
    print("Should be True:", SingletonWithInheritanceTest() is SingletonWithInheritanceTest())


