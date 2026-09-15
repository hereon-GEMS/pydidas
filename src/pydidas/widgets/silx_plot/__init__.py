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
Package with subclassed silx widgets and actions.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2023 - 2026, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"
__all__ = [
    "PydidasMaskToolsWidget",
    "PydidasPlot1D",
    "PydidasPlot2D",
    "PydidasPlot2DwithIntegrationRegions",
    "PydidasPlotStack",
    "silx_actions",
    "utilities",
]


from typing import TYPE_CHECKING

from . import utilities
from pydidas.core.lazy_imports.lazy_objects import LazyModule, LazyObject


class SilxLazyObject(LazyObject):
    """
    A subclass of LazyObject that patches the silx ColorBar
    class when it is imported.
    """

    def _resolve(self) -> object:
        utilities.ensure_colorbar_patched()
        return super()._resolve()


class SilxLazyModule(LazyModule):
    """
    A subclass of LazyModule that patches the silx ColorBar
    class when it is imported.
    """

    def _resolve(self) -> object:
        utilities.ensure_colorbar_patched()
        return super()._resolve()


if TYPE_CHECKING:
    from . import silx_actions
    from .pydidas_masktools_widget import PydidasMaskToolsWidget
    from .pydidas_plot1d import PydidasPlot1D
    from .pydidas_plot2d import PydidasPlot2D
    from .pydidas_plot2d_with_integration_regions import (
        PydidasPlot2DwithIntegrationRegions,
    )
    from .pydidas_plot_stack import PydidasPlotStack
else:
    silx_actions = SilxLazyModule("pydidas.widgets.silx_plot.silx_actions")
    PydidasPlot1D = SilxLazyObject(
        "pydidas.widgets.silx_plot.pydidas_plot1d", "PydidasPlot1D"
    )
    PydidasMaskToolsWidget = SilxLazyObject(
        "pydidas.widgets.silx_plot.pydidas_masktools_widget", "PydidasMaskToolsWidget"
    )
    PydidasPlot2D = SilxLazyObject(
        "pydidas.widgets.silx_plot.pydidas_plot2d", "PydidasPlot2D"
    )
    PydidasPlot2DwithIntegrationRegions = SilxLazyObject(
        "pydidas.widgets.silx_plot.pydidas_plot2d_with_integration_regions",
        "PydidasPlot2DwithIntegrationRegions",
    )
    PydidasPlotStack = SilxLazyObject(
        "pydidas.widgets.silx_plot.pydidas_plot_stack", "PydidasPlotStack"
    )
