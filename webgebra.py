from wg_num import NumSym, NumAbsSym
from wg_core import Function
from wg_numops import Fraction
import wg_num

wg_num.GLOBAL_LATEX = True

F = Function
Q = Fraction

def S(s):
    ss = s.split(' ')
    return NumSym(ss[0]) if len(ss) == 1 else (NumSym(i) for i in ss)

def AS(s):
    ss = s.split(' ')
    return NumAbsSym(ss[0]) if len(ss) == 1 else (NumAbsSym(i) for i in ss)

################ FORMULAE #####################

def quad(a, b, c):
    x1 = (-b + (b ** 2 - 4 * a * c) ** (1 / 2)) / (2 * a)
    x2 = (-b - (b ** 2 - 4 * a * c) ** (1 / 2)) / (2 * a)
    return (x1, x2)

################################################

def help():
    help_s = '''--- HELP ---
    Symbol(s)               s (str) - symbol
    
    F(*x), Function(*x)     *x (expr) - function arguments
    
    AbsSym(s)               s (str) - symbol
    
    Rule(a, b)              a, b (expr) - original, image
    
    Q(a, b), Fraction(a, b) a, b (expr) - num, den
    '''
    print(help_s)