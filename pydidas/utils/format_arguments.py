# -*- coding: utf-8 -*-
"""
Created on Mon May 31 09:53:08 2021

@author: ogurreck
"""

import re

def formatArguments(args, kwargs):
    """Function which accepts arguments and keyword arguments and converts
    them to a argparse-compatible list (for autoProcessing).
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
# _formatArguments

args = ['composite_nx=12']
kwargs = {'composite_ny': 10}

print(formatArguments(args, kwargs))