from copy import copy

class Expr:
    def __init__(self, e : list):
        self.e = e

    def __eq__(self, other):
        return type(self) == type(other) and self.e == other.e

    def apply(self, *rules: list):
        for r in rules:
            assert type(r) is Rule
            if r.a == self:
                return r.eval()
        ne = []
        for i in self.e:
            if isinstance(i, Expr):
                ne.append(i.apply(*rules))
            else:
                c = False
                for r in rules:
                    if r.a == i:
                        ne.append(r.eval())
                        c = True
                        break
                if not c: ne.append(i)
        k = copy(self)
        k.e = ne
        return k

    def __str__(self):
        r = 'Expr['
        for i in self.e: r += str(i) + ', '
        return r[:-2] + ']'

    def __rshift__(self, other):
        return Rule(self, other)

    def __or__(self, rules):
        if type(rules) != list: rules = [rules]
        return self.apply(*rules)

    def f_of(self, x):
        if self == x:
            return True
        for i in self.e:
            if isinstance(i, Expr) and i.f_of(x): return True
        return False

class Symbol:
    def __init__(self, ch):
        self.ch = ch

    def __str__(self):
        return self.ch

    def __eq__(self, other):
        return isinstance(other, Symbol) and self.ch == other.ch

class Function:
    def __init__(self, *args):
        self.args = args
        self.exp = None

    def __eq__(self, other):
        if self.exp == None:
            if isinstance(other, Expr):
                for i in self.args:
                    if not other.f_of(i): return False
                self.exp = other
                return True
            elif isinstance(other, Function):
                if self.args == other.args:
                    self.exp = other.exp
                    return True
                return False
        else:
            if isinstance(other, Expr):
                return self.exp == other
            elif isinstance(other, Function):
                return self.args == other.args and self.exp == other.exp
        return False

    def __str__(self):
        s = 'f('
        for i in self.args: s += str(i) + ','
        return s[:-1] + ')'

    def at(self, *args):
        if self.exp == None:
            return None
        assert len(args) == len(self.args)
        return self.exp.apply(*[Rule(self.args[i], args[i]) for i in range(len(self.args))])

    def __call__(self, *args, **kwargs):
        return self.at(*args)

class AbsSym:
    def __init__(self, ch):
        self.ch = ch

    def __str__(self):
        return self.ch + '_'

    def __eq__(self, other):
        self.img = other
        return True

class Rule:
    def __init__(self, a, b):
        self.a = a
        self.b = b
        self.has_abs = self.check_abs(self.b) #check for AbsSym in self.b (image)

    def __str__(self):
        return str(self.a) + '->' + str(self.b)

    def check_abs(self, expr):
        if isinstance(expr, AbsSym): return True
        if not isinstance(expr, Expr): return False
        for i in expr.e:
            if self.check_abs(i): return True
        return False

    def eval(self, expr=None):
        if not self.has_abs: return self.b
        if expr is None: expr = self.b
        if isinstance(expr, AbsSym): return expr.img
        if not isinstance(expr, Expr): return expr
        e = copy(expr)
        e.e = [self.eval(i) for i in expr.e]
        return e

class CommExp(Expr):
    def __init__(self, e):
        super().__init__(e)

    def __eq__(self, other):
        if type(self) != type(other): return False
        if len(self.e) != len(other.e): return False
        t = CommExp.sort_abs(self.e) # assumes AbsSym are always in self.e and not other.e
        for i in other.e:
            try: t.remove(i)
            except: return False
        return len(t) == 0

    def sort_abs(t):
        k = []
        for i in t:
            if isinstance(i, AbsSym): k.append(i)
            else: k.insert(0, i)
        return k

class AssocExp(Expr):
    def __init__(self, e):
        super().__init__(self.flatten(e))

    def flatten(self, e):
        r = []
        for i in e:
            if type(i) != type(self): r.append(i)
            else: r += i.e
        return r

#sub expr of NumExp should be NumExp
class NumExp(Expr):
    def __init__(self, e):
        super().__init__(e)

    def eval(self):
        pass

    #returns precedence (4 = sym;func , 3 = pow, 2 = mul, 1 = add; neg)
    def prec(self):
        pass

    def simplify(self):
        s = copy(self)
        s.e = [i.simplify() if isinstance(i, NumExp) else copy(i) for i in self.e]
        return s.simp_f()

    def simp_f(self):
        pass

    def apply(self, *rules: list):
        k = super().apply(*rules)
        return k.eval() if isinstance(k, NumExp) else k #this should possibly be in Expr.apply

