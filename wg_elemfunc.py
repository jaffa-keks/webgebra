from wg_num import NumExp, is_num, der


class ElemFunc(NumExp):
    def __init__(self, f, x):
        assert isinstance(x, NumExp) or is_num(x)  # maybe not needed (for now needed because of __lat__ in elemfunc)
        super().__init__([x])
        self.f = f

    def x(self):
        return self.e[0]

    def prec(self):
        return 4

    def eval_f(self):
        if is_num(self.x()):
            return self.f(self.x())
        else:
            return self

    def simp_f(self):
        return self

    def der_rule(self, x):
        return self.f_der() * der(self.x(), x)

    def f_der(self):
        pass

    def nstr(self):
        return type(self).__name__.lower() + '(' + str(self.x()) + ')'

    def lat(self):
        return type(self).__name__.lower() + '\\left(' + str(self.x()) + '\\right)'


########### Elementary funtions ###############
from cmath import sin, cos, tan, atan, exp, log, sqrt


# power should also maybe be an elem func

class Sin(ElemFunc):
    def __init__(self, x):
        super().__init__(sin, x)

    def f_der(self):
        return Cos(self.x())


class Cos(ElemFunc):
    def __init__(self, x):
        super().__init__(cos, x)

    def f_der(self):
        return -Sin(self.x())


class Tan(ElemFunc):
    def __init__(self, x):
        super().__init__(tan, x)

    def f_der(self):
        return 1 / (Cos(self.x()) ** 2)


class Atan(ElemFunc):
    def __init__(self, x):
        super().__init__(atan, x)

    def f_der(self):
        return 1 / (1 + self.x() ** 2)


class Exp(ElemFunc):
    def __init__(self, x):
        super().__init__(exp, x)

    def f_der(self):
        return Exp(self.x())

    def lat(self):
        return 'e^{' + self.prec_str(self.x()) + '}'


class Log(ElemFunc):
    def __init__(self, x):
        super().__init__(log, x)

    def f_der(self):
        return 1 / self.x


class Sqrt(ElemFunc):
    def __init__(self, x):
        super().__init__(sqrt, x)

    def f_der(self):
        return 1 / (2 * Sqrt(self.x()))

    def lat(self):
        return '\\sqrt{' + str(self.x()) + '}'
