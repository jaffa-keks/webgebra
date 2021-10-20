from webgebra import *

for l in 'qwertyuiopasdfghjklzxcvbnm':
    exec(l + "=NumSym('" + l +"')")

g1 = F(s)
g1 == 0.5/(50*s + 1)

print(g1(s))