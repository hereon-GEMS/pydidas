# This file is part of pydidas.
#
# pydidas is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Pydidas is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Pydidas. If not, see <http://www.gnu.org/licenses/>.

"""
The diffraction_exp_context package includes a singleton class with the settings
for a diffraction experiment (detector, geometry) and importers/exporters for different
formats as well as a registry metaclass to handle actual imports/exports.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2021-2022, Malte Storm, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0"
__maintainer__ = "Malte Storm"
__status__ = "Development"
__all__ = []

# import __all__ items from modules:
from .diffraction_exp_context import *
from .diffraction_exp_context_io_base import *
from .diffraction_exp_context_io_meta import *

# add modules' __all__ items to package's __all__ items and unclutter the
# namespace by deleting the module references:
from . import diffraction_exp_context

__all__.extend(diffraction_exp_context.__all__)
del diffraction_exp_context

from . import diffraction_exp_context_io_base

__all__.extend(diffraction_exp_context_io_base.__all__)
del diffraction_exp_context_io_base

from . import diffraction_exp_context_io_meta

__all__.extend(diffraction_exp_context_io_meta.__all__)
del diffraction_exp_context_io_meta

# Automatically find and import IO classes to have them registered
# with the Metaclass:
import os
import importlib

_dir = os.path.dirname(__file__)
_io_classes = set(
    item.strip(".py")
    for item in os.listdir(_dir)
    if (
        item.startswith("diffraction_exp_context_io")
        and not item[-7:] in ["base.py", "meta.py"]
    )
)

for _module in _io_classes:
    _module = importlib.import_module(f".{_module}", __package__)
    __all__ += _module.__all__

del _module
del os
del importlib