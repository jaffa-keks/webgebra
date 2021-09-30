from webgebra import *

for l in 'qwertyuiopasdfghjklzxcvbnm':
    exec(l + "=Symbol('" + l +"')")

f = 2+3*Sin(x)**2 - 1/Log(t**2 + x)
ff = der(f, x)
print(ff.simplify())