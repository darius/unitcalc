"""
Parse definitions.units
"""

import re
from unitcalc import calc, standard_units

lines = open('definitions.units').read().splitlines()
lines = iter(lines[:5174])   # unicode troubles after this
def ok():
    for line in lines:
        while line.endswith('\\'):
            line = line[:-1] + next(lines)
        if line[:1].isalpha() or line[:1] == '%':
            line = re.sub(r'#.*', '', line)
            subject, definition = line.split(None, 1)
            if definition.startswith('!'):
                continue
            if any(ch in "()[],.'" for ch in subject):
                continue
            if "'" in definition:
                continue
            subject = re.sub(r'-$', '', subject)
            standard_units[subject] = calc(definition)
            print subject, definition
            print '  ', standard_units[subject]
            if subject != 'in' and not subject.endswith('-') and subject+'s' not in standard_units:
                # XXX horrible hack
                standard_units[subject+'s'] = calc(subject)

### ok()

## calc('(1)')
#. 1

## calc('5/6')
#. 0.8333333333333334
## calc('5 / ( 1 + 6)')
#. 0.7142857142857143
