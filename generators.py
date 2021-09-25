
from copy import deepcopy

from typing import Iterator
from typing import Generator as gen

from collections import deque

import logging

class Genfunc:

    def __init__(self, func, preserve: bool = False) -> None:
        """ Wrapper to generate a replenishable generator instead of an exhaustive generator
        
        Also see Genfunc.preserved to maintain the state of arguments passed into function during call
         """
        self.function = func
        self.presv = preserve

    def __call__(self, *args, **kwargs) -> type:
        if self.presv:
            args = list(args)
            for i,j in enumerate(args):
                try:
                    args[i] = deepcopy(j)
                except:
                    print(0, f"{j} is not picklable")
                    
            for key, val in kwargs.items():
                try:
                    kwargs[key] = deepcopy(val)
                except:
                    logging.log(0, f"{val} is not picklable")
        return Generator(self.function, args, kwargs)

    @staticmethod
    def preserved(func):
        """ Wrapper to get a self replenishing iterator object instead a exhaustive generator.
        Using preserved will preserve the state of arguments passed into the function during call.
         """
        return Genfunc(func, True)

    @staticmethod
    def looped_gen(func, *args, **kwargs) -> Iterator:
        """ Constructs a self replenishing generator from the given function and arguments.
        The arguements (both positional and keyword) should be the way the are passed while calling the function normally.

        Also see Genfunc.preserved_looped_gen to preserve the state of arguements.
         """
        return Genfunc(func, args, kwargs)

    @staticmethod
    def preserved_looped_gen(func, *args, **kwargs) -> Iterator:
        """ Constructs a self replnishing generator from the given function and arguments where state of arguements is preserved.
        The arguements (both positional and keyword) should be the way the are passed while calling the function normally.
        
        Also see Genfunc.looped_gen to have a iterator where argument states can be changed during runtime.
         """
        dummy_gen = Genfunc(func, preserve = True)
        return dummy_gen(*args, **kwargs)


class Generator:

    def __init__(self, function, args, kwargs) -> None:
        self.function = function
        self.args = list(args)
        self.kwargs = kwargs
        self.storage = {"args": {}, "kwargs": {}}
        self.__store()
        self.genra = self.function(*self.args, **self.kwargs)


    def __iter__(self):
        return self


    def __next__(self):
        try:
            return next(self.genra)
        except StopIteration:
            self.__replenish()
            self.genra = self.function(*self.args, **self.kwargs)
            raise StopIteration


    def __str__(self) -> str:
        return f"Looped generator object"


    def __replenish(self) -> None:
        """ Refill the iterator arguments for the generator """
        for i in self.storage["args"]:
            if isinstance(self.storage["args"][i], Iterator):
                if isinstance(self.storage["args"][i], gen):
                    self.args[i]._refill()
                else:
                    self.args[i] = deepcopy(self.storage["args"][i])
        for i in self.storage["kwargs"]:
            if isinstance(self.storage["kwargs"][i], Iterator):
                if isinstance(self.storage["kwargs"][i], gen):
                    self.kwargs[i]._refill()
                else:
                    self.kwargs[i] = deepcopy(self.storage["kwargs"][i])
        

    def __store(self) -> None:
        """ Store the itertor objects since they get exhausted with usage """
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
                    self._refill()
                raise StopIteration


    def _refill(self) -> None:
        """ refill (pseudo) the iterator by changing the states """
        self.main = self.main ^ 1

    
    def copy(self) -> gen:
        """ To get a copy of the generator this iterator represents """
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
    def generator(genr) -> Iterator:
        """ To get a replenishable iterator from the given generator """
        return Genobject(genr)

