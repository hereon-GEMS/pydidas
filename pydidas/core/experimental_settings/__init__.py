# This file is part of pydidas.

# pydidas is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# Pydidas is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with Pydidas. If not, see <http://www.gnu.org/licenses/>.

"""
The experimental_settings sub-package includes the ExperimentalSettings 
singleton and importers / exporters for it.
"""
__author__      = "Malte Storm"
__copyright__   = "Copyright 2021, Malte Storm, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0"
__version__ = "0.0.1"
__maintainer__ = "Malte Storm"
__status__ = "Development"
__all__ = []

from . import experimental_settings_io_meta
from .experimental_settings_io_meta import *

from . import experimental_settings_io_base
from .experimental_settings_io_base import *

from . import experimental_settings
from .experimental_settings import *

__all__ += experimental_settings_io_meta.__all__
__all__ += experimental_settings_io_base.__all__
__all__ += experimental_settings.__all__

# Unclutter namespace: remove modules from namespace:
del experimental_settings_io_meta
del experimental_settings_io_base
del experimental_settings

# Automatically find and import IO classes to have them registered
# with the Metaclass:
import os
from importlib import import_module
_io_classes = [name.replace('.py', '')
               for name in os.listdir(os.path.dirname(__file__))
               if name.startswith('experimental_settings_io_')]
# remove the two generic modules with the metaclass and baseclass:
_io_classes.remove('experimental_settings_io_base')
_io_classes.remove('experimental_settings_io_meta')

for _module in _io_classes:
    _module = import_module(f'.{_module}', __package__)
    __all__ += _module.__all__

del os
del import_module
