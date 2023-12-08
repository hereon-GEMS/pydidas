# This file is part of pydidas.
#
# Copyright 2023, Helmholtz-Zentrum Hereon
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
Module with the MainMenu class which is a subclassed QMainWindow and which
manages the pydidas GUI menu.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2023, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"
__all__ = ["MainMenu"]


import os
import sys
from functools import partial
from pathlib import Path
from typing import Union

import yaml
from qtpy import QtCore, QtGui, QtWidgets

from ..contexts import GLOBAL_CONTEXTS
from ..core import PydidasQsettingsMixin, UserConfigError
from ..core.constants import PYDIDAS_STANDARD_CONFIG_PATH
from ..core.utils import (
    DOC_HOME_QURL,
    doc_filename_for_frame_manual,
    doc_qurl_for_frame_manual,
)
from ..resources import icons
from ..version import VERSION
from ..widgets import PydidasFileDialog
from ..widgets.dialogues import AcknowledgeBox, QuestionBox, critical_warning
from ..widgets.framework import PydidasFrameStack
from ..widgets.windows import (
    AboutWindow,
    ExportEigerPixelmaskWindow,
    FeedbackWindow,
    GlobalSettingsWindow,
    ImageSeriesOperationsWindow,
    MaskEditorWindow,
    QtPathsWindow,
    UserConfigWindow,
)
from ..workflow import WorkflowTree
from . import utils
from .gui_excepthook_ import gui_excepthook


TREE = WorkflowTree()


