# This file is part of pydidas.
#
# Copyright 2025, Helmholtz-Zentrum Hereon
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
The ScanFileNamingInformationWindow class is a window which explains scan file naming.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2025, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"
__all__ = ["ScanFileNamingInformationWindow"]


from pathlib import Path
from typing import Any

from qtpy import QtCore, QtWidgets

from pydidas.core import constants
from pydidas.widgets.framework import PydidasWindow
from pydidas.widgets.scroll_area import ScrollArea
from pydidas_qtcore import PydidasQApplication


INTRO_TEXT = """
The scan/file naming pattern determines how the input plugins in the pydidas Workflow
interpret the path to the detector images. <br>
<br>
For most input plugins, the scan/file naming pattern corresponds directly to the
file names of the files. <br>
<br>
Some plugins use the scan/file naming pattern not only for the file names but also
to access files in a nested directory structure. Please check the documentation
of the individual input plugins for details on how the scan/file naming pattern is 
used by the particular plugin. <br>
<br>
If multiple files are used in a scan, the scan/file naming pattern must be set up
to specify which part of the file name corresponds to the counting variable.
The dynamic part of the file name must be replaced by a placeholder of hash characters
`<b>#</b>` of the same length as the digits of the number to be replaced. Files which
include a counter of variable length (e.g. `image_9.tif`, `image_10.tif`, etc.)
should use a placeholder of the minimum length of the counter. <br>
<br>
The <i>First filename number</i> is the first number that should be used in the 
scan/file naming pattern. The index stepping of filenames defines by how much the 
counter should be incremented for each file."""

_TEXT_ACCESS_INTRO = (
    "For accessing the ScanContext parameters programmatically, the following keys "
    "must be used:"
)

_TEXT_ACCESS_EXAMPLE = """
An example of modifying the scan/file naming pattern programmatically is shown below: 
<pre><code>Scan = pydidas.contexts.ScanContext()
Scan.set_param("scan_name_pattern", "image_####.tif")
Scan.set_param("pattern_number_offset", 1)
</code></pre>
"""


class ScanFileNamingInformationWindow(PydidasWindow):
    """
    Window which displays information about scan naming conventions.
    """

    show_frame = False
    width_factor = 110

    def __init__(self, **kwargs: Any):
        PydidasWindow.__init__(self, title="Scan file naming help", **kwargs)  # noqa
        self.setMinimumHeight(600)
        self._qtapp = PydidasQApplication.instance()
        self.process_new_font_metrics(*self._qtapp.font_metrics)
        self._qtapp.sig_new_font_metrics.connect(self.process_new_font_metrics)

    def build_frame(self):
        """
        Build the frame and create all widgets.
        """
        _label_kwargs = dict(
            openExternalLinks=True,
            textInteractionFlags=QtCore.Qt.LinksAccessibleByMouse,
            textFormat=QtCore.Qt.RichText,
            gridPos=(-1, 0, 1, 1),
            font_metric_width_factor=self.width_factor,
            parent_widget="canvas",
            wordWrap=True,
        )

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
            "Scan file naming explanations",
            fontsize_offset=4,
            bold=True,
            font_metric_width_factor=self.width_factor,
            parent_widget="canvas",
        )
        self.create_spacer(None, parent_widget="canvas")
        self.create_label(
            "label_intro", INTRO_TEXT, font_metric_height_factor=17, **_label_kwargs
        )
        self.create_label(
            "label_programmatic_access",
            "Programmatic access:",
            underline=True,
            bold=True,
            font_metric_width_factor=self.width_factor,
            parent_widget="canvas",
        )
        self.create_label(
            "access_intro",
            _TEXT_ACCESS_INTRO,
            font_metric_height_factor=1,
            **_label_kwargs,
        )
        self.create_table(
            "scan_params_table",
            parent_widget="canvas",
            horizontal_header=True,
            columnCount=2,
            font_metric_width_factor=3 * self.width_factor // 4,
            horizontalHeaderLabels=[["item", "reference key"]],
            selectionMode=QtWidgets.QAbstractItemView.NoSelection,
        )
        self._widgets["scan_params_table"].add_row(
            "Scan/file naming pattern", "scan_name_pattern"
        )
        self._widgets["scan_params_table"].add_row(
            "First filename number", "pattern_number_offset"
        )
        self._widgets["scan_params_table"].add_row(
            "Index stepping of filenames", "pattern_number_delta"
        )
        self.create_label(
            "access_example",
            _TEXT_ACCESS_EXAMPLE,
            font_metric_height_factor=4.5,
            **_label_kwargs,
        )

        self.create_spacer(None, parent_widget="canvas")
        self.create_label(
            "label_examples",
            "Examples:",
            underline=True,
            bold=True,
            font_metric_width_factor=self.width_factor,
            parent_widget="canvas",
        )

        self.create_table(
            "example_table",
            autoscale_height=True,
            columnCount=4,
            font_metric_width_factor=self.width_factor,
            parent_widget="canvas",
            relative_column_widths=[0.25, 0.15, 0.15, 0.4],
            selectionMode=QtWidgets.QAbstractItemView.NoSelection,
        )
        self._widgets["example_table"].add_row(
            "naming pattern",
            "first number",
            "index stepping",
            "resulting filenames",
        )
        self._widgets["example_table"].add_row(
            "image_####.tif",
            "1",
            "1",
            "image_0001.tif, image_0002.tif, image_0003.tif, ...",
        )
        self._widgets["example_table"].add_row(
            "image_##.tif",
            "0",
            "10",
            "image_00.tif, image_10.tif, ..., image_90.tif, image_100.tif, ...",
        )
        self._widgets["example_table"].add_row(
            "scan_42_######_data.h5",
            "3",
            "3",
            "scan_42_00003_data.h5, scan_42_00006_data.h5, ...",
        )
        self._widgets["example_table"].add_row(
            "scan_42a_#.fio",
            "0",
            "5",
            "scan_42a_0.fio, scan_42a_5.fio, scan_42a_10.fio, scan_42a_15.fio, ...",
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
    def process_new_font_metrics(self, char_width: float, char_height: float):  # noqa
        """
        Set the fixed width of the widget dynamically from the font height metric.

        Parameters
        ----------
        char_width: float
            The font width in pixels.
        char_height : float
            The font height in pixels.
        """
        self.setFixedWidth(
            int((self.width_factor + 12) * char_width)
            + self._qtapp.scrollbar_width
            + 30
        )


if __name__ == "__main__":
    # This is only for testing purposes and should not be used in production code.
    # It is here to allow running this file directly to test the window.
    import pydidas_qtcore

    app = pydidas_qtcore.PydidasQApplication([])

    window = ScanFileNamingInformationWindow()
    window.show()
    app.exec_()
