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
The core package defines base classes used throughout the full pydidas
suite.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2023, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0"
__maintainer__ = "Malte Storm"
__status__ = "Production"
__all__ = []

# import os as __os
# __os.environ["QT_API"] = "pyside6"
# __os.environ["FORCE_QT_API"] = "True"

import qtpy
print("Using QT: ", qtpy.API_NAME)


# import __all__ items from modules:
from .fontsize import *
from .pydidas_qapp import *
from .pydidas_splash_screen import *

# add modules' __all__ items to package's __all__ items and unclutter the
# namespace by deleting the module references:
from . import pydidas_qapp

__all__.extend(pydidas_qapp.__all__)
del pydidas_qapp

from . import pydidas_splash_screen

__all__.extend(pydidas_splash_screen.__all__)
del pydidas_splash_screen
