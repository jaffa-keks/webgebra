from wg_core import AssocExp, CommExp, Abelian, AbsSym
from wg_num import NumExp, der, is_num


class Add(Abelian, NumExp):
    def __init__(self, *e):
        super().__init__(list(e))

    def prec(self):
        return 1

    def nstr(self):
        r = ''
        for i in self.e:
            if isinstance(i, Neg) or (is_num(i) and type(i) != complex and i < 0):
                r = r[:-1]
                r += '-' + self.prec_str(-i) + '+'
            else:
                r += self.prec_str(i) + '+' # can also just str(i) because add is lowest precidence
        return r[:-1]

    def eval_f(self):
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

    def eval_f(self):
        return -self.e[0]

    def simp_f(self):
        if type(self.e[0]) is Add:
            return Add(*[-i for i in self.e[0].e])
        return self

    def expand(self):
        if type(self.e[0]) == Add:
            return Add(*[-i for i in self.e[0].e])
        return super().expand()

    def __neg__(self):
        return self.e[0]

    def der_rule(self, x):
        return -der(self.e[0], x)


class Mult(Abelian, NumExp):
    def __init__(self, *e):
        super().__init__(list(e))

    def prec(self):
        return 2

    def nstr(self):
        r = ''
        for i in self.e:
            r += self.prec_str(i) + '*'
        return r[:-1]

    def lat(self):
        r = ''
        for i in self.e:
            r += self.prec_str(i)
        return r

    def eval_f(self):
        if len(self.e) == 0: return 1
        r = self.e[0]
        for i in self.e[1:]: r *= i
        return r

    def simp_f(self):
        for i in self.e:
            if i == 0:
                return 0

        # a * 1/a -> 1
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

        # 1*a*b*1 -> a*b
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
        xn = AbsSym('')
        while i < len(self.e) - 1:
            j = i + 1
            c = 1
            while j < len(self.e):
                if self.e[i] == self.e[j]:
                    c += 1
                    del self.e[j]
                    j -= 1
                elif Power(self.e[i], xn) == self.e[j]:
                    c += xn.img
                    del self.e[j]
                    j -= 1
                j += 1
            if c > 1:
                self.e[i] = self.e[i] ** c
            i += 1

        if len(self.e) == 1:
            return self.e[0]
        return self

    def expand(self):  # distribute
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

    def eval_f(self):
        return self.e[0] / self.e[1]

    def simp_f(self):
        if self.e[1] == 1: return self.e[0]
        return self
        #return (self.e[0] * (1/self.e[1])).expand().simplify()
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
        self.simp_f()  # maybe all num exp should simp in init (then should move self.a, self.b before super(), because it's used in simp_f)

    def prec(self):
        return 3

    def eval_f(self):
        return self.e[0] ** self.e[1]

    def simp_f(self):
        if self.e[1] == 0:
            return 1
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


NumExp.__add__ = lambda a, b: Add(a, b)
NumExp.__radd__ = lambda a, b: Add(b, a)
NumExp.__neg__ = lambda a: Neg(a)
NumExp.__mul__ = lambda a, b: Mult(a, b)
NumExp.__rmul__ = lambda a, b: Mult(b, a)
NumExp.__sub__ = lambda a, b: Add(a, -b)
NumExp.__rsub__ = lambda a, b: Add(b, -a)
NumExp.__truediv__ = lambda a, b: Fraction(a, b)
NumExp.__rtruediv__ = lambda a, b: Fraction(b, a)
NumExp.__pow__ = lambda a, b: Power(a, b)
NumExp.__rpow__ = lambda a, b: Power(b, a)