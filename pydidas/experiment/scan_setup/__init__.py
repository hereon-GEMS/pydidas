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
The scan_setup package includes a singleton class with the scan settings and
importers/exporters for different formats as well as a registry metaclass to
handle actual imports/exports.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2021, Malte Storm, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0"
__version__ = "0.0.1"
__maintainer__ = "Malte Storm"
__status__ = "Development"
__all__ = []

# import __all__ items from modules:
from .scan_setup import *
from .scan_setup_io_meta import *

# add modules' __all__ items to package's __all__ items and unclutter the
# namespace by deleting the module references:
from . import scan_setup
__all__.extend(scan_setup.__all__)
del scan_setup

from . import scan_setup_io_meta
__all__.extend(scan_setup_io_meta.__all__)
del scan_setup_io_meta

# import all IO class files to have them registered in the registry metaclass.
import os
import importlib
_dir = os.path.dirname(__file__)
_files = set(item for item in os.listdir(_dir)
             if (item.startswith('scan_setup_io')
                 and not item[-7:] in ['base.py', 'meta.py']))

for _module in _files:
    _spec = importlib.util.spec_from_file_location(
        _module.strip('.py'), os.path.join(_dir, _module))
    _tmp_module = importlib.util.module_from_spec(_spec)
    _spec.loader.exec_module(_tmp_module)
    del _tmp_module

del os
del importlib
