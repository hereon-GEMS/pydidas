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
Module with the FeedbackWindow class which allows users to create a quick feedback
form which they can copy and paste to submit feedback.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2023 - 2025, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"
__all__ = ["FeedbackWindow"]


from qtpy import QtCore, QtGui, QtWidgets

from pydidas.core import Parameter, ParameterCollection
from pydidas.core.constants import FONT_METRIC_PARAM_EDIT_WIDTH, PYDIDAS_FEEDBACK_URL
from pydidas.core.utils import apply_qt_properties, copy_text_to_system_clipbord
from pydidas.widgets.framework import PydidasWindow


INFO_TEXT = (
    "Please enter information about the problem/suggestion below and fill out "
    "the form. \nUsing the button at the bottom of the window will copy the "
    "given information to the clipboard. Please paste the information in the "
    "field on the webpage and submit the feedback on the webpage.\n"
    "(You can use only the 'detailed feedback' field, all information will be "
    "encoded in the detailed feedback.)"
)


class FeedbackWindow(PydidasWindow):
    """
    Create all widgets and initialize their state.

    Parameters
    ----------
    self : pydidas.gui.DefineScanFrame
        The DefineScanFrame instance.
    """

    show_frame = False
    default_params = ParameterCollection(
        Parameter("email", str, "", name="E-mail address (optional)")
    )

    def __init__(self, **kwargs: dict):
        PydidasWindow.__init__(self, title="pydidas feedback", **kwargs)

    def build_frame(self):
        """
        Create all widgets for the frame and place them in the layout.
        """
        _metrics = QtWidgets.QApplication.instance().font_metrics
        _font_width = int(_metrics[0])
        _font_height = int(_metrics[1])

        self.create_label(
            "label_title",
            "pydidas Feedback",
            bold=True,
            fontsize_offset=2,
            font_metric_width_factor=FONT_METRIC_PARAM_EDIT_WIDTH,
        )
        self.create_label(
            "label_title",
            INFO_TEXT,
            font_metric_height_factor=8,
            font_metric_width_factor=FONT_METRIC_PARAM_EDIT_WIDTH,
            gridPos=(-1, 0, 1, 1),
            wordWrap=True,
        )

        self.create_line(None)
        self.create_label(
            "label_title",
            "type of feedback",
            bold=True,
            font_metric_width_factor=FONT_METRIC_PARAM_EDIT_WIDTH,
        )
        self.create_radio_button_group(
            "type",
            ["Bug report", "Improvement suggestion", "Usage question"],
            columns=1,
            gridPos=(-1, 0, 1, 1),
            rows=-1,
        )
        self.create_line(None)
        self.create_label(
            "label_title",
            "feedback information",
            bold=True,
            font_metric_width_factor=FONT_METRIC_PARAM_EDIT_WIDTH,
        )
        self.create_param_widget(
            self.get_param("email"),
            font_metric_width_factor=FONT_METRIC_PARAM_EDIT_WIDTH,
            width_io=0.5,
            width_text=0.5,
        )
        self.create_line(None)
        self.create_label(
            "label_details",
            "Detailed feedback:",
            font_metric_width_factor=FONT_METRIC_PARAM_EDIT_WIDTH,
        )
        self.add_any_widget(
            "details",
            QtWidgets.QPlainTextEdit(),
            fixedWidth=_font_width * FONT_METRIC_PARAM_EDIT_WIDTH,
            fixedHeight=_font_height * 15,
        )
        self.create_button(
            "button_copy",
            "Copy to clipboard and open feedback webpage.",
            font_metric_width_factor=FONT_METRIC_PARAM_EDIT_WIDTH,
        )
        _default_font = self._widgets["details"].document().defaultFont()
        _default_font.setFamily(QtWidgets.QApplication.instance().font_family)
        self._widgets["details"].document().setDefaultFont(_default_font)

    def connect_signals(self):
        """
        Connect the signals.
        """
        self._widgets["button_copy"].clicked.connect(self._submit_feedback)
        QtWidgets.QApplication.instance().sig_new_font_metrics.connect(
            self.process_new_font_metrics
        )
        QtWidgets.QApplication.instance().sig_new_font_family.connect(
            self.process_new_font_family
        )

    @QtCore.Slot(float, float)
    def process_new_font_metrics(self, char_width: float, char_height: float):
        """
        Process the user input of the new font size.

        Parameters
        ----------
        char_width : float
            The average metrics width of a char.
        char_height : float
            The average metrics height of a char.
        """
        self.setFixedWidth(int(char_width * FONT_METRIC_PARAM_EDIT_WIDTH + 20))
        apply_qt_properties(
            self._widgets["details"],
            fixedWidth=int(char_width * FONT_METRIC_PARAM_EDIT_WIDTH),
            fixedHeight=char_height * 15,
        )
        self.adjustSize()

    @QtCore.Slot(str)
    def process_new_font_family(self, family: str):
        """
        Update the TextEdit font family.

        Parameters
        ----------
        family : str
            The new font family.
        """
        _default_font = self._widgets["details"].document().defaultFont()
        _default_font.setFamily(QtWidgets.QApplication.instance().font_family)
        self._widgets["details"].document().setDefaultFont(_default_font)

    @QtCore.Slot()
    def _submit_feedback(self):
        _text = (
            f"Sender: {self.get_param_value('email')}\n\n"
            f"Type: {self._widgets['type'].active_label}\n\n"
            f"Details: \n{self._widgets['details'].toPlainText()}"
        )
        copy_text_to_system_clipbord(_text)
        QtGui.QDesktopServices.openUrl(PYDIDAS_FEEDBACK_URL)
