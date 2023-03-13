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
Module with the ScanDimensionInformationWindow class which explains the scan dimensions.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2021-2022, Malte Storm, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0"
__maintainer__ = "Malte Storm"
__status__ = "Development"
__all__ = ["ScanDimensionInformationWindow"]

import os

from qtpy import QtCore, QtGui

from ...core import constants
from ...widgets import ScrollArea
from .pydidas_window import PydidasWindow


INTRO_TEXT = (
    "The scan dimensions are organized following the data structure. Both in the case "
    "of individual files and of container files (e.g. Hdf5), individual frames from a "
    "multi-dimension scan are acquired and stored in a linear manner."
    "The scan dimensions must be set up to allow pydidas to extract the "
    "multi-dimensional coordinate from the single frame number. <br><br>For a "
    "2-dimensional scan, the structure would be:"
    "<pre><code>n = 0"
    "<br>for <i>i</i> in <i>dim_1_points</i>:"
    "<br>    move motor 1 to position"
    "<br>    for <i>j</i> in <i>dim_2_points</i>:"
    "<br>        move motor 2 to position"
    "<br>        acquire image <i>n</i>"
    "<br>        <i>n = n + 1</i></code></pre>"
    "The frame index <i>n</i> is not explicitly defined but usually "
    "incremented by the detector control software. However, it is also implicitly "
    "defined through <code><i>n(i, j) = i * number(dim_2_points) + j</i></code>. "
    "Pydidas follows the convention of defining scan dimension 1 as the slowest and "
    "scan dimension <i>n</i> in a <i>n</i>-dimensional scan as the fastest."
)


EXAMPLE_0 = (
    "Consider the following example of a two-dimensional mesh scan in <i>x</i> and "
    "<i>z</i>: Three linescans with 6 points each in <i>x</i> inside a loop over 3"
    "<i>z</i> positions:"
)
EXAMPLE_1 = (
    "Programmaticly, this scan is written as:"
    "<pre><code>n = 0"
    "<br>for <i>i_z</i> in [0, 1, 2]:"
    "<br>    move z-motor to position z(i_z)"
    "<br>    for <i>j_x</i> in <i>[0, 1, 2, 3, 4, 5]</i>:"
    "<br>        move x-motor to position x(j_x)"
    "<br>        acquire image <i>n</i>"
    "<br>        <i>n = n + 1</i></code></pre>"
    "The (detector) frame numbers <i>n</i> are given by incrementing a global index, "
    "starting with <code>n = 0</code>:"
)

EXAMPLE_2 = (
    "Because <i>x</i> is iterating faster than <i>z</i>, it is considered the fast "
    "axis and must be put as scan dimension 2 in pydidas to be consistent with the "
    "programmatical scan order."
)

IMAGE_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "resources")


class ScanDimensionInformationWindow(PydidasWindow):
    """
    Window which displays information about scan dimensions and their order.
    """

    show_frame = False

    def __init__(self, parent=None, **kwargs):
        PydidasWindow.__init__(self, parent, title="Scan dimension help", **kwargs)

    def build_frame(self):
        """
        Build the frame and create all widgets.
        """

        self.create_empty_widget(
            "canvas",
            layout_kwargs=dict(
                contentsMargins=(0, 0, 0, 0),
            ),
            sizePolicy=constants.EXP_FIX_POLICY,
            alignment=constants.QT_DEFAULT_ALIGNMENT,
            parent_widget=None,
        )
        self.create_any_widget(
            "scroll_area",
            ScrollArea,
            widget=self._widgets["canvas"],
            fixedWidth=650,
            sizePolicy=constants.FIX_EXP_POLICY,
            stretch=(1, 0),
            layout_kwargs={"alignment": None},
        )
        self.create_label(
            "label_title",
            "Scan dimension information",
            fontsize=14,
            bold=True,
            fixedWidth=600,
            parent_widget=self._widgets["canvas"],
        )
        self.create_spacer(None, parent_widget=self._widgets["canvas"])
        self.create_label(
            "label_intro",
            INTRO_TEXT,
            openExternalLinks=True,
            textInteractionFlags=QtCore.Qt.LinksAccessibleByMouse,
            textFormat=QtCore.Qt.RichText,
            gridPos=(-1, 0, 1, 1),
            fixedWidth=600,
            parent_widget=self._widgets["canvas"],
        )
        self.create_spacer(None, parent_widget=self._widgets["canvas"])
        self.create_label(
            "example_title",
            "Example:",
            underline=True,
            bold=True,
            fixedWidth=600,
            parent_widget=self._widgets["canvas"],
        )
        self.create_label(
            "example_0",
            EXAMPLE_0,
            fixedWidth=600,
            parent_widget=self._widgets["canvas"],
        )

        _image0 = QtGui.QPixmap(os.path.join(IMAGE_PATH, "scan_scheme_with_lines.png"))
        self.create_label(
            "example_image0",
            "",
            pixmap=_image0,
            fixedWidth=_image0.width(),
            fixedHeight=_image0.height(),
            parent_widget=self._widgets["canvas"],
        )
        self.create_label(
            "example_1",
            EXAMPLE_1,
            fixedWidth=600,
            parent_widget=self._widgets["canvas"],
        )
        _image1 = QtGui.QPixmap(os.path.join(IMAGE_PATH, "scan_scheme_with_points.png"))
        self.create_label(
            "example_image1",
            "",
            pixmap=_image1,
            fixedWidth=_image1.width(),
            fixedHeight=_image1.height(),
            parent_widget=self._widgets["canvas"],
        )
        self.create_label(
            "example_2",
            EXAMPLE_2,
            fixedWidth=600,
            parent_widget=self._widgets["canvas"],
        )

        self.create_button(
            "but_close", "Close", gridPos=(-1, 1, 1, 1), autoDefault=True
        )

    def connect_signals(self):
        """
        Build the frame and create all widgets.
        """
        self._widgets["but_close"].clicked.connect(self.close)

    def finalize_ui(self):
        """
        Build the window.
        """
        super().finalize_ui()
        self.setGeometry(200, 200, 640, 640)
