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
Module with PydidasPlot1D class which adds configurations to the base silx Plot1D.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2021-2022, Malte Storm, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0"
__maintainer__ = "Malte Storm"
__status__ = "Development"
__all__ = ["PydidasPlot1D"]

from qtpy import QtCore
from silx.gui.plot import Plot1D


class PydidasPlot1D(Plot1D):
    """
    A customized silx.gui.plot.Plot1D with an additional configuration.
    """

    def __init__(self, parent=None, backend=None):
        Plot1D.__init__(self, parent, backend)

        self.getRoiAction().setVisible(False)
        self.getFitAction().setVisible(False)

        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)
