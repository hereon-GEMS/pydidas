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
Module with PydidasFileDialog which is a persistent QFileDialog which allows to keep
persistent references to the selected directory.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2021-2022, Malte Storm, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0"
__maintainer__ = "Malte Storm"
__status__ = "Development"
__all__ = ["PydidasFileDialog"]

import pathlib
import os

from qtpy import QtWidgets, QtCore

from ..core.utils import get_pydidas_qt_icon
from ..core import PydidasQsettingsMixin, UserConfigError
from ..contexts import ScanContext
from .factory import CreateWidgetsMixIn


SCAN = ScanContext()


class PydidasFileDialog(
    QtWidgets.QFileDialog, CreateWidgetsMixIn, PydidasQsettingsMixin
):
    """
    The PydidasFileDialog is a subclassed QFileDialog with two additional
    buttons which allow fast navigation to the ScanContext base directory and to the
    latest selected directory (in any dialog).

    The usage is the same as for the generic QFileDialog.

    Parameters
    ----------
    parent : Union[None, QWidget], optional
        The dialog's parent widget. The default is None.
    caption : Union[None, str], optional
        The dialog caption. If None, the caption will be selected based on the
        type of dialog. The default is None.
    dialog_type : str
        The type of the dialog. Must be open_file, save_file, or open_directory.
        The default is open_file.
    formats : Union[None, str], optional
        The list of format filters for filenames, if used. The default is None.
    """

    def __init__(self, parent=None, **kwargs):
        QtWidgets.QFileDialog.__init__(self, parent)
        CreateWidgetsMixIn.__init__(self)
        PydidasQsettingsMixin.__init__(self)
        self._config = {
            "caption": kwargs.get("caption", None),
            "type": kwargs.get("dialog_type", "open_file"),
            "formats": kwargs.get("formats", None),
            "curr_dir": None,
            "scan_base": None,
            "latest": None,
            "qsettings_ref": None,
        }
        self.qsettings_ref = kwargs.get("qsettings_ref", None)

        self._set_basic_widget_configuration()
        self._insert_buttons_in_sidebar()
        self._set_user_response_method()

        self._widgets["but_latest_location"].clicked.connect(self.goto_latest_location)
        self._widgets["but_scan_home"].clicked.connect(self.goto_scan_base_dir)

    def _set_basic_widget_configuration(self):
        """
        Set the basic configuration for the widget.
        """
        if self._config["caption"] is not None:
            self.setWindowTitle(self._config["caption"])
        if self._config["formats"] is not None:
            self.setNameFilter(self._config["formats"])
        self.setViewMode(QtWidgets.QFileDialog.Detail)
        self.setOption(QtWidgets.QFileDialog.DontUseNativeDialog)
        self.setSidebarUrls(
            [
                QtCore.QUrl("file:"),
                QtCore.QUrl.fromLocalFile(QtCore.QDir.homePath()),
                QtCore.QUrl.fromLocalFile(
                    QtCore.QStandardPaths.standardLocations(
                        QtCore.QStandardPaths.DesktopLocation
                    )[0]
                ),
                QtCore.QUrl.fromLocalFile(
                    QtCore.QStandardPaths.standardLocations(
                        QtCore.QStandardPaths.DocumentsLocation
                    )[0]
                ),
            ]
        )
        self.setMinimumWidth(900)
        self.setMinimumHeight(600)
        _sidebar = self.findChild(QtWidgets.QListView, "sidebar")
        _sidebar.setMinimumWidth(180)

    def _insert_buttons_in_sidebar(self):
        """
        Insert buttons to access specific locations.
        """
        self.create_empty_widget("sidebar_frame", parent_widget=None)
        self.create_button(
            "but_latest_location",
            "Open latest selected location",
            icon="qt-std::59",
            parent_widget=self._widgets["sidebar_frame"],
        )
        self.create_button(
            "but_scan_home",
            "Open scan base directory",
            icon=get_pydidas_qt_icon("scan_home.png"),
            parent_widget=self._widgets["sidebar_frame"],
        )
        _splitter = self.layout().itemAt(2).widget()
        _listview = _splitter.widget(0)
        _listview.setParent(None)
        self.add_any_widget(
            "listview", _listview, parent_widget=self._widgets["sidebar_frame"]
        )
        _splitter.insertWidget(0, self._widgets["sidebar_frame"])

    def _set_user_response_method(self):
        """
        Set the get_user_response method based on the selected dialog type.
        """
        if self._config["type"] == "open_file":
            self.get_user_response = self.get_existing_filename
        elif self._config["type"] == "save_file":
            self.get_user_response = self.get_saving_filename
        elif self._config["type"] == "open_directory":
            self.get_user_response = self.get_existing_directory
        else:
            raise ValueError("The dialog type {self._config['type']} is not supported.")

    @QtCore.Slot()
    def goto_latest_location(self):
        """
        Open the latest location from any dialogue.
        """
        self.setDirectory(self._config["latest"])

    @QtCore.Slot()
    def goto_scan_base_dir(self):
        """
        Open the ScanContext home directory, if set.

        Returns
        -------
        None.

        """
        self.setDirectory(self._config["scan_base"])

    def exec_(self):
        """
        Execute the dialog.

        Returns
        -------
        int
            The return code of the file dialog.
        """
        self._config["scan_base"] = SCAN.get_param_value(
            "scan_base_directory", dtype=str
        )
        self._config["latest"] = self.q_settings_get_value("dialogues/current")
        self._widgets["but_scan_home"].setEnabled(
            os.path.isdir(self._config["scan_base"])
        )
        if self._config["latest"] is not None:
            self._widgets["but_latest_location"].setEnabled(
                os.path.isdir(self._config["latest"])
            )
        if self._config["curr_dir"] is not None:
            self.setDirectory(self._config["curr_dir"])

        return QtWidgets.QFileDialog.exec_(self)

    def get_existing_directory(self):
        """
        Execute the dialog and get an existing directory.

        Returns
        -------
        Union[str, None]
            The directory path, if selected or None.
        """
        if self._config["caption"] is None:
            self.setWindowTitle("Select directory")
        self.setAcceptMode(QtWidgets.QFileDialog.AcceptOpen)
        self.setFileMode(QtWidgets.QFileDialog.DirectoryOnly)
        res = self.exec_()
        if res == 0:
            return None
        _selection = self.selectedFiles()[0]
        self._config["curr_dir"] = _selection
        self.q_settings_set_key("dialogues/current", self._config["curr_dir"])
        if self._config["qsettings_ref"] is not None:
            self.q_settings_set_key(
                self._config["qsettings_ref"], self._config["curr_dir"]
            )
        return _selection

    def get_existing_filename(self):
        """
        Execute the dialog and get the full path of an existing file.

        Returns
        -------
        Union[str, None]
            The full file path, if selected, or None.
        """
        if self._config["caption"] is None:
            self.setWindowTitle("Select existing file")
        self.setAcceptMode(QtWidgets.QFileDialog.AcceptOpen)
        self.setFileMode(QtWidgets.QFileDialog.ExistingFile)
        res = self.exec_()
        if res == 0:
            return None
        _selection = self.selectedFiles()[0]
        self._config["curr_dir"] = os.path.dirname(_selection)
        self.q_settings_set_key("dialogues/current", self._config["curr_dir"])
        if self._config["qsettings_ref"] is not None:
            self.q_settings_set_key(
                self._config["qsettings_ref"], self._config["curr_dir"]
            )
        return _selection

    def get_saving_filename(self):
        """
        Execute the dialog and get the full path of a file for saving.

        The file may exist or a new filename can be entered.

        Returns
        -------
        Union[str, None]
            The full file path, if selected, or None.
        """
        if self._config["caption"] is None:
            self.setWindowTitle("Select filename")
        self.setAcceptMode(QtWidgets.QFileDialog.AcceptSave)
        self.setFileMode(QtWidgets.QFileDialog.AnyFile)
        res = self.exec_()
        if res == 0:
            return None
        _selection = self.selectedFiles()[0]
        self._config["curr_dir"] = os.path.dirname(_selection)
        self.q_settings_set_key("dialogues/current", self._config["curr_dir"])
        if self._config["qsettings_ref"] is not None:
            self.q_settings_set_key(
                self._config["qsettings_ref"], self._config["curr_dir"]
            )
        return _selection

    def set_curr_dir(self, item):
        """
        Set the current directory to the directory of the given item.

        Parameters
        ----------
        item : Union[pathlib.Path, str]
            The filename or directory name.
        """
        if isinstance(item, pathlib.Path):
            item = str(item)
        if os.path.isdir(item):
            self._config["curr_dir"] = item
        elif os.path.isfile(item):
            self._config["curr_dir"] = os.path.dirname(item)
        else:
            raise UserConfigError(
                f"The given entry {item} is neither a valid directory nor file. Please "
                "check the input and try again."
            )
        self.setDirectory(self._config["curr_dir"])

    @property
    def qsettings_ref(self):
        """
        Get the identifier to store the current path.

        Returns
        -------
        str
            The identifier name.
        """
        if self._config["qsettings_ref"] is None:
            return None
        return self._config["qsettings_ref"][10:]

    @qsettings_ref.setter
    def qsettings_ref(self, name):
        """
        Set a new reference identifier for the QSettings.

        Parameters
        ----------
        name : str
            The identifier name.
        """
        self._config["qsettings_ref"] = (
            "dialogues/" + name if name is not None else None
        )
        if name is not None:
            self._config["curr_dir"] = self.q_settings_get_value(
                self._config["qsettings_ref"], str
            )
