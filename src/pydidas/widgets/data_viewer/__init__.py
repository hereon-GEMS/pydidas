# This file is part of pydidas.
#
# Copyright 2025, Helmholtz-Zentrum Hereon
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
Package with subclassed silx widgets and actions.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2025, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"


from .axes_selector import AxesSelector
from .data_axis_selector import DataAxisSelector
from .data_viewer import DataViewer
from .table_with_result_datasets import TableWithResultDatasets


__all__ = [
    axes_selector.__all__
    + data_axis_selector.__all__
    + data_viewer.__all__
    + table_with_result_datasets.__all__
]

# Clean up the namespace:
del (
    axes_selector,
    data_axis_selector,
    data_viewer,
    table_with_result_datasets,
)
