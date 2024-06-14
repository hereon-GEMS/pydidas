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
Module with the DataBrowsingFrameBuilder class which is used to populate
the DataBrowsingFrame with widgets.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2023 - 2024, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"
__all__ = ["DataBrowsingFrameBuilder"]


from qtpy import QtGui, QtWidgets

# from ....widgets.silx_plot import PydidasDataViewerFrame
from ....core.constants import POLICY_EXP_EXP
from ....widgets.framework import BaseFrame
from ....widgets.selection import (
    DirectoryExplorer,
    Hdf5DatasetSelector,
    RawMetadataSelector,
)
from ....widgets.silx_plot.silx_data_viewer import SilxDataViewer


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

        frame.create_empty_widget("browser", sizePolicy=POLICY_EXP_EXP)
        frame.create_any_widget(
            "explorer",
            DirectoryExplorer,
            gridPos=(0, 0, 1, 1),
            parent_widget="browser",
        )
        frame.create_spacer(
            "explorer_spacer",
            gridPos=(0, -1, 1, 1),
            parent_widget="browser",
            fixedWidth=5,
        )
        frame.create_empty_widget(
            "viewer_and_filename", parent_widget=None, sizePolicy=POLICY_EXP_EXP
        )
        frame.create_spacer(
            "spacer",
            gridPos=(0, 0, 1, 1),
            parent_widget="viewer_and_filename",
            fixedWidth=5,
        )
        frame.create_label(
            "filename_label",
            "Filename:",
            parent_widget="viewer_and_filename",
            gridPos=(0, 1, 1, 1),
            font_metric_width_factor=12,
        )
        frame.create_lineedit(
            "filename",
            gridPos=(0, 2, 1, 1),
            parent_widget="viewer_and_filename",
            readOnly=True,
            sizePolicy=POLICY_EXP_EXP,
        )
        frame.create_any_widget(
            "hdf5_dataset_selector",
            Hdf5DatasetSelector,
            gridPos=(-1, 1, 1, 2),
            parent_widget="viewer_and_filename",
            visible=False,
        )
        frame.create_any_widget(
            "raw_metadata_selector",
            RawMetadataSelector,
            gridPos=(-1, 1, 1, 2),
            parent_widget="viewer_and_filename",
            visible=False,
        )
        frame.add_any_widget(
            "viewer",
            SilxDataViewer(),
            gridPos=(-1, 1, 1, 2),
            parent_widget="viewer_and_filename",
        )

        frame._widgets["splitter"] = QtWidgets.QSplitter()
        frame._widgets["splitter"].setSizePolicy(
            QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding
        )
        frame._widgets["splitter"].setStretchFactor(0, 10)
        frame._widgets["splitter"].setStretchFactor(1, 50)
        frame._widgets["splitter"].addWidget(frame._widgets["browser"])
        frame._widgets["splitter"].addWidget(frame._widgets["viewer_and_filename"])
        frame._widgets["splitter"].setSizes(
            [int(0.4 * frame.width()), int(0.6 * frame.width())]
        )
        frame.layout().addWidget(frame._widgets["splitter"])

        for handle in frame.findChildren(QtWidgets.QSplitterHandle):
            palette = handle.palette()
            palette.setColor(QtGui.QPalette.ColorRole.Window, QtGui.QColor("#797979"))
            handle.setPalette(palette)
