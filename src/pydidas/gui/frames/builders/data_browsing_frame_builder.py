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
Module with the DataBrowsingFrameBuilder class which is used to populate
the DataBrowsingFrame with widgets.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2023 - 2025, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"
__all__ = ["create_splitter", "get_widget_creation_information"]


from qtpy import QtGui, QtWidgets

from pydidas.core.constants import POLICY_EXP_EXP
from pydidas.widgets.selection import (
    DirectoryExplorer,
    Hdf5DatasetSelector,
    RawMetadataSelector,
)
from pydidas.widgets.silx_plot import SilxDataViewer


def get_widget_creation_information() -> list[list[str, tuple, dict]]:
    """
    Get the widget creation information for the DataBrowsingFrame.

    Returns
    -------
    list[list[str, tuple, dict]]
        The widget creation information. Each list entry includes all the
        necessary information to create a single widget in the form of a
        list with the following entries:

        - The widget creation method name.
        - The arguments for the widget creation method.
        - The keyword arguments for the widget creation method.
    """
    return [
        ["create_label", (None, "Data browser"), {"fontsize_offset": 4, "bold": True}],
        [
            "create_empty_widget",
            ("browser",),
            {"sizePolicy": POLICY_EXP_EXP, "minimumWidth": 200},
        ],
        [
            "create_any_widget",
            ("explorer", DirectoryExplorer),
            {"gridPos": (0, 0, 1, 1), "parent_widget": "browser"},
        ],
        [
            "create_spacer",
            ("explorer_spacer",),
            {"gridPos": (0, -1, 1, 1), "parent_widget": "browser", "fixedWidth": 5},
        ],
        [
            "create_empty_widget",
            ("viewer_and_filename",),
            {"parent_widget": None, "sizePolicy": POLICY_EXP_EXP},
        ],
        [
            "create_spacer",
            ("spacer",),
            {
                "gridPos": (0, 0, 1, 1),
                "parent_widget": "viewer_and_filename",
                "fixedWidth": 5,
            },
        ],
        [
            "create_label",
            ("filename_label", "Filename:"),
            {
                "parent_widget": "viewer_and_filename",
                "gridPos": (0, 1, 1, 1),
                "font_metric_width_factor": 12,
            },
        ],
        [
            "create_lineedit",
            ("filename",),
            {
                "gridPos": (0, 2, 1, 1),
                "parent_widget": "viewer_and_filename",
                "readOnly": True,
                "sizePolicy": POLICY_EXP_EXP,
            },
        ],
        [
            "create_any_widget",
            ("hdf5_dataset_selector", Hdf5DatasetSelector),
            {
                "gridPos": (-1, 1, 1, 2),
                "parent_widget": "viewer_and_filename",
                "visible": False,
            },
        ],
        [
            "create_any_widget",
            ("raw_metadata_selector", RawMetadataSelector),
            {
                "gridPos": (-1, 1, 1, 2),
                "parent_widget": "viewer_and_filename",
                "visible": False,
            },
        ],
        [
            "add_any_widget",
            ("viewer", SilxDataViewer()),
            {"gridPos": (-1, 1, 1, 2), "parent_widget": "viewer_and_filename"},
        ],
    ]


def create_splitter(
    filesystem_browser: QtWidgets.QWidget,
    data_viewer: QtWidgets.QWidget,
    frame_width: int,
) -> QtWidgets.QSplitter:
    """
    Create a splitter widget for the frame.

    Parameters
    ----------
    filesystem_browser : QtWidgets.QWidget
        The filesystem browser widget.
    data_viewer : QtWidgets.QWidget
        The data viewer widget.
    frame_width : int
        The width of the frame.

    Returns
    -------
    QtWidgets.QSplitter
        The splitter widget.
    """
    _splitter = QtWidgets.QSplitter()
    _splitter.setSizePolicy(*POLICY_EXP_EXP)
    _splitter.addWidget(filesystem_browser)
    _splitter.addWidget(data_viewer)
    _splitter.setSizes([int(0.4 * frame_width), int(0.6 * frame_width)])
    _splitter.setStretchFactor(0, 10)
    _splitter.setStretchFactor(1, 50)
    _splitter.setCollapsible(0, False)
    _splitter.setCollapsible(1, False)

    for handle in _splitter.findChildren(QtWidgets.QSplitterHandle):
        palette = handle.palette()
        palette.setColor(QtGui.QPalette.ColorRole.Window, QtGui.QColor("#797979"))
        handle.setPalette(palette)
    return _splitter
