# This file is part of pydidas.
#
# Copyright 2023, Helmholtz-Zentrum Hereon
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
Module with the DataBrowsingFrameBuilder class which is used to populate
the DataBrowsingFrame with widgets.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2023, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"
__all__ = ["DataBrowsingFrameBuilder"]


import qtawesome as qta
from qtpy import QtWidgets

from ....core.constants import POLICY_EXP_EXP
from ....widgets.factory import PydidasSquareButton
from ....widgets.framework import BaseFrame
from ....widgets.selection import DirectoryExplorer, Hdf5DatasetSelector
from ....widgets.silx_plot import PydidasImageView


class DataBrowsingFrameBuilder:
    """
    Class to populate the DataBrowsingFrame with widgets.
    """

    @classmethod
    def build_frame(cls, frame: BaseFrame):
        """
        Build the frame and create all required widgets.
        """
        frame.create_label(None, "Data browser", fontsize_offset=4, bold=True)

        frame.create_empty_widget(
            "browser",
            fix_width=False,
            sizePolicy=POLICY_EXP_EXP,
        )
        frame.create_any_widget(
            "explorer",
            DirectoryExplorer,
            parent_widget="browser",
            gridPos=(0, 0, 3, 1),
        )
        frame.create_any_widget(
            "hdf_dset",
            Hdf5DatasetSelector,
            parent_widget="browser",
            gridPos=(3, 0, 1, 1),
        )
        frame.create_any_widget(
            "but_minimize",
            PydidasSquareButton,
            icon=qta.icon("fa.chevron-left"),
            parent_widget="browser",
            gridPos=(0, 1, 1, 1),
        )
        frame.create_any_widget(
            "but_maximize",
            PydidasSquareButton,
            parent_widget="browser",
            icon=qta.icon("fa.chevron-right"),
            gridPos=(2, 1, 1, 1),
        )

        frame._widgets["viewer"] = PydidasImageView()

        frame._widgets["hdf_dset"].register_view_widget(frame._widgets["viewer"])

        frame._widgets["splitter"] = QtWidgets.QSplitter()
        frame._widgets["splitter"].setSizePolicy(
            QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding
        )
        frame._widgets["splitter"].setStretchFactor(0, 10)
        frame._widgets["splitter"].setStretchFactor(1, 20)
        frame._widgets["splitter"].addWidget(frame._widgets["browser"])
        frame._widgets["splitter"].addWidget(frame._widgets["viewer"])
        frame.layout().addWidget(frame._widgets["splitter"])
