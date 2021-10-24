from webgebra import *

x, y, z, s, w = S('x y z s w')
a,b,c,d,e,f = S('a b c d e f')
x_, y_, z_ = AS('x y z')

h1 = a+b+c+a+b
m = x_ + c + x_

print(m == h1, h1 | m >> x_)