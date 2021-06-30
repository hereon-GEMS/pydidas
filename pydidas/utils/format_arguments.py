# This file is part of pydidas.

# pydidas is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# Foobar is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with Foobar.  If not, see <http://www.gnu.org/licenses/>.

import re

def formatArguments(args, kwargs):
    """Function which accepts arguments and keyword arguments and converts
    them to a argparse-compatible list.
    """
    newArgs = [None]
    for item, key in kwargs.items():
        if key is True:
            newArgs.append(f'--{item}')
        else:
            newArgs.append(f'-{item}')
            if not isinstance(key, str):
                newArgs.append(str(key))
            else:
                newArgs.append(key)
    for arg in args:
        if not isinstance(arg, str) :
            arg = str(arg)
        if '=' in arg or ' ' in arg:
            tmp = [item for item in re.split(' |=', arg) if item != '']
            if tmp[0][0] != '-':
                tmp[0] = '-{}'.format(tmp[0])
            newArgs += tmp
        else:
            newArgs.append(arg)
    return newArgs
