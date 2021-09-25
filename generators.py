
from copy import deepcopy

from typing import Iterator
from typing import Generator as gen

from collections import deque

class Genfunc:

    def __init__(self, func, preserve: bool = False) -> None:
        self.function = func
        self.presv = preserve

    def __call__(self, *args, **kwargs) -> type:
        if self.presv:
            argos = []
            kgs = {}
            for i in args:
                try:
                    argos.append(deepcopy(i))
                except:
                    raise TypeError(f"{i} is not picklable")
            for key, val in kwargs.items():
                try:
                    kgs[key] = deepcopy(val)
                except:
                    raise TypeError(f"{i} is not picklable")
            args = argos
            kwargs = kgs            
        return Generator(self.function, args, kwargs)

    @staticmethod
    def preserved(func):
        return Genfunc(func, True)

    @staticmethod
    def looped_gen(func, *args, **kwargs):
        return Genfunc(func, args, kwargs)

    @staticmethod
    def preserved_looped_gen(func, *args, **kwargs):
        dummy_gen = Genfunc(func, preserve = True)
        return dummy_gen(*args, **kwargs)


class Generator:

    def __init__(self, function, args, kwargs) -> None:
        self.function = function
        self.args = list(args)
        self.kwargs = kwargs
        self.storage = {"args": {}, "kwargs": {}}
        self.__store__()
        self.genra = self.function(*self.args, **self.kwargs)


    def __iter__(self):
        return self


    def __next__(self):
        try:
            return next(self.genra)
        except StopIteration:
            self.__replenish__()
            self.genra = self.function(*self.args, **self.kwargs)
            raise StopIteration


    def __str__(self):
        return f"Looped generator object"


    def __replenish__(self):
        for i in self.storage["args"]:
            if isinstance(self.storage["args"][i], Iterator):
                if isinstance(self.storage["args"][i], gen):
                    self.args[i].refill()
                else:
                    self.args[i] = deepcopy(self.storage["args"][i])
        for i in self.storage["kwargs"]:
            if isinstance(self.storage["kwargs"][i], Iterator):
                if isinstance(self.storage["kwargs"][i], gen):
                    self.kwargs[i].refill()
                else:
                    self.kwargs[i] = deepcopy(self.storage["kwargs"][i])
        

    def __store__(self):
        for i in range(len(self.args)):
            if isinstance(self.args[i], Iterator):
                if isinstance(self.args[i], gen):
                    self.storage["args"][i] = self.args[i]
                    self.args[i] = Genobject(self.storage["args"][i], expl = True)
                else:
                    self.storage["args"][i] = deepcopy(self.args[i])
        for i in self.kwargs:
            if isinstance(self.kwargs[i], Iterator):
                if isinstance(self.kwargs[i], gen):
                    self.storage["kwargs"][i] = self.kwargs[i]
                    self.kwargs[i] = Genobject(self.storage["kwargs"][i], expl = True)
                else:
                    self.storage["kwargs"][i] = deepcopy(self.kwargs[i])



class Genobject:

    def __init__(self, genr, expl: bool = False):
        self.genrtr = genr
        self.deqs = [deque(), deque()]
        self.main = 0  # main generator dequeue index
        self.nglct = []
        self.expl = expl  # explictly changing the state of generator


    def __next__(self):
        if self.deqs[self.main]:
            val = self.deqs[self.main].popleft()
            self.deqs[self.main ^ 1].append(val)
            return val
        else:
            try:
                val = next(self.genrtr)
                for i in range(len(self.deqs)):
                    if i not in ([self.main] + self.nglct):
                        self.deqs[i].append(val)
                return val
            except StopIteration:
                if not self.expl:
                    self.refill()
                raise StopIteration


    def refill(self):
        self.main = self.main ^ 1

    
    def copy(self):
        obj = deque()
        indx = len(self.deqs)
        self.deqs.append(obj)
        for i in (self.deqs[self.main ^ 1] + self.deqs[self.main]):
            obj.append(i)

        def genr(objct, indx):
            while True:
                if objct:
                    yield objct.popleft()
                else:
                    try:
                        val = next(self.genr)
                        for i in range(len(self.deqs)):
                            if i not in ([indx] + self.nglct):
                                self.deqs[i].append(val)
                        yield val
                    except StopIteration:
                        self.nglct.append(indx)
                        return 0

        return genr(obj, indx)


    def __iter__(self):
        return self


    @staticmethod
    def generator(genr):
        return Genobject(genr)



@Genfunc
def counter(lis, num):
    k = num
    for i in lis:
        yield i
        if not k:
            return
        k -= 1

def cntr(num):
    for i in range(num):
        yield i

# b = cntr(10)
# a = counter(b, 3)

# print(list(a))
# print(list(a))
# print(list(a))
# for i in a:
#     print(i)
# print(list(a))

m = counter("hello world hype!", 5)
print(list(m))
print(list(m))

# o = cntr(10)

# c = Genobject.generator(o)

# for i in c:
#     print(i)

# print(list(c))
# print(list(c))