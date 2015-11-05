class classproperty(object):
    def __init__(self, fget):
        self.fget = fget
    def __get__(self, owner_self, owner_cls):
        return self.fget(owner_cls)

def iterbytes(bstring):
    for b in bstring:
        yield bytes((b,))