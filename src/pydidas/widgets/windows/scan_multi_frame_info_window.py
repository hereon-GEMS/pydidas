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
The ScanMultiFrameInfoWindow class is a window which explains scan file naming.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2025, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"
__all__ = ["ScanMultiFrameInfoWindow"]


from typing import Any

from qtpy import QtCore, QtWidgets

from pydidas.core import constants
from pydidas.widgets.framework import PydidasWindow
from pydidas.widgets.scroll_area import ScrollArea
from pydidas_qtcore import PydidasQApplication


INTRO_TEXT = """
The multi-frame handling allows to specify how individual (detector) frames are 
assigned to <i>scan points</i>, i.e. to the scanned grid of time and/or motor positions.
<br><br>
The parameter <i>Frame index stepping per scan point</i> defines how the global frame
counter is incremented for each scan point. For example, if the value is set to 1,
the frame counter will be incremented by 1 for each scan point. This corresponds to a 
1:1 relation between scan points and data frames. At a value of 3, the frame counter 
would be incremented by 3 for each scan point, i.e. scan point #0 would use frame #0, 
scan point #1 would use frame #3, etc. <br>
<br>
The <i>Frames to process per scan point</i> determines how many frames are processed
at each scan point. If this value larger than 1, the <i>Frame index stepping per 
scan point</i> will determine the first frame index that is used for the scan point.
<br><br>
The <i>Multi-frame handling</i> parameter defines how the individual frames should be
processed for each scan point. The given operation will be applied per pixel. Note 
that this parameter is only relevant if the <i>Frames to process per scan point</i>
is larger than 1. The options are:
<ul>
<li><b>Average</b>: The average of the frames is calculated and assigned to the 
scan point.</li>
<li><b>Sum</b>: The sum of the frames is calculated and assigned to the scan point.</li>
<li><b>Maximum</b>: The maximum of the frames is calculated and assigned to the scan 
point.</li>
<li><b>Stack</b>: The individual frames are loaded and an image stack is created and 
assigned to the scan point. This will result in a multi-dimensional dataset.</li>
</ul>
<br>
<b>Note:</b> The multi-frame handling applies to the individual frame, not files.
Files with multiple frames per file, e.g. HDF5 files, are compatible because the 
frames in each file are treated individually.
<br><br>
<b>Note: If multiple frames are processed at each scan point, the number of scan 
points must be reduced accordingly.</b> For example, if 30 frames have been acquired
and 3 frames are processed at each scan point, the number of scan points cannot be
larger than 10. If n_frames is the total number of frames, delta is the increment of
the frame index per scan point, and m_frames is the number of frames processed at
each scan point, the maximum number of scan points is given by:
<pre><code>max_scan_points = (n_frames - m_frames + 1) / delta,</code></pre>rounded
down to the nearest integer. Please consult the table below for examples of how
the number of scan points must be adjusted depending on the parameters:
"""
_TEXT_EXAMPLES_INTRO = (
    "The following examples are meant to provide some hands-on guidance on the "
    "practical use of the multi-frame handling parameters. "
)

_TEXT_ACCESS_INTRO = (
    "For accessing the ScanContext parameters programmatically, the following keys "
    "must be used:"
)

_TEXT_ACCESS_EXAMPLE = """
An example of modifying the scan/file naming pattern programmatically is shown below: 
<pre><code>Scan = pydidas.contexts.ScanContext()
Scan.set_param("frame_indices_per_scan_point", "5")
Scan.set_param("scan_frames_per_point", 2)
Scan.set_param("scan_multi_frame_handling", "Sum")
</code></pre>
"""