#    def __eq__(self, other):
#        return Expr.__eq__(self, other) or other.__eq__(self)
        #this is because of cases like x == x^1 which would not be true if would be tested only by symbol's __eq__

    def __add__(self, other):
        return Add(self, other)

    def __radd__(self, other):
        return Add(other, self)

    def __neg__(self):
        return Neg(self)

    def __sub__(self, other):
        return self + -other

    def __rsub__(self, other):
        return other + -self

    def __mul__(self, other):
        return Mult(self, other)

    def __rmul__(self, other):
        return Mult(other, self)

    def __truediv__(self, other):
        return Fraction(self, other)

    def __rtruediv__(self, other):
        return Fraction(other, self)

    def __pow__(self, other):
        return Power(self, other)

    def __rpow__(self, other):
        return Power(other, self)

    def __repr__(self): # for ipython (notebook)
        try:
            from IPython.display import Latex, display
            display(Latex('$$' + self.lat().replace('$$', '') + '$$'))
        except:
            pass
        return super().__repr__()

    def __str__(self):
        return self.nstr()

    def prec_str(self, e): # e is child NumExp
        if not isinstance(e, NumExp) or e.prec() > self.prec():
            return str(e)
        return ('\\left(' + str(e) + '\\right)') if lat else '(' + str(e) + ')'

    def nstr(self): #num exp string
        pass

    #latex
    def lat(self):
        return self.nstr()

    def der_rule(self, x):
        pass

def is_num(x):
    return type(x) in [int, float, complex]

def der(exp, x):
    if not (is_num(exp) or isinstance(exp, NumExp)):
        return NotImplemented
    if is_num(exp) or not exp.f_of(x):
        return 0
    return exp.der_rule(x)

class NumSym(Symbol, NumExp):
    def __init__(self, ch):
        super().__init__(ch)
        self.e = []

    def prec(self):
        return 4

    def eval(self):
        return self

    def simp_f(self):
        return self

    def der_rule(self, x):
        assert self == x
        return 1

    def nstr(self):
        return self.ch

class Add(AssocExp, CommExp, NumExp):
    def __init__(self, *e):
        super().__init__(list(e))

    def prec(self):
        return 1

    def nstr(self):
        r = ''
        for i in self.e:
            r += self.prec_str(i) + '+' # can also just str(i) because add is lowest precidence
        return r[:-1]

    def eval(self):
        if len(self.e) == 0: return 0
        s = self.e[0]
        for i in self.e[1:]: s+= i
        return s

    def simp_f(self):
        # delete a - a
        i = 0
        while i < len(self.e) - 1:
            j = i + 1
            n = -self.e[i]
            while j < len(self.e):
                if n == self.e[j]:
                    del self.e[j]
                    del self.e[i]
                    i -= 1
                    break
                j += 1
            i += 1

        i = 0
        while i < len(self.e):
            if self.e[i] == 0:
                del self.e[i]
                i -= 1
            i += 1

        if len(self.e) == 0:
            return 0

        # convert a + a + ... + a -> n a
        i = 0
        while i < len(self.e) - 1:
            j = i + 1
            c = 1
            while j < len(self.e):
                if self.e[i] == self.e[j]:
                    c += 1
                    del self.e[j]
                    j -= 1
                j += 1
            if c > 1:
                self.e[i] = c*self.e[i]
            i += 1

        if len(self.e) == 1:
            return self.e[0]

        return self

    def der_rule(self, x):
        return Add(*[der(i, x) for i in self.e])

class Neg(NumExp):
    def __init__(self, e):
        super().__init__([e])

    def prec(self):
        return 1

    def nstr(self):
        return '-' + self.prec_str(self.e[0])

    def eval(self):
        return -self.e[0]

    def simp_f(self):
        if type(self.e[0]) is Add:
            return Add(*[-i for i in self.e[0].e])
        return self

    def __neg__(self):
        return self.e[0]

    def der_rule(self, x):
        return -der(self.e[0], x)

class Mult(AssocExp, CommExp, NumExp):
    def __init__(self, *e):
        super().__init__(list(e))

    def prec(self):
        return 2

    def nstr(self):
        r = ''
        for i in self.e:
            r += self.prec_str(i) + ('*' if not lat else '') # should possibly make nstr and lat for this
        return r[:-1]

    def eval(self):
        if len(self.e) == 0: return 1
        r = self.e[0]
        for i in self.e[1:]: r *= i
        return r

    def simp_f(self):
        for i in self.e:
            if i == 0:
                return 0

        #a * 1/a -> 1
        i = 0
        while i < len(self.e) - 1:
            j = i + 1
            n1 = 1/self.e[i]
            n2 = self.e[i] ** -1
            while j < len(self.e):
                if n1 == self.e[j] or n2 == self.e[j]:
                    del self.e[j]
                    self.e[i] = 1
                    break
                j += 1
            i += 1

        #1*a*b*1 -> a*b
        i = 0
        while i < len(self.e):
            if self.e[i] == 1:
                del self.e[i]
                i -= 1
            i += 1

        if len(self.e) == 0:
            return 1

        # convert a a ... a -> a^n
        i = 0
        while i < len(self.e) - 1:
            j = i + 1
            c = 1
            while j < len(self.e):
                if self.e[i] == self.e[j]:
                    c += 1
                    del self.e[j]
                    j -= 1
                j += 1
            if c > 1:
                self.e[i] = self.e[i] ** c
            i += 1

        if len(self.e) == 1:
            return self.e[0]
        return self

    #maybe expand should be a general function of NumExp
    def expand(self): #distribute
        for i in self.e:
            if type(i) is Add:
                t = self.e[:]
                t.remove(i)
                return Add(*[Mult(*(t + [x])) for x in i.e])
        return self

    def der_rule(self, x):
        s = []
        for i in range(len(self.e)):
            t = self.e[:]
            t[i] = der(t[i], x)
            s.append(Mult(*t))
        return Add(*s)

