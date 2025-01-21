# This file is part of pydidas.
#
# Copyright 2023 - 2025, Helmholtz-Zentrum Hereon
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
__copyright__ = "Copyright 2023 - 2025, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"


from .directory_explorer import *
from .hdf5_dataset_selector import *
from .raw_metadata_selector import *
from .result_selection_widget import *


__all__ = (
    directory_explorer.__all__
    + hdf5_dataset_selector.__all__
    + raw_metadata_selector.__all__
    + result_selection_widget.__all__
)

# Clean up the namespace:
del (
    directory_explorer,
    hdf5_dataset_selector,
    raw_metadata_selector,
    result_selection_widget,
)
