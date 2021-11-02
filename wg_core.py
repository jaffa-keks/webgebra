from copy import copy


class Expr:
    def __init__(self, e: list):
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
        self.img = None

    def __str__(self):
        return self.ch + '_'

    def __eq__(self, other):
        if self.img is None:
            self.img = other
            return True
        return self.img == other


class Rule:
    def __init__(self, a, b):
        self.a = a
        self.b = b
        self.has_abs = self.check_abs(self.b)  # check for AbsSym in self.b (image)

    def __str__(self):
        return str(self.a) + '->' + str(self.b)

    def check_abs(self, expr):
        if isinstance(expr, AbsSym):  # AbsSym img is reset on rule creation
            expr.img = None
            return True
        if not isinstance(expr, Expr): return False
        for i in expr.e:
            if self.check_abs(i): return True  # beacuse this return true early, not all abssym.img are reset, FIX THIS
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
        t = CommExp.sort_abs(self.e)  # assumes AbsSym are always in self.e and not other.e
        for i in other.e:
            try:
                t.remove(i)
            except:
                return False
        return len(t) == 0

    def sort_abs(t):
        k = []
        for i in t:
            if isinstance(i, AbsSym):
                k.append(i)
            else:
                k.insert(0, i)
        return k


class AssocExp(Expr):
    def __init__(self, e):
        super().__init__(self.flatten(e))

    def flatten(self, e):
        r = []
        for i in e:
            if type(i) != type(self):
                r.append(i)
            else:
                r += i.e
        return r

    def __eq__(self, other):
        if type(other) != type(self): return False
        for i in range(len(self.e) - 1):
            if isinstance(self.e[i], AbsSym) and isinstance(self.e[i + 1], AbsSym):
                raise Exception  # can't have 2 consecutive AbsSym
        j = 0
        lr = []
        for i in range(len(self.e)):
            if isinstance(self.e[i], AbsSym): continue
            j0 = j
            while j <= len(other.e):
                if len(other.e) - j < len(self.e) - i:
                    return False
                if self.e[i] == other.e[j]:
                    if j < i: return False
                    if j - j0 > 0: lr.append((j0, j))
                    j += 1
                    break
                j += 1
        if j < len(other.e) and not isinstance(self.e[-1], AbsSym):
            return False
        if j < len(other.e): lr.append((j, len(other.e)))
        l = 0
        for i in self.e:
            if not isinstance(i, AbsSym): continue
            c = copy(self)
            c.e = other.e[lr[l][0]:lr[l][1]]
            # i.img = c
            if i != c: return False
            l += 1
        return True

# both associative and commutative
class Abelian(AssocExp, CommExp):
    def __init__(self, e: list):
        super().__init__(e)

    # again assuming AbsSym is in self, not in other (like in comm and assoc exp)
    def __eq__(self, other):
        if type(self) != type(other): return False
        if len(self.e) > len(other.e): return False
        #can only have 1 abs_sym in abelian expr
        k = CommExp.sort_abs(self.e)
        t = other.e[:]
        if isinstance(k[-2], AbsSym): raise Exception  # means that at least 2 elements are AbsSym
        for i in k[:-1]:
            try: t.remove(i)
            except: return False
        if not isinstance(k[-1], AbsSym):
            if len(t) > 1: return False
            return k[-1] == t[0]
        c = copy(self)
        c.e = t
        assert k[-1] == c
        return True