class ScanMultiFrameInfoWindow(PydidasWindow):
    """
    Window which displays information about scan naming conventions.
    """

    show_frame = False
    width_factor = 110

    def __init__(self, **kwargs: Any):
        PydidasWindow.__init__(self, title="Scan multi-frame handling help", **kwargs)  # noqa
        self.setMinimumHeight(800)
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
            "Scan multi-frame handling explanations",
            fontsize_offset=4,
            bold=True,
            font_metric_width_factor=self.width_factor,
            parent_widget="canvas",
        )
        self.create_spacer(None, parent_widget="canvas")
        self.create_label(
            "label_intro", INTRO_TEXT, font_metric_height_factor=35, **_label_kwargs
        )
        self.create_table(
            "scan_point_table",
            autoscale_height=True,
            columnCount=4,
            font_metric_width_factor=self.width_factor,
            parent_widget="canvas",
            relative_column_widths=[0.25, 0.25, 0.25, 0.25],
            selectionMode=QtWidgets.QAbstractItemView.NoSelection,
        )
        self._widgets["scan_point_table"].add_row(
            "Total number of frames",
            "Frame index stepping per scan point",
            "Frames to process per scan point",
            "Maximum number of scan points",
        )
        self._widgets["scan_point_table"].add_row("30", "1", "1", "30")
        self._widgets["scan_point_table"].add_row("30", "3", "1", "10")
        self._widgets["scan_point_table"].add_multicolumn_cell(
            "If only every third frame is used, the maximum number of scan points "
            "must be divided by 3.",
            start_col=1,
        )
        self._widgets["scan_point_table"].add_row("30", "1", "3", "28")
        self._widgets["scan_point_table"].add_multicolumn_cell(
            "If 3 frames are processed at each scan point, the maximum number of scan "
            "points must be reduced by 2. The scan point #28 will use the frames "
            "#28, #29, and #30 and scan point #29 would require up to frame #31.",
            start_col=1,
        )
        self._widgets["scan_point_table"].add_row("30", "4", "6", "6")
        self._widgets["scan_point_table"].add_multicolumn_cell(
            "Because 6 frames are processed at each scan point, the maximum number "
            "of scan points must be reduced by 5. Since the frame index is "
            "incremented by 4 for each scan point, the maximum number of scan points "
            "must be divided by 4. Therefore, a total of (30 - 6 + 1) / 4 = 6 "
            "scan points can be used. The last scan point #5 (*) will use the frames "
            "#20, #21, #22, #23, #24, and #25. The scan point #6 would require "
            "up to frame #30 which is not available (**)."
            "\n(*) Note that counting starts at 0, i.e. #5 is the 6th scan point."
            "\n(**) The 30 frames include the frames #0 to #29",
            start_col=1,
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
        self.create_label(
            "access_example",
            _TEXT_EXAMPLES_INTRO,
            font_metric_height_factor=3,
            **_label_kwargs,
        )
        self.create_table(
            "example_table",
            autoscale_height=True,
            columnCount=5,
            font_metric_width_factor=self.width_factor,
            parent_widget="canvas",
            relative_column_widths=[0.2, 0.2, 0.2, 0.2, 0.2],
            selectionMode=QtWidgets.QAbstractItemView.NoSelection,
        )
        self._widgets["example_table"].add_row(
            "",
            "Scan/file naming pattern",
            "Frame index stepping per scan point",
            "Frames to process per scan point",
            "Multi-frame handling",
        )
        self._widgets["example_table"].add_multicolumn_cell(
            "Acquisition of multiple frames per scan point: In this example, "
            "multiple frames are acquired per scan point, and the sum of the frames "
            "is required:"
        )
        self._widgets["example_table"].add_row("", "image_####.tif", "3", "3", "Sum")
        self._widgets["example_table"].add_multicolumn_cell(
            "These settings will result in the following data usage:"
            "\nScan point #0: sum(image_0000.tif, image_0001.tif, image_0002.tif)"
            "\nScan point #1: sum(image_0003.tif, image_0004.tif, image_0005.tif)"
            "\netc.",
            start_col=1,
        )
        self._widgets["example_table"].add_multicolumn_cell(
            "Analysis with rolling average over multiple scan points: In this example, "
            "one frame is acquired per scan point, but the frames of multiple scan "
            "points are used to calculate a rolling average."
        )
        self._widgets["example_table"].add_row(
            "", "image_####.tif", "1", "3", "Average"
        )
        self._widgets["example_table"].add_multicolumn_cell(
            "These settings will result in the following data usage:"
            "\nScan point #0: mean(image_0000.tif, image_0001.tif, image_0002.tif)"
            "\nScan point #1: mean(image_0001.tif, image_0002.tif, image_0003.tif)"
            "\netc.",
            start_col=1,
        )
        self._widgets["example_table"].add_multicolumn_cell(
            "Analysis with rolling average over multiple scan points for groups of "
            "scan points: In this example, the acquisition is performed in groups of "
            "4 images per scan point, and a rolling average over 3 scan points is "
            "processed as output."
        )
        self._widgets["example_table"].add_row("", "data_##.npy", "4", "8", "Average")
        self._widgets["example_table"].add_multicolumn_cell(
            "These settings will result in the following data usage:"
            "\nScan point #0: mean(data_00.npy, data_01.npy, .., data_07.npy)"
            "\nScan point #1: mean(data_04.npy, data_05.npy, .., data_11.npy)"
            "\netc.",
            start_col=1,
        )
        self._widgets["example_table"].add_multicolumn_cell(
            "Analysis with four acquisition per scan point which need to be "
            "processed individually further along the pipeline. The `Stack` "
            "option will result in a 3-dimensional dataset of shape (4, det_y, det_x)."
        )
        self._widgets["example_table"].add_row("", "data_####.tif", "4", "4", "Stack")
        self._widgets["example_table"].add_multicolumn_cell(
            "These settings will result in the following data usage:"
            "\nScan point #0: array([data_00.npy, data_01.npy, data_02.npy, "
            "data_03.npy])"
            "\nScan point #1: array([data_04.npy, data_05.npy, data_06.npy, "
            "data_07.npy])\netc.",
            start_col=1,
        )
        self._widgets["example_table"].add_multicolumn_cell(
            "Using a single HDF5 file. In this example, the ::<num> syntax is used to "
            "specify the index of frames to be processed at each scan point. "
        )
        self._widgets["example_table"].add_row("", "data_AB.h5", "4", "4", "Average")
        self._widgets["example_table"].add_multicolumn_cell(
            "These settings will result in the following data usage:"
            "\nScan point #0: mean(data_AB.h5::0, data_AB.h5::1, data_AB.h5::2, "
            "data_AB.h5::3), "
            "\nScan point #1: mean(data_AB.h5::4, data_AB.h5::5, data_AB.h5::6, "
            "data_AB.h5::7)\netc.",
            start_col=1,
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
            "Frame index stepping per scan point", "frame_indices_per_scan_point"
        )
        self._widgets["scan_params_table"].add_row(
            "Frames to process per scan point", "scan_frames_per_point"
        )
        self._widgets["scan_params_table"].add_row(
            "Multi-frame handling", "scan_multi_frame_handling"
        )
        ("frame_indices_per_scan_point",)
        ("scan_frames_per_point",)
        ("scan_multi_frame_handling",)
        self.create_label(
            "access_example",
            _TEXT_ACCESS_EXAMPLE,
            font_metric_height_factor=5.5,
            **_label_kwargs,
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

    window = ScanMultiFrameInfoWindow()
    window.show()
    app.exec_()
