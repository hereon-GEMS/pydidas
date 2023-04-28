# This file is part of pydidas.
#
# Copyright 2021-, Helmholtz-Zentrum Hereon
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
__copyright__ = "Copyright 2021-, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Development"
__all__ = ["QtPathsWindow"]


import os
from functools import partial

from qtpy import QtCore, QtGui, QtSvg

from ...core.utils import get_pydidas_icon_fname
from ...version import VERSION
from ..framework import PydidasWindow


class QtPathsWindow(PydidasWindow):
    """
    Window which displays basic information about the pydidas software.
    """

    show_frame = False

    def __init__(self, parent=None, **kwargs):
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
        PydidasWindow.__init__(self, parent, title="pydidas paths", **kwargs)

    def build_frame(self):
        """
        Build the frame and create all widgets.
        """

        self.create_label(
            "label_title",
            "pydidas paths",
            fontsize=14,
            bold=True,
            gridPos=(0, 0, 1, 1),
        )
        self.create_spacer(None)
        self.create_label(
            "label_document_path",
            f"Logging directory: {self._log_path}",
            gridPos=(1, 0, 1, 1),
        )
        self.create_button(
            "but_open_logdir",
            "Open logging directory",
            icon=self.style().standardIcon(42),
            fixedWidth=180,
            fixedHeight=25,
            gridPos=(1, 1, 1, 1),
        )
        self.create_label(
            "label_config_path",
            f"Config directory: {self._config_path}",
            gridPos=(2, 0, 1, 1),
        )
        self.create_button(
            "but_open_configdir",
            "Open config directory",
            icon=self.style().standardIcon(42),
            fixedWidth=180,
            fixedHeight=25,
            gridPos=(2, 1, 1, 1),
        )
        self.add_any_widget(
            "svg_logo",
            QtSvg.QSvgWidget(get_pydidas_icon_fname()),
            gridPos=(0, 2, 1, 1),
            fixedHeight=75,
            fixedWidth=75,
            layout_kwargs={"alignment": (QtCore.Qt.AlignRight | QtCore.Qt.AlignTop)},
        )
        self.create_spacer(None)
        self.create_button(
            "but_okay",
            "&Close",
            gridPos=(-1, 2, 1, 1),
            focusPolicy=QtCore.Qt.StrongFocus,
        )

    def connect_signals(self):
        """
        Build the frame and create all widgets.
        """
        self._widgets["but_okay"].clicked.connect(self.close)
        self._widgets["but_open_logdir"].clicked.connect(
            partial(self.open_folder, self._log_path)
        )
        self._widgets["but_open_configdir"].clicked.connect(
            partial(self.open_folder, self._config_path)
        )

    def finalize_ui(self):
        """
        Finalize the user interface.
        """
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
