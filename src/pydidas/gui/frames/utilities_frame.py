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
Module with the UtilitiesFrame which allows to present and open various utilities.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2023 - 2025, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"
__all__ = ["UtilitiesFrame"]


from functools import partial

from qtpy import QtCore, QtWidgets

from pydidas.gui.frames.builders import UtilitiesFrameBuilder
from pydidas.gui.frames.composite_creator_frame import CompositeCreatorFrame
from pydidas.widgets.framework import BaseFrame
from pydidas.widgets.windows import (
    ExportEigerPixelmaskWindow,
    GlobalSettingsWindow,
    ImageSeriesOperationsWindow,
    MaskEditorWindow,
    UserConfigWindow,
)


class UtilitiesFrame(BaseFrame):
    """
    The UtilitiesFrame allows to open various independent utilities.
    """

    menu_icon = "mdi::apps-box"
    menu_title = "Utilities"
    menu_entry = "Utilities"

    def __init__(self, **kwargs: dict):
        BaseFrame.__init__(self, **kwargs)
        self._child_windows = {}
        self.__window_counter = 0
        self._add_config_windows()

    def _add_config_windows(self):
        """
        Create the required widgets and signals for the global configuration window.
        """
        _frame = GlobalSettingsWindow()
        _frame.frame_activated(_frame.frame_index)
        self._child_windows["global_settings"] = _frame
        _frame = UserConfigWindow()
        _frame.frame_activated(_frame.frame_index)
        self._child_windows["user_config"] = _frame

    def build_frame(self):
        """
        Build the frame and populate it with widgets.
        """
        UtilitiesFrameBuilder.build_frame(self)

    def finalize_ui(self):
        """
        finalize the UI initialization.
        """
        self.__app = QtWidgets.QApplication.instance()
        self.__app.sig_exit_pydidas.connect(
            self._child_windows["global_settings"].close
        )

    def connect_signals(self):
        """
        Connect the required signals and slots to add functionality to widgets.
        """
        self._widgets["button_eiger_mask"].clicked.connect(
            partial(self.create_and_show_temp_window, ExportEigerPixelmaskWindow)
        )
        self._widgets["button_series_operations"].clicked.connect(
            partial(self.create_and_show_temp_window, ImageSeriesOperationsWindow)
        )
        self._widgets["button_mask_editor"].clicked.connect(
            partial(self.create_and_show_temp_window, MaskEditorWindow)
        )
        self._widgets["button_global_settings"].clicked.connect(
            partial(self.show_window, "global_settings")
        )
        self._widgets["button_user_config"].clicked.connect(
            partial(self.show_window, "user_config")
        )
        self._widgets["button_composite_creation"].clicked.connect(
            partial(self.create_and_show_frame, CompositeCreatorFrame)
        )
        # self._widgets["button_directory_spy"].clicked.connect(
        #     partial(self.create_and_show_frame, DirectorySpyFrame)
        # )

    @QtCore.Slot(object)
    def create_and_show_temp_window(self, window: QtWidgets.QWidget):
        """
        Show the given temporary window.

        Parameters
        ----------
        window : QtCore.QWidget
            The window to be shown.
        """
        _name = f"temp_window_{self.__window_counter:03d}"
        self.__window_counter += 1
        self._child_windows[_name] = window()
        self._child_windows[_name].sig_closed.connect(
            partial(self.remove_window_from_children, _name)
        )
        self.__app.sig_exit_pydidas.connect(self._child_windows[_name].close)
        self._child_windows[_name].show()

    @QtCore.Slot(object)
    def create_and_show_frame(self, frame: BaseFrame):
        """
        Show the given frame.

        Parameters
        ----------
        frame : pydidas.widgets.framework.BaseFrame
            The frame to be shown.
        """
        if frame.menu_title in self._child_windows:
            self._child_windows[frame.menu_title].show()
            return
        _frame = frame()
        _frame.setWindowTitle(frame.menu_title)
        _frame.frame_activated(_frame.frame_index)
        self._child_windows[frame.menu_title] = _frame
        _frame.show()

    @QtCore.Slot(str)
    def show_window(self, name: str):
        """
        Show a separate window.

        Parameters
        ----------
        name : str
            The name key of the window to be shown.
        """
        _index = self._child_windows[name].frame_index
        self._child_windows[name].frame_activated(_index)
        self._child_windows[name].show()
        self._child_windows[name].raise_()

    @QtCore.Slot(str)
    def remove_window_from_children(self, name: str):
        """
        Remove the specified window from the list of child window.

        Parameters
        ----------
        name : str
            The name key for the window.
        """
        if name in self._child_windows:
            self._child_windows[name].deleteLater()
            del self._child_windows[name]
