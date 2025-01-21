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
Module with the QtPathsWindow class which shows the generic paths used in pydidas.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2023 - 2025, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"
__all__ = ["QtPathsWindow"]


import os
from functools import partial

from qtpy import QtCore, QtGui, QtWidgets

from pydidas.core.constants import (
    ALIGN_TOP_RIGHT,
    FONT_METRIC_CONSOLE_WIDTH,
    FONT_METRIC_SMALL_BUTTON_WIDTH,
    FONT_METRIC_WIDE_BUTTON_WIDTH,
)
from pydidas.resources import logos
from pydidas.version import VERSION
from pydidas.widgets.framework import PydidasWindow


_FULL_WIDTH = FONT_METRIC_CONSOLE_WIDTH + FONT_METRIC_WIDE_BUTTON_WIDTH


class QtPathsWindow(PydidasWindow):
    """Window which displays basic information about the pydidas software."""

    show_frame = False

    def __init__(self, **kwargs: dict):
        self._log_path = os.path.join(
            QtCore.QStandardPaths.standardLocations(
                QtCore.QStandardPaths.DocumentsLocation
            )[0],
            "pydidas",
            VERSION,
        )
        self._config_path = QtCore.QStandardPaths.standardLocations(
            QtCore.QStandardPaths.ConfigLocation
        )[0]
        PydidasWindow.__init__(self, title="pydidas paths", **kwargs)

    def build_frame(self):
        """Build the frame and create all widgets."""
        _font_width, _font_height = QtWidgets.QApplication.instance().font_metrics

        self.create_empty_widget(
            "left_container",
            font_metric_width_factor=_FULL_WIDTH,
        )
        self.create_label(
            "label_title",
            "pydidas paths",
            bold=True,
            fontsize_offset=4,
            parent_widget="left_container",
        )
        self.create_spacer(None, parent_widget="left_container")
        self.create_label(
            "label_document_path",
            f"Logging directory: {self._log_path}",
            font_metric_width_factor=FONT_METRIC_CONSOLE_WIDTH,
            gridPos=(2, 0, 1, 1),
            parent_widget="left_container",
        )
        self.create_button(
            "but_open_logdir",
            "Open logging directory",
            icon="qt-std::SP_DialogOpenButton",
            font_metric_width_factor=FONT_METRIC_WIDE_BUTTON_WIDTH,
            gridPos=(2, 1, 1, 1),
            parent_widget="left_container",
        )
        self.create_label(
            "label_config_path",
            f"Config directory: {self._config_path}",
            font_metric_width_factor=FONT_METRIC_CONSOLE_WIDTH,
            gridPos=(3, 0, 1, 1),
            parent_widget="left_container",
        )
        self.create_button(
            "but_open_configdir",
            "Open config directory",
            font_metric_width_factor=FONT_METRIC_WIDE_BUTTON_WIDTH,
            gridPos=(3, 1, 1, 1),
            icon="qt-std::SP_DialogOpenButton",
            parent_widget="left_container",
        )
        self.add_any_widget(
            "svg_logo",
            logos.pydidas_logo_svg(),
            alignment=ALIGN_TOP_RIGHT,
            fixedHeight=_font_height * 5,
            fixedWidth=_font_height * 5,
            gridPos=(0, 1, 1, 1),
        )
        self.create_button(
            "but_okay",
            "&Close",
            focusPolicy=QtCore.Qt.StrongFocus,
            font_metric_width_factor=FONT_METRIC_SMALL_BUTTON_WIDTH,
            gridPos=(1, 1, 1, 1),
        )

    def connect_signals(self):
        """Connect all required signals."""
        self._widgets["but_okay"].clicked.connect(self.close)
        self._widgets["but_open_logdir"].clicked.connect(
            partial(self.open_folder, self._log_path)
        )
        self._widgets["but_open_configdir"].clicked.connect(
            partial(self.open_folder, self._config_path)
        )
        QtWidgets.QApplication.instance().sig_new_font_metrics.connect(
            self.process_new_font_metrics
        )

    def finalize_ui(self):
        """Finalize the user interface."""
        QtCore.QTimer.singleShot(0, self._widgets["but_okay"].setFocus)

    @QtCore.Slot()
    def open_folder(self, folder):
        """
        Open the selected folder in the system's standard file browser.

        Parameters
        ----------
        folder : str
            The folder name.
        """
        QtGui.QDesktopServices.openUrl(QtCore.QUrl.fromLocalFile(folder))

    @QtCore.Slot(float, float)
    def process_new_font_metrics(self, char_width: float, char_height: float):
        """
        Process the user input of the new font size.

        Parameters
        ----------
        char_width: float
            The font width in pixels.
        char_height : float
            The font height in pixels.
        """
        self._widgets["svg_logo"].setFixedSize(
            QtCore.QSize(char_height * 5, char_height * 5)
        )
        self.resize(
            QtCore.QSize(
                _FULL_WIDTH * char_width + 5 * char_height + 20, char_height * 10
            )
        )
        self.adjustSize()
