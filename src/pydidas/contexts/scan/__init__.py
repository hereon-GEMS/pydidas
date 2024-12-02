# This file is part of pydidas.
#
# Copyright 2024, Helmholtz-Zentrum Hereon
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
The scan_context package includes a singleton class with the scan settings and
importers/exporters for different formats as well as a registry metaclass to
handle actual imports/exports.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2024, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"
__all__ = []

# import __all__ items from modules:
from .scan import *
from .scan_context import *
from .scan_io_base import *
from .scan_io import *

# add modules' __all__ items to package's __all__ items and unclutter the
# namespace by deleting the module references:
from . import scan

__all__.extend(scan.__all__)
del scan

from . import scan_context

__all__.extend(scan_context.__all__)
del scan_context

from . import scan_io_base

__all__.extend(scan_io_base.__all__)
del scan_io_base

from . import scan_io

__all__.extend(scan_io.__all__)
del scan_io

# Automatically find and import IO classes to have them registered
# with the Metaclass:
import os
import importlib

_dir = os.path.dirname(__file__)
_io_classes = set(
    item.strip(".py")
    for item in os.listdir(_dir)
    if (item.startswith("scan_io") and item[-7:] not in ["base.py", "meta.py"])
)

for _module in _io_classes:
    _module = importlib.import_module(f".{_module}", __package__)
    __all__ += _module.__all__

del _module
del os
del importlib
