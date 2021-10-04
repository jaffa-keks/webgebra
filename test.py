from webgebra import *

for l in 'qwertyuiopasdfghjklzxcvbnm':
    exec(l + "=Symbol('" + l +"')")

f = F(x, y)
f == x + y

print(f, f(a, b), f(6, 7))

# for some reason add is numexp but not exp