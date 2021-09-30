from copy import copy

class Exp:
    def __init__(self, e : list):
        self.e = e

    def __eq__(self, other):
        return type(self) == type(other) and self.e == other.e

    def apply(self, *rules: list):
        for r in rules:
            assert type(r) is Rule
            if self == r.a:
                return r.b
        s = copy(self)
        s.e = self.e[:]
        for i in range(len(s.e)):
            if isinstance(s.e[i], Exp):
                s.e[i] = s.e[i].apply(*rules)
            else:
                for r in rules:
                    if s.e[i] == r.a:
                        s.e[i] = r.b
        return s

    def __str__(self):
        r = 'Exp['
        for i in self.e: r += str(i) + ', '
        return r[:-2] + ']'

    def __rshift__(self, other):
        return Rule(self, other)

    def __or__(self, rules):
        if type(rules) != list: rules = [rules]
        return self.apply(*rules)

class Rule:
    def __init__(self, a, b):
        self.a = a
        self.b = b

    def __str__(self):
        return str(self.a) + '->' + str(self.b)

class CommExp(Exp):
    def __init__(self, e):
        super().__init__(e)

    def __eq__(self, other):
        if type(self) != type(other): return False
        if len(self.e) != len(other.e): return False
        t = other.e[:]
        for i in self.e:
            try: t.remove(i)
            except: return False
        return len(t) == 0

class AssocExp(Exp):
    def __init__(self, e):
        super().__init__(self.flatten(e))

    def flatten(self, e):
        r = []
        for i in e:
            if type(i) != type(self): r.append(i)
            else: r += i.e
        return r

class NumExp(Exp):
    def __init__(self, e):
        super().__init__(e)

    def eval(self):
        pass

    def simplify(self):
        s = copy(self)
        s.e = [i.simplify() if isinstance(i, NumExp) else i for i in self.e]
        return s.simp_f()

    def simp_f(self):
        pass

    def apply(self, *rules: list):
        k = super().apply(*rules)
        return k.eval() if isinstance(k, NumExp) else k

    def __eq__(self, other):
        return Exp.__eq__(self, other) or other.__eq__(self)
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

    #latex
    def __lat__(self):
        return str(self)

    def f_of(self, x):
        if self == x:
            return True
        for i in self.e:
            if isinstance(i, NumExp) and i.f_of(x): return True
        return False

    def der_rule(self, x):
        pass

def is_num(x):
    return isinstance(x, NumExp) or type(x) in [int, float, complex]

def der(exp, x):
    if not is_num(exp):
        return NotImplemented
    if not isinstance(exp, NumExp) or not exp.f_of(x):
        return 0
    return exp.der_rule(x)

class Symbol(NumExp):
    def __init__(self, ch):
        super().__init__([])
        self.ch = ch

    def eval(self):
        return self

    def simp_f(self):
        return self

    def __str__(self):
        return self.ch

    def __eq__(self, other):
        return type(other) == Symbol and self.ch == other.ch

    def der_rule(self, x):
        assert self == x
        return 1

class Add(AssocExp, CommExp, NumExp):
    def __init__(self, *e):
        super().__init__(list(e))

    def __str__(self):
        r = ''
        for i in self.e:
            r += str(i) + '+'
        return r[:-1]

    def eval(self):
        return sum(self.e)

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

    def __str__(self):
        return '-' + str(self.e[0])

    def eval(self):
        return -self.e[0]

    def simp_f(self):
        return self

    def __neg__(self):
        return self.e[0]

    def der_rule(self, x):
        return -der(self.e[0], x)

class Mult(AssocExp, CommExp, NumExp):
    def __init__(self, *e):
        super().__init__(list(e))

    def __str__(self):
        r = ''
        for i in self.e:
            r += str(i) + '*'
        return r[:-1]

    def eval(self):
        r=1
        for i in self.e:
            r *= i
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
        self.a = a
        self.b = b

    def eval(self):
        return self.a / self.b

    def simp_f(self):
        return (self.a * (self.b ** -1)).expand().simplify()

    def __str__(self):
        return str(self.a) + '/' + str(self.b)

    def der_rule(self, x):
        return Fraction(der(self.a, x)*self.b - self.a*der(self.b, x), self.b**2)

class Power(NumExp):
    def __init__(self, a, b):
        super().__init__([a, b])
        self.a = a
        self.b = b
        self.simp_f() # maybe all num exp should simp in init (then should move self.a, self.b before super(), because it's used in simp_f)

    def eval(self):
        return self.a ** self.b

    def simp_f(self):
        if self.b == 1:
            return self.a
        if type(self.a) is Power:
            self.b *= self.a.b
            self.a = self.a.a
        return self

    def __eq__(self, other):
        return (self.b == 1 and self.a == other) or (self.b == -1 and other == 1/self.a) or super().__eq__(other)

    def __str__(self):
        return str(self.a) + '^' + str(self.b)

    def der_rule(self, x):
        return self.b*(self.a ** (self.b-1))

################ FORMULAE #####################

def quad(a, b, c):
    x1 = (-b + (b ** 2 - 4 * a * c) ** (1 / 2)) / (2 * a)
    x2 = (-b - (b ** 2 - 4 * a * c) ** (1 / 2)) / (2 * a)
    return (x1, x2)









################################################