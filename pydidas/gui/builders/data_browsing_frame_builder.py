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
Module with the DataBrowsingFrameBuilder class which is used to populate
the DataBrowsingFrame with widgets.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2021-2022, Malte Storm, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0"
__maintainer__ = "Malte Storm"
__status__ = "Development"
__all__ = ["DataBrowsingFrameBuilder"]

from qtpy import QtWidgets, QtCore
import qtawesome as qta
from silx.gui.plot.ImageView import ImageView

from ...widgets import BaseFrame
from ...widgets.selection import DirectoryExplorer, Hdf5DatasetSelector


class DataBrowsingFrameBuilder(BaseFrame):
    """
    Mix-in class which includes the build_frame method to populate the
    base class's UI and initialize all widgets.
    """

    def __init__(self, parent=None, **kwargs):
        BaseFrame.__init__(self, parent, **kwargs)

    def build_frame(self):
        """
        Build the frame and create all required widgets.
        """
        self.create_label(None, "Data browser", fontsize=14, bold=True)

        _button_iconsize = 25
        self._widgets["selection"] = QtWidgets.QFrame()
        self._widgets["selection"].setSizePolicy(
            QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Expanding
        )
        self._widgets["selection"].setLayout(QtWidgets.QGridLayout())
        self._widgets["selection"].layout().setRowStretch(0, 10)

        self.create_any_widget(
            "tree",
            DirectoryExplorer,
            parent_widget=self._widgets["selection"],
            gridPos=(0, 0, 3, 1),
        )
        self.create_any_widget(
            "hdf_dset",
            Hdf5DatasetSelector,
            parent_widget=self._widgets["selection"],
            gridPos=(3, 0, 1, 1),
        )
        self.create_button(
            "but_minimize",
            "",
            icon=qta.icon("fa.chevron-left"),
            iconSize=QtCore.QSize(_button_iconsize, _button_iconsize),
            fixedHeight=_button_iconsize,
            fixedWidth=_button_iconsize,
            gridPos=(0, 1, 1, 1),
            parent_widget=self._widgets["selection"],
        )
        self.create_button(
            "but_maximize",
            "",
            icon=qta.icon("fa.chevron-right"),
            iconSize=QtCore.QSize(_button_iconsize, _button_iconsize),
            fixedHeight=_button_iconsize,
            fixedWidth=_button_iconsize,
            gridPos=(2, 1, 1, 1),
            parent_widget=self._widgets["selection"],
        )

        self._widgets["viewer"] = ImageView()
        self._widgets["viewer"].setData = self._widgets["viewer"].setImage
        self._widgets["viewer"].setAttribute(QtCore.Qt.WA_DeleteOnClose)

        self._widgets["hdf_dset"].register_view_widget(self._widgets["viewer"])
        self._widgets["splitter"] = QtWidgets.QSplitter()
        self._widgets["splitter"].setSizePolicy(
            QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding
        )
        self._widgets["splitter"].addWidget(self._widgets["selection"])
        self._widgets["splitter"].addWidget(self._widgets["viewer"])
        self.layout().addWidget(self._widgets["splitter"])
