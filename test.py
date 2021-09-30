from webgebra import *

x = Symbol('x')
y = Symbol('y')
z = Symbol('z')
t = Symbol('t')

t = x +y +-z + x + t
print(t | [x >> 2, z >> -4])