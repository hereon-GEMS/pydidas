# This file is part of pydidas.
#
# Copyright 2023 - 2026, Helmholtz-Zentrum Hereon
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
Module with various utility functions for widgets.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2023 - 2026, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"
__all__ = [
    "DataAxisSelector",
    "DataViewer",
    "PydidasPlot2D",
    "PydidasPlot2DwithIntegrationRegions",
    "PydidasPlotStack",
]

from typing import TYPE_CHECKING

from pydidas.core.lazy_imports.lazy_objects import LazyObject


if TYPE_CHECKING:
    from pydidas.widgets.data_viewer import DataAxisSelector, DataViewer
    from pydidas.widgets.silx_plot import (
        PydidasPlot2D,
        PydidasPlot2DwithIntegrationRegions,
        PydidasPlotStack,
    )
else:
    DataAxisSelector = LazyObject("pydidas.widgets.data_viewer", "DataAxisSelector")
    DataViewer = LazyObject("pydidas.widgets.data_viewer", "DataViewer")
    PydidasPlot2D = LazyObject("pydidas.widgets.silx_plot", "PydidasPlot2D")
    PydidasPlot2DwithIntegrationRegions = LazyObject(
        "pydidas.widgets.silx_plot", "PydidasPlot2DwithIntegrationRegions"
    )
    PydidasPlotStack = LazyObject("pydidas.widgets.silx_plot", "PydidasPlotStack")
