from wg_core import Expr, Symbol, AbsSym
from copy import copy

GLOBAL_LATEX = False


# sub expr of NumExp should be NumExp
class NumExp(Expr):
    def __init__(self, e):
        super().__init__(e)

    # returns precedence (4 = sym;func , 3 = pow, 2 = mul, 1 = add; neg)
    def prec(self):
        pass

    def eval(self):
        s = copy(self)
        s.e = [i.eval() if isinstance(i, NumExp) else copy(i) for i in self.e]
        return s.eval_f()

    def eval_f(self):
        return self  # maybe should be pass (for mandatory override)

    def simplify(self):
        s = copy(self)
        s.e = [i.simplify() if isinstance(i, NumExp) else copy(i) for i in self.e]
        return s.simp_f()

    def simp_f(self):
        pass

    # maybe expand should also be modeled with expand_f
    def expand(self):
        s = copy(self)
        s.e = [i.expand().eval() if isinstance(i, NumExp) else copy(i) for i in self.e]
        return s

    def apply(self, *rules: list):
        k = super().apply(*rules)
        return k.eval() if isinstance(k, NumExp) else k  # this should possibly be in Expr.apply

#    def __eq__(self, other):
#        return Expr.__eq__(self, other) or other.__eq__(self)
        # this is because of cases like x == x^1 which would not be true if would be tested only by symbol's __eq__

    def __repr__(self):  # for ipython (notebook)
        if GLOBAL_LATEX:
            from IPython.display import Latex, display
            display(Latex('$$' + str(self).replace('$$', '') + '$$'))
        return super().__repr__()

    def __str__(self):
        if GLOBAL_LATEX:
            return self.lat()
        return self.nstr()

    def prec_str(self, e):  # e is child NumExp
        if not isinstance(e, NumExp) or e.prec() > self.prec():
            return str(e)
        return ('\\left(' + str(e) + '\\right)') if GLOBAL_LATEX else '(' + str(e) + ')'

    def nstr(self):  # num exp string
        pass

    # latex
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

    def simp_f(self):
        return self

    def der_rule(self, x):
        assert self == x
        return 1

    def nstr(self):
        return self.ch


class NumAbsSym(AbsSym, NumExp):
    def __init__(self, ch):
        super().__init__(ch)

    def prec(self):
        return 4

    def nstr(self):
        return self.ch + '_'

    def lat(self):
        return self.ch
