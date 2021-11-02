from webgebra import *
from math import pi

wg_num.GLOBAL_LATEX = False

x, y, z, s, w = S('x y z s w')
a,b,c,d,e,f = S('a b c d e f')
x_, y_, z_ = AS('x y z')
x0 = S('x_0')

f = a * x**2
print(f.taylor(x, x0).simplify())
print(Sin(x).taylor(x, pi/2).simplify())