from wg_core import Expr
from wg_numops import Add, Mult

class Polynomial(Expr):
    def __init__(self, *k):
        super().__init__(list(k))

    def dg(self):
        return len(self.e) - 1

    def trim(self):
        if self.e[-1] != 0: return self
        for i in range(len(self.e)):
            if self.e[-(i+1)] != 0:  # maybe polynomial could be on an arbitrary field, and then instead of 0 use field.identity
                return Polynomial(*self.e[:-i])
        return 0

    def as_f(self, x):
        return Add(*[self.e[i]*x**i for i in range(len(self.e))][::-1])

    def __add__(self, other):
        a, b = (self, other) if self.dg() >= other.dg() else (other, self)
        e = [a.e[i] + b.e[i] for i in range(len(b.e))]
        e += a.e[len(b.e):]
        return Polynomial(*e).trim()

    def __mul__(self, other):
        u = [0] * (self.dg() + other.dg() + 1)
        for n in range(len(u)):
            b1 = max(n - self.dg(), 0)
            b2 = min(n, other.dg())
            for m in range(b1, b2+1):
                u[n] += self.e[n-m]*other.e[m]
        return Polynomial(*u)

    def __pow__(self, power):
        p = Polynomial(1)
        for i in range(power):
            p *= self
        return p

class FactoredPolynomial(Expr):
    def __init__(self, *zeros):
        super().__init__(list(zeros))
        self.z = {}
        for z in zeros:
            try: self.z[z] += 1
            except: self.z[z] = 1

    # x : NumExp
    def as_f(self, x):
        return Mult(*[(x - i)**self.z[i] for i in self.z.keys()])

    def expand(self):
        k = Polynomial(1)
        for i in self.z.keys():
            k *= Polynomial(1, -i) ** self.z[i]
        return k

class Rational(Expr):
    def __init__(self, p, q):
        super().__init__([p, q])

    # need to make fraction decompositon somehow
    def pfd(self):
        assert isinstance(self.e[1], FactoredPolynomial)
        # FINISH THIS

print(FactoredPolynomial(1, 1).expand())