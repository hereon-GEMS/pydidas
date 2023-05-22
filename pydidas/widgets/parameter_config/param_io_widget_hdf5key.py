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
Module with the ParamIoWidgetHdf5Key class used to edit Parameters. This
class is used exclusively for editing Hdf5key Parameters because of the
implemented typechecks and a button to browse through all included data sets.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2023, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"
__all__ = ["ParamIoWidgetHdf5Key"]


from qtpy import QtCore

from ...core.constants import HDF5_EXTENSIONS, PARAM_INPUT_EDIT_WIDTH
from ..dialogues import Hdf5DatasetSelectionPopup
from ..file_dialog import PydidasFileDialog
from .param_io_widget_with_button import ParamIoWidgetWithButton


class ParamIoWidgetHdf5Key(ParamIoWidgetWithButton):
    """
    Widgets for I/O during plugin parameter for filepaths.
    (Includes a small button to select a filepath from a dialogue.)
    """

    io_edited = QtCore.Signal(str)

    def __init__(
        self, parent, param, width=PARAM_INPUT_EDIT_WIDTH, persistent_qsettings_ref=None
    ):
        """
        Setup the widget.

        Init method to setup the widget and set the links to the parameter
        and Qt parent widget.

        Parameters
        ----------
        parent : QWidget
            A QWidget instance.
        param : Parameter
            A Parameter instance.
        width : int, optional
            The width of the IOwidget.
        """
        super().__init__(parent, param, width)
        self._button.setToolTip("Select a dataset from all dataset keys in a file.")
        self.io_dialog = PydidasFileDialog(
            parent=self,
            dialog_type="open_file",
            formats=("Hdf5 files (*." + " *.".join(HDF5_EXTENSIONS) + ")"),
            qsettings_ref=persistent_qsettings_ref,
            default_extension="Hdf5",
        )

    def button_function(self):
        """
        Open a dialogue to select a file.

        This method is called upon clicking the "open file" button
        and opens a QFileDialog widget to select a filename.
        """
        _result = self.io_dialog.get_user_response()
        if _result is not None:
            dset = Hdf5DatasetSelectionPopup(self, _result).get_dset()
            if dset is not None:
                self.setText(str(dset))
                self.emit_signal()
