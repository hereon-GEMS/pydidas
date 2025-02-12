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
Package with subclassed silx widgets and actions.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2023 - 2025, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"

from . import silx_actions as actions
from ._silx_data_viewer import *
from .pydidas_masktools_widget import *
from .pydidas_plot1d import *
from .pydidas_plot2d import *
from .pydidas_plot2d_with_integration_regions import *
from .pydidas_plot_stack import *


__all__ = ["actions", "utilities"] + (
    pydidas_masktools_widget.__all__
    + _silx_data_viewer.__all__
    + pydidas_plot1d.__all__
    + pydidas_plot2d.__all__
    + pydidas_plot_stack.__all__
    + pydidas_plot2d_with_integration_regions.__all__
)

# Clean up the namespace:
del (
    pydidas_masktools_widget,
    pydidas_plot1d,
    pydidas_plot2d,
    pydidas_plot_stack,
    pydidas_plot2d_with_integration_regions,
    pydidas_position_info,  # noqa
    silx_actions,  # noqa
)
