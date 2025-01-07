# This file is part of pydidas.
#
# Copyright 2024 - 2025, Helmholtz-Zentrum Hereon
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
Module with the SelectImageFrameWidget class which allows select a filename and (for
hdf5) files dataset and frame.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2024 - 2025, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"
__all__ = ["SelectImageFrameWidget"]


from pathlib import Path
from typing import Union

from qtpy import QtCore

from pydidas.core import Parameter, UserConfigError
from pydidas.core.constants import POLICY_EXP_FIX
from pydidas.core.utils import get_hdf5_populated_dataset_keys, is_hdf5_filename
from pydidas.data_io import IoManager
from pydidas.widgets.dialogues import Hdf5DatasetSelectionPopup
from pydidas.widgets.file_dialog import PydidasFileDialog
from pydidas.widgets.widget_with_parameter_collection import (
    WidgetWithParameterCollection,
)


class SelectImageFrameWidget(WidgetWithParameterCollection):
    """
    A widget which allows to select an image from a file.

    Parameters
    ----------
    *input_params : tuple[Parameter, ...]
        Parameters passed to the widget to handle the frame references.
    **kwargs : dict
        Supported keyword arguments are;

        parent : Union[None, QWidget], optional
            The parent widget. The default is None.
        import_reference : Union[None, str], optional
            The reference for the file dialogue to store persistent settings.
            If None, only the
    """

    sig_new_file_selection = QtCore.Signal(str, dict)
    sig_file_valid = QtCore.Signal(bool)

    def __init__(self, *input_params: tuple[Parameter, ...], **kwargs: dict):
        WidgetWithParameterCollection.__init__(self, **kwargs)
        self.add_params(*input_params)
        self.__import_dialog = PydidasFileDialog()
        self.__import_qref = kwargs.get("import_reference", None)
        self.create_button(
            "but_open",
            "Select image file",
            icon="qt-std::SP_DialogOpenButton",
            sizePolicy=POLICY_EXP_FIX,
        )
        self.create_param_widget(
            self.get_param("filename"),
            linebreak=True,
            persistent_qsettings_ref=kwargs.get("import_reference", None),
        )
        self.create_param_widget(
            self.get_param("hdf5_key"),
            linebreak=True,
            visible=False,
        )
        self.create_param_widget(self.get_param("hdf5_frame"), visible=False)
        self.create_param_widget(self.get_param("hdf5_slicing_axis"), visible=False)
        self.create_button(
            "but_confirm_file",
            "Confirm input selection",
            sizePolicy=POLICY_EXP_FIX,
            visible=False,
        )
        self._widgets["but_open"].clicked.connect(self.open_image_dialog)
        self._widgets["but_confirm_file"].clicked.connect(self._selected_new_file)
        self.param_widgets["filename"].io_edited.connect(
            self.process_new_filename_input
        )
        self.restore_param_widgets()

    @QtCore.Slot()
    def open_image_dialog(self):
        """
        Open the image selected through the filename.
        """
        _fname = self.__import_dialog.get_existing_filename(
            caption="Import image",
            formats=IoManager.get_string_of_formats(),
            qsettings_ref=self.__import_qref,
        )
        if _fname is not None:
            self.set_param_value_and_widget("filename", _fname)
            self.process_new_filename_input(_fname)

    @QtCore.Slot(str)
    def process_new_filename_input(self, filename: Union[Path, str]):
        """
        Process the input of a new filename in the Parameter widget.

        Parameters
        ----------
        filename : str
            The filename.
        """
        if not Path(filename).is_file():
            self._toggle_file_selected(False)
            raise UserConfigError(
                "The selected filename is not a valid file. Please check the input "
                "and correct the path."
            )
        self._toggle_file_selected(True)
        if is_hdf5_filename(filename):
            _dsets = get_hdf5_populated_dataset_keys(filename, min_dim=2)
            if self.get_param_value("hdf5_key", dtype=str) not in _dsets:
                _dset = Hdf5DatasetSelectionPopup(self, filename).get_dset()
                if _dset is not None:
                    self.set_param_value_and_widget("hdf5_key", _dset)
        if not is_hdf5_filename(filename):
            self._selected_new_file()

    def _toggle_file_selected(self, is_selected: bool):
        """
        Modify widgets visibility and activation based on the file selection.

        Parameters
        ----------
        is_selected : bool
            Flag to process.
        """
        _is_hdf5 = is_hdf5_filename(self.get_param_value("filename"))
        for _name in ["but_confirm_file"]:
            self._widgets[_name].setVisible(is_selected and _is_hdf5)
        for _name in ["hdf5_key", "hdf5_frame", "hdf5_slicing_axis"]:
            self.param_composite_widgets[_name].setVisible(is_selected and _is_hdf5)
        self.sig_file_valid.emit(is_selected)

    @QtCore.Slot()
    def _selected_new_file(self):
        """
        Open a new file / frame based on the input Parameters.
        """
        _fname = self.get_param_value("filename", dtype=str)
        _slice_ax = self.get_param_value("hdf5_slicing_axis")
        _options = {
            "dataset": self.get_param_value("hdf5_key", dtype=str),
            "indices": (
                None
                if _slice_ax is None
                else ((None,) * _slice_ax + (self.get_param_value("hdf5_frame"),))
            ),
        }
        self.sig_new_file_selection.emit(_fname, _options)

    def restore_param_widgets(self):
        """
        Restore the hdf5 parameter keys from the Parameters.
        """
        for _key in ["filename", "hdf5_key", "hdf5_frame", "hdf5_slicing_axis"]:
            self.update_widget_value(_key, self.get_param_value(_key))
        with QtCore.QSignalBlocker(self):
            self._toggle_file_selected(self.get_param_value("filename").is_file())
