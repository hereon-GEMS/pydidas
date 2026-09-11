# This file is part of pydidas.
#
# Copyright 2026, Helmholtz-Zentrum Hereon
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
The silx module holds functions and classes exposed by the silx package,
which are lazily imported to reduce initial loading time.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2026, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"
__all__ = [
    "BackendMatplotlib",
    "Colormap",
    "ImageToolBar",
    "Plot1D",
    "Plot2D",
    "PlotAction",
    "PlotToolButton",
    "Scatter",
    "plot_items",
]


from typing import TYPE_CHECKING

from pydidas.core.lazy_imports.lazy_objects import LazyObject


if TYPE_CHECKING:
    from silx.gui.colors import Colormap
    from silx.gui.plot import Plot1D, Plot2D
    from silx.gui.plot import items as plot_items
    from silx.gui.plot.actions import PlotAction
    from silx.gui.plot.backends.BackendMatplotlib import BackendMatplotlib
    from silx.gui.plot.items import Scatter
    from silx.gui.plot.PlotToolButtons import PlotToolButton
    from silx.gui.plot.tools import ImageToolBar
else:
    BackendMatplotlib = LazyObject(
        "silx.gui.plot.backends.BackendMatplotlib", "BackendMatplotlib"
    )
    Colormap = LazyObject("silx.gui.colors", "Colormap")
    ImageToolBar = LazyObject("silx.gui.plot.tools", "ImageToolBar")
    Plot1D = LazyObject("silx.gui.plot", "Plot1D")
    Plot2D = LazyObject("silx.gui.plot", "Plot2D")
    PlotAction = LazyObject("silx.gui.plot.actions", "PlotAction")
    PlotToolButton = LazyObject("silx.gui.plot.PlotToolButtons", "PlotToolButton")
    Scatter = LazyObject("silx.gui.plot.items", "Scatter")
    plot_items = LazyObject("silx.gui.plot", "items")
