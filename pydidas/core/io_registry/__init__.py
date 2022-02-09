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
The core.io_registry package provides the framework for an extension-based
registry of classes which are managed by a metaclass.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2021, Malte Storm, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0"
__version__ = "0.1.0"
__maintainer__ = "Malte Storm"
__status__ = "Development"
__all__ = []


# import __all__ items from modules:
from .generic_io_base import *
from .generic_io_meta import *

# add modules' __all__ items to package's __all__ items and unclutter the
# namespace by deleting the module references:
from . import generic_io_base
__all__.extend(generic_io_base.__all__)
del generic_io_base

from . import generic_io_meta
__all__.extend(generic_io_meta.__all__)
del generic_io_meta
