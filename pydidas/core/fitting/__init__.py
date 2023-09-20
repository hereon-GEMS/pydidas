# This file is part of pydidas.
#
# Copyright 2023, Helmholtz-Zentrum Hereon
# SPDX-License-Identifier: GPL-3.0-only
#
# pydidas is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 3 as
# published by the Free Software Foundation.
#
# Pydidas is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Pydidas. If not, see <http://www.gnu.org/licenses/>.

"""
The core.fitting package defines generic functions for fitting.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2023, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"
__all__ = []

# import __all__ items from modules:
from .fit_func_meta import *
from .fit_func_base import *


# Automatically find and import fit function classes to have them registered
# with the Metaclass:
import os
import importlib

_dir = os.path.dirname(__file__)
_fit_classes = set(
    item.strip(".py")
    for item in os.listdir(_dir)
    if (
        os.path.isfile(os.path.join(_dir, item))
        and item not in ["__init__.py", "fit_func_base.py", "fit_func_meta.py"]
    )
)

for __module in _fit_classes:
    __module = importlib.import_module(f".{__module}", __package__)
    __all__ += __module.__all__

del os
del importlib
