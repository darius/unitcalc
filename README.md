unitcalc
========

A calculator with units. Prerequisite: `pip install peglet`.

What it can do:

    >>> from unitcalc import *
    >>> load()
    >>> calc('3000 furlongs / fortnight')
    0.49892857142857144 m s^-1
    >>> calc('(2 * 6 ft * earthradius)^.5 in miles')
    2.9990780906608245  # The horizon from a 6-foot-high POV is 3 miles off.

You can calculate from Python code without converting your formulas to
strings:

    >>> hour, day = calc('hour'), calc('day')
    >>> Quantity(7) * day / hour
    168.0  # Hours in a week

The obviously nicer ``7 * day / hour`` wouldn't be hard to support.

Its knowledge comes from
[definitions.units](https://github.com/darius/unitcalc/blob/master/definitions.units)
from [GNU Units](http://en.wikipedia.org/wiki/GNU_Units). Since it was
a hacky 4-page hack, much of GNU Units didn't make it in, but
thousands of definitions useful to technical calculations did.

The code conceives of a value-with-units as a polynomial whose
variables are the basic uninterpreted units, such as 'm', meter. (This
means Fahrenheit and Centigrade aren't units it can know about, except
as temperature differences -- they have different zero-points.) A
slightly cute bit of
[implementation](https://github.com/darius/unitcalc/blob/master/unitcalc.py#L134):
it uses my parsing library [Peglet](https://github.com/darius/peglet)
to code just a scanner, with the actual parsing done by [precedence
climbing](https://github.com/darius/unitcalc/blob/master/precedence_climbing.py).

