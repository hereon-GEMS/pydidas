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
The ScanDimensionInformationWindow class is a window which explains the scan dimensions.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2023 - 2025, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"
__all__ = ["ScanDimensionInformationWindow"]


from pathlib import Path

from qtpy import QtCore, QtGui, QtWidgets

from pydidas.core import constants
from pydidas.widgets.framework import PydidasWindow
from pydidas.widgets.scroll_area import ScrollArea


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
    "<i>z</i>: Three linescans with 6 points each in <i>x</i> inside a loop over 3 "
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

IMAGE_PATH = Path(__file__).parent.parent.parent.joinpath("resources", "images")


class ScanDimensionInformationWindow(PydidasWindow):
    """
    Window which displays information about scan dimensions and their order.
    """

    show_frame = False
    width_factor = 88

    def __init__(self, **kwargs: dict):
        PydidasWindow.__init__(self, title="Scan dimension help", **kwargs)
        self.setMinimumHeight(600)
        self._qtapp = QtWidgets.QApplication.instance()
        self.process_new_font_metrics(*self._qtapp.font_metrics)
        self._qtapp.sig_new_font_metrics.connect(self.process_new_font_metrics)

    def build_frame(self):
        """
        Build the frame and create all widgets.
        """

        self.create_empty_widget(
            "canvas",
            sizePolicy=constants.POLICY_EXP_FIX,
            alignment=constants.ALIGN_TOP_LEFT,
            parent_widget=None,
            font_metric_width_factor=self.width_factor,
        )
        self.create_any_widget(
            "scroll_area",
            ScrollArea,
            widget=self._widgets["canvas"],
            sizePolicy=constants.POLICY_FIX_EXP,
            stretch=(1, 0),
            layout_kwargs={"alignment": None},
        )
        self.create_label(
            "label_title",
            "Scan dimension information",
            fontsize_offset=4,
            bold=True,
            font_metric_width_factor=self.width_factor,
            parent_widget="canvas",
        )
        self.create_spacer(None, parent_widget="canvas")
        self.create_label(
            "label_intro",
            INTRO_TEXT,
            openExternalLinks=True,
            textInteractionFlags=QtCore.Qt.LinksAccessibleByMouse,
            textFormat=QtCore.Qt.RichText,
            gridPos=(-1, 0, 1, 1),
            font_metric_width_factor=self.width_factor,
            font_metric_height_factor=19,
            parent_widget="canvas",
            wordWrap=True,
        )
        self.create_spacer(None, parent_widget="canvas")
        self.create_label(
            "example_title",
            "Example:",
            underline=True,
            bold=True,
            font_metric_width_factor=self.width_factor,
            parent_widget="canvas",
        )
        self.create_label(
            "example_0",
            EXAMPLE_0,
            font_metric_width_factor=self.width_factor,
            font_metric_height_factor=2,
            parent_widget="canvas",
            wordWrap=True,
        )

        _image0 = QtGui.QPixmap(
            IMAGE_PATH.joinpath("scan_scheme_with_lines.png").as_posix()
        )
        self.create_label(
            "example_image0",
            "",
            pixmap=_image0,
            fixedWidth=_image0.width(),
            fixedHeight=_image0.height(),
            parent_widget="canvas",
        )
        self.create_label(
            "example_1",
            EXAMPLE_1,
            font_metric_width_factor=self.width_factor,
            font_metric_height_factor=11,
            parent_widget="canvas",
            wordWrap=True,
        )
        _image1 = QtGui.QPixmap(
            IMAGE_PATH.joinpath("scan_scheme_with_points.png").as_posix()
        )
        self.create_label(
            "example_image1",
            "",
            pixmap=_image1,
            fixedWidth=_image1.width(),
            fixedHeight=_image1.height(),
            parent_widget="canvas",
        )
        self.create_label(
            "example_2",
            EXAMPLE_2,
            font_metric_width_factor=self.width_factor,
            font_metric_height_factor=2,
            parent_widget="canvas",
            wordWrap=True,
        )

        self.create_button(
            "but_close",
            "Close",
            gridPos=(-1, 1, 1, 1),
            autoDefault=True,
            font_metric_width_factor=12,
        )

    def connect_signals(self):
        """
        Build the frame and create all widgets.
        """
        self._widgets["but_close"].clicked.connect(self.close)

    @QtCore.Slot(float, float)
    def process_new_font_metrics(self, char_width: float, char_height: float):
        """
        Set the fixed width of the widget dynamically from the font height metric.

        Parameters
        ----------
        char_width: float
            The font width in pixels.
        char_height : float
            The font height in pixels.
        """
        self.setFixedWidth(int(100 * char_width) + self._qtapp.scrollbar_width + 30)
