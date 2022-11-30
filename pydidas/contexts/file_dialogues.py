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
Module with PydidasFileDialog and PydidasDirDialog classes which allow to select a
file or directory in a QFileDialog while keeping a persistent reference to the
selected directory.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2021-2022, Malte Storm, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0"
__maintainer__ = "Malte Storm"
__status__ = "Development"
__all__ = ["PydidasFileDialog", "PydidasDirDialog"]

import os
import pathlib

from qtpy import QtWidgets, QtCore

from ..core import PydidasQsettings, UserConfigError


class PydidasFileDialog(QtCore.QObject):
    """
    Convenience class which stores the current working directory for the QFileDialog
    and calls the dialog in the dialog's current directory.
    """

    def __init__(
        self,
        parent=None,
        caption="",
        formats="",
        dialog=QtWidgets.QFileDialog.getOpenFileName,
        qsettings_ref=None,
    ):
        QtCore.QObject.__init__(self, parent)
        self._qsettings_ref = None
        self._curr_dir = None
        self._caption = caption
        self._formats = formats
        self._dialog = dialog
        self.qsettings_ref = qsettings_ref
        if self._qsettings_ref is not None:
            self._qsettings = PydidasQsettings()
            self._curr_dir = self._qsettings.value(self._qsettings_ref, str)

    def get_user_response(self):
        """
        Get the user response for selecting a file in the specified dialogue.

        Returns
        -------
        str
            The selected filename.
        """
        _fname = self._dialog(
            self.parent(), self._caption, self._curr_dir, self._formats
        )[0]
        if _fname != "":
            self._curr_dir = os.path.dirname(_fname)
            if self._qsettings_ref is not None:
                self._qsettings.set_value(self._qsettings_ref, self._curr_dir)
        return _fname

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
            self._curr_dir = item
            return
        if os.path.isfile(item):
            self._curr_dir = os.path.dirname(item)
            return
        raise UserConfigError(
            f"The given entry {item} is neither a valid directory nor file. Please "
            "check the input and try again."
        )

    @property
    def qsettings_ref(self):
        """
        Get the identifier to store the current path.

        Returns
        -------
        str
            The identifier name.
        """
        if self._qsettings_ref is None:
            return None
        return self._qsettings_ref[10:]

    @qsettings_ref.setter
    def qsettings_ref(self, name):
        """
        Set a new reference identifier for the QSettings.

        Parameters
        ----------
        name : str
            The identifier name.
        """
        _old_settings = self._qsettings_ref
        self._qsettings_ref = "dialogues/" + name if name is not None else None
        if _old_settings is None and name is not None:
            self._qsettings = PydidasQsettings()
            self._curr_dir = self._qsettings.value(self._qsettings_ref, str)


class PydidasDirDialog(PydidasFileDialog):
    """
    A subclass of the PydidasFileDialog which handles directories instead of files.
    """

    def __init__(
        self,
        parent=None,
        caption="",
        dialog=QtWidgets.QFileDialog.getExistingDirectory,
        qsettings_ref=None,
    ):
        PydidasFileDialog.__init__(
            self,
            parent=parent,
            caption=caption,
            dialog=dialog,
            qsettings_ref=qsettings_ref,
        )

    def get_user_response(self):
        """
        Get the user response for selecting a directory in the specified dialogue.

        Returns
        -------
        str
            The selected directory name.
        """
        _dirname = self._dialog(self.parent(), self._caption, self._curr_dir)
        if _dirname != "":
            self._curr_dir = _dirname
            if self._qsettings_ref is not None:
                self._qsettings.set_value(self._qsettings_ref, _dirname)
        return _dirname
