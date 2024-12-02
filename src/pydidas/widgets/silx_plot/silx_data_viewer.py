# This file is part of pydidas.
#
# Copyright 2024, Helmholtz-Zentrum Hereon
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
Module with custom Pydidas DataViews to be used in silx widgets.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2024, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"
__all__ = ["SilxDataViewer"]


from pydidas_qtcore import PydidasQApplication
from silx.gui.data.DataViewerFrame import DataViewerFrame
from silx.gui.data.DataViews import PLOT2D_MODE, _ImageView, _StackView

from ._data_views import _PydidasPlot2dView


class SilxDataViewer(DataViewerFrame):
    """
    A subclass of the DataViewerFrame to use custom Pydidas 2d data view.
    """

    def __init__(self, parent=None):
        self.__qtapp = PydidasQApplication.instance()
        super(SilxDataViewer, self).__init__(parent=parent)
        self.__pydidas_view = _PydidasPlot2dView(self)

        for _view in [_v for _v in self.availableViews() if isinstance(_v, _ImageView)]:
            _success = _view.replaceView(PLOT2D_MODE, self.__pydidas_view)
            if not _success:
                raise TypeError(
                    "Could not replace the default view in SilxDataViewer with the "
                    "custom pydidas view."
                )
        for _view in [_v for _v in self.availableViews() if isinstance(_v, _StackView)]:
            self.removeView(_view)

        # TODO : remove after silx update with pull request #4131 has been released
        indices = [
            self._DataViewerFrame__dataViewer._DataViewer__getStackIndex(_view)
            for _view in self.availableViews()
        ]
        if len(indices) != len(set(indices)):
            raise ValueError("There are duplicate stack indices.")