class Fraction(NumExp):
    def __init__(self, a, b):
        super().__init__([a, b])

    def prec(self):
        return 2

    def eval(self):
        return self.e[0] / self.e[1]

    def simp_f(self):
        if self.e[0] == 1: return self
        return (self.e[0] * (1/self.e[1])).expand().simplify()
        #return (self.e[0] * (self.e[1] ** -1)).expand().simplify()

    def __mul__(self, other):
        if isinstance(other, Fraction):
            return Fraction(self.e[0]*other.e[0], self.e[1]*other.e[1])
        return super().__mul__(other)

    def nstr(self):
        return self.prec_str(self.e[0]) + '/' + self.prec_str(self.e[1])

    def lat(self):
        return '\\frac{' + str(self.e[0]) +'}{' + str(self.e[1]) + '}'

    def der_rule(self, x):
        return Fraction(der(self.e[0], x)*self.e[1] - self.e[0]*der(self.e[1], x), self.e[1]**2)

class Power(NumExp):
    def __init__(self, a, b):
        super().__init__([a, b])
        self.simp_f() # maybe all num exp should simp in init (then should move self.a, self.b before super(), because it's used in simp_f)

    def prec(self):
        return 3

    def eval(self):
        return self.e[0] ** self.e[1]

    def simp_f(self):
        if self.e[1] == 1:
            return self.e[0]
        if type(self.e[0]) is Power:
            self.e[1] *= self.e[0].e[1]
            self.e[0] = self.e[0].e[0]
        return self

#    def __eq__(self, other):
#        return (self.e[1] == 1 and self.e[0] == other) or (self.e[1] == -1 and other == 1/self.e[0]) or super().__eq__(other)

    def nstr(self):
        return self.prec_str(self.e[0]) + '^' + self.prec_str(self.e[1])

    def lat(self):
        return self.prec_str(self.e[0]) + '^{' + self.prec_str(self.e[1]) + '}'

    def der_rule(self, x):
        return self.e[1]*(self.e[0] ** (self.e[1]-1))*der(self.e[0], x)

class ElemFunc(NumExp):
    def __init__(self, f, x):
        assert isinstance(x, NumExp) or is_num(x) # maybe not needed (for now needed because of __lat__ in elemfunc)
        super().__init__([x])
        self.f = f
        self.x = x

    def prec(self):
        return 4

    def eval(self):
        if is_num(self.x):
            return self.f(self.x)
        else:
            return self

    def simp_f(self):
        return self

    def der_rule(self, x):
        return self.f_der()*der(self.x, x)

    def f_der(self):
        pass

    def nstr(self):
        return type(self).__name__.lower() + '(' + str(self.x) + ')'

    def lat(self):
        return type(self).__name__.lower() + '\\left(' + str(self.x) + '\\right)'

########### Elementary funtions ###############
from cmath import sin, cos, tan, atan, exp, log, sqrt

#power should also maybe be an elem func

class Sin(ElemFunc):
    def __init__(self, x):
        super().__init__(sin, x)

    def f_der(self):
        return Cos(self.x)

class Cos(ElemFunc):
    def __init__(self, x):
        super().__init__(cos, x)

    def f_der(self):
        return -Sin(self.x)

class Tan(ElemFunc):
    def __init__(self, x):
        super().__init__(tan, x)

    def f_der(self):
        return 1/(Cos(self.x)**2)

class Atan(ElemFunc):
    def __init__(self, x):
        super().__init__(atan, x)

    def f_der(self):
        return 1/(1+self.x**2)

class Exp(ElemFunc):
    def __init__(self, x):
        super().__init__(exp, x)

    def f_der(self):
        return Exp(self.x)

class Log(ElemFunc):
    def __init__(self, x):
        super().__init__(log, x)

    def f_der(self):
        return 1/self.x

class Sqrt(ElemFunc):
    def __init__(self, x):
        super().__init__(sqrt, x)

    def f_der(self):
        return 1/(2*Sqrt(self.x))

    def lat(self):
        return '\\sqrt{' + self.prec_str(self.x) + '}'

###############################################

lat = False
F = Function
Q = Fraction

def NS(s):
    ss = s.split(' ')
    return (NumSym(i) for i in ss)

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