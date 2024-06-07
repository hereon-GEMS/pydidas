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
Module with PydidasImageView class which adds configurations to the base silx ImageView.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2023 - 2024, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"
__all__ = ["PydidasDataViewerFrame"]


from silx.gui import qt
from silx.gui.data.DataViewerFrame import DataViewerFrame
from silx.gui.data.DataViewerSelector import DataViewerSelector

from ._data_views import PydidasDataViewer


class PydidasDataViewerFrame(DataViewerFrame):
    """
    A customized silx.gui.data.DataViewerFrame with an additional configuration.

    Parameters
    ----------
    **kwargs : dict
        Supported keyword arguments are:

        parent : Union[QWidget, None], optional
            The parent widget or None for no parent. The default is None.
        backend : Union[None, silx.gui.plot.backends.BackendBase], optional
            The silx backend to use. If None, this defaults to the standard
            silx settings. The default is None.
        show_cs_transform : bool, optional
            Flag whether to show the coordinate transform action. The default
            is True.
    """

    def __init__(self, parent=None):
        super(DataViewerFrame, self).__init__(parent)

        self._DataViewerFrame__dataViewer = PydidasDataViewer(self)
        # initialize views when `self.__dataViewer` is set
        self._DataViewerFrame__dataViewer.initializeViews()
        self._DataViewerFrame__dataViewer.setFrameShape(qt.QFrame.StyledPanel)
        self._DataViewerFrame__dataViewer.setFrameShadow(qt.QFrame.Sunken)
        self._DataViewerFrame__dataViewerSelector = DataViewerSelector(
            self, self._DataViewerFrame__dataViewer
        )
        self._DataViewerFrame__dataViewerSelector.setFlat(True)

        layout = qt.QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        layout.addWidget(self._DataViewerFrame__dataViewer, 1)
        layout.addWidget(self._DataViewerFrame__dataViewerSelector)
        self.setLayout(layout)

        self._DataViewerFrame__dataViewer.dataChanged.connect(
            self._DataViewerFrame__dataChanged
        )
        self._DataViewerFrame__dataViewer.displayedViewChanged.connect(
            self._DataViewerFrame__displayedViewChanged
        )
        self._DataViewerFrame__dataViewer.selectionChanged.connect(
            self._DataViewerFrame__selectionChanged
        )