class MainMenu(QtWidgets.QMainWindow, PydidasQsettingsMixin):
    """
    Inherits from :py:class:`qtpy.QtWidgets.QMainWindow`.

    The MainWindowWindow is a bare QMainWindow with a menu.

    Parameters
    ----------
    parent : QtWidgets.QWidget, optional
        The widget's parent. The default is None.
    geometry : Union[tuple, list, None], optional
        The geometry as a 4-tuple or list. The entries are the top left
        corner coordinates (x0, y0) and width and height. If None, the
        default values will be used. The default is None.
    """

    STATE_FILENAME = f"pydidas_gui_state_{VERSION}.yaml"
    EXIT_STATE_FILENAME = f"pydidas_gui_exit_state_{VERSION}.yaml"

    sig_close_main_window = QtCore.Signal()

    def __init__(self, parent=None, geometry=None):
        QtWidgets.QMainWindow.__init__(self, parent)
        PydidasQsettingsMixin.__init__(self)
        sys.excepthook = gui_excepthook

        self._child_windows = {}
        self._actions = {}
        self._menus = {}
        self.__window_counter = 0

        self._setup_mainwindow_widget(geometry)
        self._add_config_windows()
        self._create_gui_state_dialogs()
        self._create_menu()

        self._help_shortcut = QtWidgets.QShortcut(QtCore.Qt.Key_F1, self)
        self._help_shortcut.activated.connect(self._open_help)
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)
        _app = QtWidgets.QApplication.instance()
        _app.aboutToQuit.connect(self.centralWidget().reset)
        self.sig_close_main_window.connect(_app.send_gui_close_signal)

    def _setup_mainwindow_widget(self, geometry):
        """
        Setup the user interface.

        Parameters
        ----------
        geometry : Union[tuple, list, None], optional
            The geometry as a 4-tuple or list. The entries are the top left
            corner coordinates (x0, y0) and width and height. If None, the
            default values will be used. The default is None.
        """
        if isinstance(geometry, (tuple, list)) and len(geometry) == 4:
            self.setGeometry(*geometry)
        else:
            self.setGeometry(40, 60, 1400, 1000)
        self.setCentralWidget(PydidasFrameStack())
        self.statusBar().showMessage("pydidas started")
        self.setWindowTitle("pydidas GUI")
        self.setWindowIcon(icons.pydidas_icon_with_bg())
        self.setFocus(QtCore.Qt.OtherFocusReason)

    def _add_config_windows(self):
        """
        Add the required widgets and signals for the global configuration
        window and create it.
        """
        _frame = GlobalSettingsWindow()
        _frame.frame_activated(_frame.frame_index)
        self._child_windows["global_settings"] = _frame
        _frame = UserConfigWindow()
        _frame.frame_activated(_frame.frame_index)
        self._child_windows["user_config"] = _frame

    def _create_gui_state_dialogs(self):
        """
        Create the persistent dialogues for import/export of the GUI state.
        """
        self.__import_dialog = PydidasFileDialog(
            parent=self,
            dialog_type="open_file",
            caption="Import GUI state file",
            formats="All supported files (*.yaml *.yml);;YAML (*.yaml *.yml)",
            qsettings_ref="MainWindowGuiState__import",
        )
        self.__export_dialog = PydidasFileDialog(
            parent=self,
            dialog_type="save_file",
            caption="Export GUI state file",
            formats="All supported files (*.yaml *.yml);;YAML (*.yaml *.yml)",
            default_extension="yaml",
            qsettings_ref="MainWindowGuiState__export",
        )

    def _create_menu(self):
        """
        Create the application's main menu.
        """
        self._create_menu_actions()
        self._connect_menu_actions()
        self._add_actions_to_menu()

    def _create_menu_actions(self):
        """
        Create all required actions for the menu entries and store them in the
        internal _actions dictionary.
        """
        store_state_action = QtWidgets.QAction("&Store GUI state", self)
        store_state_action.setStatusTip(
            "Store the current state of the graphical user interface including"
            " all frame Parameters and App configurations. This action allows "
            "users to store their state in the machines configuration for "
            "loading it again at a later date."
        )
        self._actions["store_state"] = store_state_action

        export_state_action = QtWidgets.QAction("&Export GUI state", self)
        export_state_action.setStatusTip(
            "Export the current state of the graphical user interface "
            "to a user-defined file. This includes all frame Parameters and "
            "App configurations."
        )
        self._actions["export_state"] = export_state_action

        restore_state_action = QtWidgets.QAction("&Restore GUI state", self)
        restore_state_action.setStatusTip(
            "Restore the state of the graphical user interface from a "
            "previously created snapshot."
        )
        self._actions["restore_state"] = restore_state_action

        restore_state_action = QtWidgets.QAction("&Restore GUI state at exit", self)
        restore_state_action.setStatusTip(
            "Restore the state of the graphical user interface from the stored "
            "information at the (correct) exit."
        )
        self._actions["restore_exit_state"] = restore_state_action

        import_state_action = QtWidgets.QAction("&Import GUI state", self)
        import_state_action.setStatusTip(
            "Import the state of the graphical user interface from a "
            "user-defined file."
        )
        self._actions["import_state"] = import_state_action

        exit_action = QtWidgets.QAction(QtGui.QIcon("exit.png"), "E&xit", self)
        exit_action.setStatusTip("Exit application")
        self._actions["exit"] = exit_action

        self._actions["open_settings"] = QtWidgets.QAction("&Settings", self)
        self._actions["open_user_config"] = QtWidgets.QAction("&User config", self)

        self._actions["tools_export_eiger_pixel_mask"] = QtWidgets.QAction(
            "&Export Eiger Pixelmask", self
        )
        self._actions["tools_image_series_ops"] = QtWidgets.QAction(
            "&Image series processing", self
        )
        self._actions["tools_mask_editor"] = QtWidgets.QAction(
            "Edit detector &mask", self
        )
        self._actions["tools_clear_local_logs"] = QtWidgets.QAction(
            "&Clear local log files", self
        )

        self._actions["open_documentation_browser"] = QtWidgets.QAction(
            "Open documentation in default web browser", self
        )
        self._actions["open_about"] = QtWidgets.QAction("About pydidas", self)
        self._actions["open_paths"] = QtWidgets.QAction("Pydidas paths", self)
        self._actions["check_for_update"] = QtWidgets.QAction("Check for update", self)
        self._actions["open_feedback"] = QtWidgets.QAction("Open feedback form", self)

    def _connect_menu_actions(self):
        """
        Connect all menu actions to their respective slots.
        """
        self._actions["store_state"].triggered.connect(self._action_store_state)
        self._actions["export_state"].triggered.connect(self._action_export_state)
        self._actions["restore_state"].triggered.connect(self._action_restore_state)
        self._actions["restore_exit_state"].triggered.connect(self._action_restore_exit)
        self._actions["import_state"].triggered.connect(self._action_import_state)
        self._actions["exit"].triggered.connect(self.close)
        self._actions["open_settings"].triggered.connect(
            partial(self.show_window, "global_settings")
        )
        self._actions["open_user_config"].triggered.connect(
            partial(self.show_window, "user_config")
        )
        self._actions["tools_export_eiger_pixel_mask"].triggered.connect(
            partial(self.create_and_show_temp_window, ExportEigerPixelmaskWindow)
        )
        self._actions["tools_image_series_ops"].triggered.connect(
            partial(self.create_and_show_temp_window, ImageSeriesOperationsWindow)
        )
        self._actions["tools_clear_local_logs"].triggered.connect(
            utils.clear_local_log_files
        )
        self._actions["tools_mask_editor"].triggered.connect(
            partial(self.create_and_show_temp_window, MaskEditorWindow)
        )
        self._actions["open_documentation_browser"].triggered.connect(
            utils.open_doc_in_browser
        )
        self._actions["open_about"].triggered.connect(
            partial(self.create_and_show_temp_window, AboutWindow)
        )
        self._actions["open_paths"].triggered.connect(
            partial(self.create_and_show_temp_window, QtPathsWindow)
        )
        self._actions["check_for_update"].triggered.connect(
            partial(self.check_for_updates, force_check=True)
        )
        self._actions["open_feedback"].triggered.connect(
            partial(self.create_and_show_temp_window, FeedbackWindow)
        )

    def _add_actions_to_menu(self):
        """
        Add the defined actions to the menu bar.
        """
        _menu = self.menuBar()

        _state_menu = QtWidgets.QMenu("&GUI state", self)
        _state_menu.addAction(self._actions["store_state"])
        _state_menu.addAction(self._actions["export_state"])
        _state_menu.addSeparator()
        _state_menu.addAction(self._actions["restore_state"])
        _state_menu.addAction(self._actions["restore_exit_state"])
        _state_menu.addAction(self._actions["import_state"])

        _file_menu = _menu.addMenu("&File")
        _file_menu.addMenu(_state_menu)
        _file_menu.addAction(self._actions["exit"])
        _menu.addMenu(_file_menu)

        _utilities_menu = _menu.addMenu("&Tools")
        _utilities_menu.addAction(self._actions["tools_export_eiger_pixel_mask"])
        _utilities_menu.addAction(self._actions["tools_image_series_ops"])
        _utilities_menu.addAction(self._actions["tools_mask_editor"])
        _utilities_menu.addSeparator()
        _utilities_menu.addAction(self._actions["tools_clear_local_logs"])
        _menu.addMenu(_utilities_menu)

        _options_menu = _menu.addMenu("&Options")
        _options_menu.addAction(self._actions["open_user_config"])
        _options_menu.addAction(self._actions["open_settings"])

        _help_menu = _menu.addMenu("&Help")
        _help_menu.addAction(self._actions["open_documentation_browser"])
        _help_menu.addSeparator()
        _help_menu.addAction(self._actions["open_feedback"])
        _help_menu.addAction(self._actions["open_paths"])
        _help_menu.addSeparator()
        _help_menu.addAction(self._actions["check_for_update"])
        _help_menu.addAction(self._actions["open_about"])
        _menu.addMenu(_help_menu)

        self._menus["file"] = _file_menu
        self._menus["state"] = _state_menu
        self._menus["utilities"] = _utilities_menu
        self._menus["options"] = _options_menu
        self._menus["help"] = _help_menu

    @QtCore.Slot()
    def _action_store_state(self):
        """
        Store the current GUI state in a generic file.
        """
        _reply = QuestionBox(
            "Store GUI state",
            "Do you want to store the current GUI state "
            "(and overwrite any previous states)?",
        ).exec_()
        if _reply:
            self.export_gui_state(
                PYDIDAS_STANDARD_CONFIG_PATH.joinpath(self.STATE_FILENAME)
            )

    @QtCore.Slot()
    def _action_export_state(self):
        """
        Store the current GUI state in a user-defined file.
        """
        _fname = self.__export_dialog.get_user_response()
        if _fname is not None:
            self.export_gui_state(_fname)

    @QtCore.Slot()
    def _action_restore_state(self):
        """
        Restore the GUI state from a generic file.
        """
        _reply = QuestionBox(
            "Restore GUI state",
            "Do you want to restore the GUI state? This will reset any changes"
            " you made and you might lose work.",
        ).exec_()
        if _reply:
            self.restore_gui_state(state="saved")

    @QtCore.Slot()
    def _action_restore_exit(self):
        """
        Restore the GUI to its state at the last exit.
        """
        _reply = QuestionBox(
            "Restore GUI state",
            "Do you want to restore the GUI state? This will reset any changes"
            " you made and you might lose work.",
        ).exec_()
        if _reply:
            self.restore_gui_state(state="exit")

    @QtCore.Slot()
    def _action_import_state(self):
        """
        Restore the GUI state from a user-defined file.
        """
        _fname = self.__import_dialog.get_user_response()
        if _fname is not None:
            self.restore_gui_state(state="manual", filename=_fname)

    @QtCore.Slot()
    def check_for_updates(self, force_check: bool = False, auto_check: bool = False):
        """
        Check if the pydidas version is up to date and show a dialog if not.

        Parameters
        ----------
        force_check : bool, optional
            Flag to force a check even when the user disabled checking for
            updates. The default is False.
        auto_check : bool, optional
            Flag to signalize an automatic update check. This will only display
            a notice when the local and remote versions differ. The default is False.
        """
        if (
            not self.q_settings_get("user/check_for_updates", default=True)
            and not force_check
        ):
            return
        _remote_v = utils.get_remote_version()
        _ack_version = self.q_settings_get(
            "user/update_version_acknowledged", default=""
        )
        _text = (
            (
                "A new version of pydidas is available.\n\n"
                f"    Locally installed version: {VERSION}\n"
                f"    Latest release: {_remote_v}.\n\n"
            )
            if _remote_v > VERSION
            else (
                f"The locally installed version of pydidas (version {VERSION}) \n"
                "is the latest available version. No actions required."
            )
        )
        if auto_check and _remote_v > VERSION and _remote_v not in [-1, _ack_version]:
            _text += "Please update pydidas to benefit from the latest improvements."
        if (
            auto_check and _remote_v > VERSION and _remote_v not in [-1, _ack_version]
        ) or not auto_check:
            _ack = AcknowledgeBox(
                show_checkbox=auto_check,
                text=_text,
                text_preformatted=True,
                title=(
                    "Pydidas update available"
                    if _remote_v > VERSION
                    else "Pydidas version information"
                ),
            ).exec_()
            if _ack:
                self.q_settings_set("user/update_version_acknowledged", _remote_v)

    @QtCore.Slot(str)
    def update_status(self, text):
        """
        Get a text message and show it in the global status widget.

        This slot can be used by any QObject to send an update which will be
        added to the global list of status messages.

        Parameters
        ----------
        text : str
            The status message.
        """
        self.statusBar().showMessage(text)
        if text[-1] != "\n":
            text += "\n"
        self.__info_widget.add_status(text)

    @QtCore.Slot(str)
    def show_window(self, name):
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

    @QtCore.Slot(object)
    def create_and_show_temp_window(self, window):
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
        self._child_windows[_name].show()

    @QtCore.Slot(str)
    def remove_window_from_children(self, name):
        """
        Remove the specified window from the list of child window.

        Parameters
        ----------
        name : str
            The name key for the window.
        """
        if name in self._child_windows:
            del self._child_windows[name]

    def export_gui_state(self, filename: Union[Path, str]):
        """
        This function exports the GUI state.

        Parameters
        ----------
        filename : Union[Path, str]
            The full file system path of the configuration file.
        """
        if isinstance(filename, str):
            filename = Path(filename)
        if not filename.parent.is_dir():
            filename.parent.mkdir(parents=True)
        _state = self.__get_window_states()
        for _index, _frame in enumerate(self.centralWidget().frames):
            _frameindex, _frame_state = _frame.export_state()
            assert _index == _frameindex
            _state[f"frame_{_index:02d}"] = _frame_state
        for _key, _context in GLOBAL_CONTEXTS.items():
            _state[_key] = _context.get_param_values_as_dict(
                filter_types_for_export=True
            )
        _state["workflow_tree"] = TREE.export_to_string()
        _state["pydidas_version"] = VERSION
        with open(filename, "w") as _file:
            yaml.dump(_state, _file, Dumper=yaml.SafeDumper)

    def __get_window_states(self):
        """
        Get the states of the main window and all child windows for exporting.

        Returns
        -------
        _window_states : dict
            The dictionary with the required information to store and restore
            window states.
        """
        _window_states = {}
        for _key, _window in self._child_windows.items():
            if _key != "tmp":
                _window_states[_key] = _window.export_window_state()
        _window_states["main"] = self.export_mainwindow_state()
        return _window_states

    def export_mainwindow_state(self):
        """
        Export the main window's state.

        Returns
        -------
        dict
            The state of the main window required to restore the look.
        """
        return {
            "geometry": self.geometry().getRect(),
            "frame_index": self.centralWidget().currentIndex(),
        }

    def restore_gui_state(self, state="saved", filename=None):
        """
        Restore the window states from saved information.

        If the filename is not specified, the internally used file for storing
        the state will be opened.

        Parameters
        ----------
        state: str, optional
            The state to be restored. Can be "saved" to restore the last saved state,
            "exit" to restore the state on exit or "manual" to manually give a filename.
        filename : Union[None, str], optional
            The filename to be used to restore the state. This kwarg will only be used
            if the state kwarg is set to "manual".
        """
        if state.upper() == "SAVED":
            filename = utils.get_standard_state_full_filename(self.STATE_FILENAME)
        elif state.upper() == "EXIT":
            filename = utils.get_standard_state_full_filename(self.EXIT_STATE_FILENAME)
        elif state.upper() == "MANUAL" and filename is None:
            raise UserConfigError(
                "A filename must be supplied for 'manual' gui state restoration."
            )
        elif state.upper() == "MANUAL" and os.path.isfile(filename):
            pass
        else:
            raise UserConfigError(f"The given state '{state}' cannot be interpreted.")
        if not os.path.isfile(filename):
            return
        with open(filename, "r") as _file:
            _state = yaml.load(_file, Loader=yaml.SafeLoader)
        if _state is None:
            return
        if _state.get("pydidas_version", "0.0.0") != VERSION:
            raise UserConfigError(
                "The saved state was not created with the current pydidas version and "
                "cannot be imported."
            )
        self._restore_global_objects(_state)
        self._restore_frame_states(_state)
        self._restore_window_states(_state)

    @staticmethod
    def _restore_global_objects(state):
        """
        Get the states of pydidas' global objects (ScanContext,
        DiffractionExperimentContext, WorkflowTree)

        Parameters
        ----------
        state : dict
            The restored global states which includes the states for the
            global objects.
        """
        try:
            TREE.restore_from_string(state["workflow_tree"])
        except KeyError:
            raise UserConfigError("Cannot import Workflow. Not all plugins found.")
        for _contex_key, _context in GLOBAL_CONTEXTS.items():
            for _key, _val in state[_contex_key].items():
                _context.set_param_value(_key, _val)

    def _restore_window_states(self, state):
        """
        Get the states of the main window and all child windows for exporting.

        Returns
        -------
        state : dict
            The dictionary with the required information to store and restore
            window states.
        """
        for _key, _window in self._child_windows.items():
            if not _key.startswith("temp_window"):
                _window.restore_window_state(state[_key])
        self.restore_mainwindow_state(state["main"])

    def restore_mainwindow_state(self, state):
        """
        Restore the main window's state from saved information.

        Parameters
        ----------
        state : dict
            The stored state of the main window.
        """
        self.setGeometry(*state["geometry"])
        _frame_index = state["frame_index"]
        if _frame_index >= 0:
            self.centralWidget().setCurrentIndex(_frame_index)

    def _restore_frame_states(self, state):
        """
        Restore the states of all the frames in the PydidasFrameStack.

        Parameters
        ----------
        state : dict
            The state information for all frames.
        """
        _frame_info = [
            f"frame_{_index:02d}" in state.keys()
            for _index, _ in enumerate(self.centralWidget().frames)
        ]
        if False in _frame_info:
            critical_warning(
                "Error",
                "The state is not defined for all frames. Aborting Frame state import.",
            )
            return
        for _index, _frame in enumerate(self.centralWidget().frames):
            _frame.restore_state(state[f"frame_{_index:02d}"])

    @QtCore.Slot()
    def _open_help(self):
        """
        Open the help in a browser.

        This slot will check whether a helpfile exists for the current frame and open
        the respective helpfile if it exits or the main documentation if it does not.
        """
        _frame_class = self.centralWidget().currentWidget().__class__.__name__
        _docfile = doc_filename_for_frame_manual(_frame_class)

        if os.path.exists(_docfile):
            _url = doc_qurl_for_frame_manual(_frame_class)
        else:
            _url = DOC_HOME_QURL
        _ = QtGui.QDesktopServices.openUrl(_url)

    def deleteLater(self):
        """
        Add deleteLater entries for the associated windows.
        """
        for _window in self._child_windows.values():
            try:
                _window.deleteLater()
            except RuntimeError:
                pass
        super().deleteLater()

    def closeEvent(self, event):
        """
        Handle the Qt closeEvent.

        This method adds calls to the child windows to close themselves.

        Parameters
        ----------
        event : QtCore.QEvent
            The closing event.
        """
        _reply = QuestionBox(
            "Exit confirmation", "Do you want to close the pydidas window?"
        ).exec_()
        if not _reply:
            event.ignore()
            return
        self.export_gui_state(
            PYDIDAS_STANDARD_CONFIG_PATH.joinpath(self.EXIT_STATE_FILENAME)
        )
        self.sig_close_main_window.emit()
        event.accept()
