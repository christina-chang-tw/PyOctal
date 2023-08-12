
class helllo():
    
    @property
    def hi(self, a):
        print("hello")
        print(a)

    @hi.getter
    def hi(self):
        return 1, 3


a = helllo()
a.hi = 1
