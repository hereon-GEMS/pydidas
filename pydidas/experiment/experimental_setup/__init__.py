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
The experimental_setup package includes a singleton class with the settings
for the experiment (detector, geometry) and importers/exporters for different
formats as well as a registry metaclass to handle actual imports/exports.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2021, Malte Storm, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0"
__version__ = "0.0.1"
__maintainer__ = "Malte Storm"
__status__ = "Development"
__all__ = []

# import __all__ items from modules:
from .experimental_setup import *
from .experimental_setup_io_meta import *

# add modules' __all__ items to package's __all__ items and unclutter the
# namespace by deleting the module references:
from . import experimental_setup
__all__.extend(experimental_setup.__all__)
del experimental_setup

from . import experimental_setup_io_meta
__all__.extend(experimental_setup_io_meta.__all__)
del experimental_setup_io_meta

# import all IO class files to have them registered in the registry metaclass.
import os
import importlib
import sys
_dir = os.path.dirname(__file__)
sys.path.insert(0, _dir)
_files = set(item for item in os.listdir(_dir)
             if (item.startswith('experimental_setup_io')
                 and not item[-7:] in ['base.py', 'meta.py']))

for _module in _files:
    _modname = 'pydidas.experiment.experimental_setup' + _module.strip('.py')
    _filepath = os.path.join(_dir, _module)
    _spec = importlib.util.spec_from_file_location(_modname, _filepath)
    _tmp_module = importlib.util.module_from_spec(_spec)
    _spec.loader.exec_module(_tmp_module)

del _tmp_module

del os
del sys
del importlib
