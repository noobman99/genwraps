
from generators import *

@Genfunc.preserved
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

b = cntr(10)
a = counter(b, 3)

print(list(a))
print(list(a))
print(list(a))
for i in a:
    print(i)
print(list(a))

m = counter("hello world hype!", 5)
print(list(m))
print(list(m))

o = cntr(10)

c = Genobject.generator(o)

for i in c:
    print(i)

print(list(c))
print(list(c))