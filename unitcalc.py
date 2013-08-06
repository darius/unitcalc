"""
Prototype of unit calculator.
Dependencies:
pip install peglet

To do:
make 'x in y' carry along y's units instead of being scalar
friendlier error reporting
add more standard units to convert between (use units.txt?)
"""

from __future__ import division
import operator

from peglet import Parser, join
from precedence_climbing import make_parse_primary, make_parse_expr

class Quantity(object):
    "A value with units."

    def __init__(self, value, units={}):
        self.value = value
        self.units = {u: p for u, p in units.items() if p != 0}

    def __repr__(self):
        units = show_units(self.units)
        return '%r %s' % (self.value, units) if units else repr(self.value)

    def __neg__(self):
        return Quantity(-self.value, self.units)

    def __add__(self, other):
        assert isinstance(other, Quantity)
        check_compatible(self, other)
        return Quantity(self.value + other.value, self.units)

    def __sub__(self, other):
        assert isinstance(other, Quantity)
        check_compatible(self, other)
        return Quantity(self.value - other.value, self.units)

    def __mul__(self, other):
        assert isinstance(other, Quantity)
        units = {u: self.units.get(u, 0) + other.units.get(u, 0)
                 for u in set(self.units.keys() + other.units.keys())}
        return Quantity(self.value * other.value, units)

    def __div__(self, other):
        assert isinstance(other, Quantity)
        units = {u: self.units.get(u, 0) - other.units.get(u, 0)
                 for u in set(self.units.keys() + other.units.keys())}
        return Quantity(self.value / other.value, units)

    def __truediv__(self, other):
        return self.__div__(other)

    def __pow__(self, other):
        other_value = as_scalar(other)
        units = {u: 2*p for u, p in self.units.items()}
        return Quantity(self.value ** other_value, units)

def check_compatible(u1, u2):
    if u1.units.keys() != u2.units.keys():
        raise ValueError("Different units", u1, u2)

def show_units(units):
    if not units: return ''
    return ' '.join(u if p == 1 else '%s^%d' % (u, p) 
                    for u, p in sorted(units.items()))

def as_scalar(q):
    if not isinstance(q, Quantity): return q
    assert not q.units
    return q.value

## Quantity(5)
#. 5
## Quantity(5, {'m': 1})
#. 5 m
## Quantity(5, {'m': 1}) + Quantity(137, {'m': 1})
#. 142 m
## Quantity(5, {'m': 1}) * Quantity(2, {'m': 1, 's': -1})
#. 10 m^2 s^-1

def in_units(q, u):
    check_compatible(q, u)
    return q / u    # getting a scalar out, which is less than ideal

infix_ops = {
  # lprec means left-precedence, rprec means right
  # token  lprec rprec     op
    '+':    (10,   11,   operator.add), # left-associative
    '-':    (10,   11,   operator.sub),
    'in':   (15,   16,   in_units),       # XXX should be nonassociative
    '*':    (20,   21,   operator.mul),
    '/':    (20,   21,   operator.div), 
    '^':    (30,   30,   operator.pow), # right-associative
}

prefix_ops = {
  # token  pprec    op
    '-':    (20,  lambda n: -n),
    '/':    (25,  lambda n: Quantity(1) / n), # XXX right precedence?
}

## calc('/ m')
#. 1.0 m^-1

standard_units = dict(foot = Quantity(0.3048, {'m':1}))

def make_unit(name):
    return standard_units.get(name, Quantity(1, {name: 1}))

parse_primary = make_parse_primary(parse_literal=lambda x: x, prefix_ops=prefix_ops)

token_grammar = r"""
expr     = _ tokens
tokens   = token tokens
         | 
token    = operator | unit | floatlit | intlit

operator = ([-+*/^]) _
         | (in)\b _
unit     = ([A-Za-z]+) _ make_unit

floatlit = float _  join make_float Quantity
intlit   = int _    join make_int Quantity

float    = int frac exp
         | int frac
         | int exp
int      = (-[1-9]) digits
         | (-) digit
         | ([1-9]) digits
         | digit
frac     = ([.]) digits
exp      = ([eE][+-]?) digits
digits   = (\d+)
digit    = (\d)

_        = \s*
"""

scan_em = Parser(token_grammar, make_int=int, make_float=float, **globals())

def calc(string):
    tokens = iter(scan_em(string))
    def scan(): scan.token = next(tokens, None)
    scan()

    parse_expr = make_parse_expr(scan, infix_ops, parse_primary)
    result = parse_expr(0)
    assert scan.token is None, "Input not fully consumed"
    return result

## calc('5')
#. 5
## calc('5 m')
#. 5 m
## calc('5 m + 3 m')
#. 8 m
## calc('52.1 m * 3 m')
#. 156.3 m^2
## calc('5 m / s')
#. 5.0 m s^-1
## calc('5 m / s^2')
#. 5.0 m s^-2
## calc('-5')
#. -5
## calc('')  # XXX should complain
## calc('20 m / s^2 in 10   m/s^2')
#. 2.0
## calc('2 in 1')
#. 2.0
## calc('2 foot')
#. 0.6096 m
## calc('3 m in foot')
#. 9.84251968503937

## calc('-3 - 2 - 1')
#. -6
