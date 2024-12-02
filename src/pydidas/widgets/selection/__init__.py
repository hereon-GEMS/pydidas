# This file is part of pydidas.
#
# Copyright 2023 - 2024, Helmholtz-Zentrum Hereon
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
Package with widgets which allow the selection of a specific element.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2023 - 2024, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"
__all__ = []

# import __all__ items from modules:
from .directory_explorer import *
from .hdf5_dataset_selector import *
from .raw_metadata_selector import *
from .result_selection_widget import *

# add modules' __all__ items to package's __all__ items and unclutter the
# namespace by deleting the module references:
from . import directory_explorer

__all__.extend(directory_explorer.__all__)
del directory_explorer

from . import hdf5_dataset_selector

__all__.extend(hdf5_dataset_selector.__all__)
del hdf5_dataset_selector

from . import raw_metadata_selector

__all__.extend(raw_metadata_selector.__all__)
del raw_metadata_selector

from . import result_selection_widget

__all__.extend(result_selection_widget.__all__)
del result_selection_widget
