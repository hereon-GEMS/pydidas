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
The data_io.implementations package includes imports/exporters for data
in different formats.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2021-2022, Malte Storm, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0"
__maintainer__ = "Malte Storm"
__status__ = "Development"
__all__ = []

# import __all__ items from modules:
from .figure_utils import *
from .roi_slice_manager import *

# add modules' __all__ items to package's __all__ items and unclutter the
# namespace by deleting the module references:
from . import figure_utils
__all__.extend(figure_utils.__all__)
del figure_utils

from . import roi_slice_manager
__all__.extend(roi_slice_manager.__all__)
del roi_slice_manager
