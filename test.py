from webgebra import *

for l in 'qwertyuiopasdfghjklzxcvbnm':
    exec(l + "=NumSym('" + l +"')")

k_ = AbsSym('k')

f = F(x)
f == x*a

print(f(x) | k_*x >> x**k_)