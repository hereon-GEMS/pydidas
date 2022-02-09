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
Package with widgets which allow the selection of a specific element.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2021, Malte Storm, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0"
__version__ = "0.1.0"
__maintainer__ = "Malte Storm"
__status__ = "Development"
__all__ = []

# import __all__ items from modules:
from .directory_explorer import *
from .hdf5_dataset_selector import *
from .radio_button_group import *
from .result_selector_for_output import *

# add modules' __all__ items to package's __all__ items and unclutter the
# namespace by deleting the module references:
from . import directory_explorer
__all__.extend(directory_explorer.__all__)
del directory_explorer

from . import hdf5_dataset_selector
__all__.extend(hdf5_dataset_selector.__all__)
del hdf5_dataset_selector

from . import radio_button_group
__all__.extend(radio_button_group.__all__)
del radio_button_group

from . import result_selector_for_output
__all__.extend(result_selector_for_output.__all__)
del result_selector_for_output
