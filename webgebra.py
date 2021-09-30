from copy import copy

class Exp:
    def __init__(self, e : list):
        self.e = e

    def __eq__(self, other):
        return type(self) == type(other) and self.e == other.e

    def apply(self, rules: list, rec=False):
        for r in rules:
            if self == r.a:
                return r.b
        s = self if rec else copy(self)
        s.e = self.e[:]
        for i in range(len(s.e)):
            if isinstance(s.e[i], Exp):
                s.e[i] = s.e[i].apply(rules, rec=True)
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
        return self.apply(rules)

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
        return type(self) == type(other) and CommExp.comp_e(self.e, other.e)

    def comp_e(e1, e2):
        if len(e1) != len(e2): return False
        for e in e1:
            if e not in e2:
                return False
        return True

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

    def simplify(self, rec=False):
        s = copy(self) if not rec else self
        s.e = [i.simplify(True) for i in self.e]
        return s.simp_f()

    def simp_f(self):
        pass

    def apply(self, rules: list, rec=False):
        k = super().apply(rules, rec=rec)
        return k.eval() if isinstance(k, NumExp) else k

    def __add__(self, other):
        return Add(self, other)

    def __radd__(self, other):
        return Add(other, self)

    def __neg__(self):
        return Neg(self)

    def __mul__(self, other):
        return Mult(self, other)

    def __rmul__(self, other):
        return Mult(other, self)

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
        return self

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

class Mult(AssocExp, CommExp, NumExp):
    def __init__(self, *e):
        super().__init__(list(e))

    def __str__(self):
        r = ''
        for i in self.e:
            r += str(i) + ' '
        return r[:-1]

    def eval(self):
        r=1
        for i in self.e:
            r *= i
        return r

    def simp_f(self):
        pass
        return self