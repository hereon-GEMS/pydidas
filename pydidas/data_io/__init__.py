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
The data_io subpackage includes functionality to load and save data in
various formats.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2021-2022, Malte Storm, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0"
__maintainer__ = "Malte Storm"
__status__ = "Development"
__all__ = []

# import sub-packages:
from . import implementations
from . import low_level_readers
from . import utils

# import __all__ items from modules:
from .composite_image import *
from .import_export import *
from .io_master import *
from .roi_controller import *
from .roi_controller_1d import *

# add modules' __all__ items to package's __all__ items and unclutter the
# namespace by deleting the module references:
from . import composite_image
__all__.extend(composite_image.__all__)
del composite_image

from . import import_export
__all__.extend(import_export.__all__)
del import_export

from . import io_master
__all__.extend(io_master.__all__)
del io_master

from . import roi_controller
__all__.extend(roi_controller.__all__)
del roi_controller

from . import roi_controller_1d
__all__.extend(roi_controller_1d.__all__)
del roi_controller_1d
