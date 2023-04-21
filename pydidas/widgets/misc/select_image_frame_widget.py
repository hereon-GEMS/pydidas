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
Module with the SelectImageFrameWidget class which allows select a filename and (for
hdf5) files dataset and frame.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2021-2022, Malte Storm, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0"
__maintainer__ = "Malte Storm"
__status__ = "Development"
__all__ = ["SelectImageFrameWidget"]


from pathlib import Path

from qtpy import QtCore

from ...core import UserConfigError
from ...core.constants import (
    CONFIG_WIDGET_WIDTH,
    DEFAULT_TWO_LINE_PARAM_CONFIG,
    STANDARD_FONT_SIZE,
)
from ...core.utils import get_hdf5_populated_dataset_keys, is_hdf5_filename
from ...data_io import IoMaster
from ...widgets.dialogues import Hdf5DatasetSelectionPopup
from ..file_dialog import PydidasFileDialog
from ..widget_with_parameter_collection import WidgetWithParameterCollection


class SelectImageFrameWidget(WidgetWithParameterCollection):
    """
    A widget which allows to select an image from a file.
    """

    sig_new_file_selection = QtCore.Signal(str, object)
    sig_file_valid = QtCore.Signal(bool)

    def __init__(self, *input_params, parent=None, import_reference=None, **kwargs):
        WidgetWithParameterCollection.__init__(self, parent)
        self.add_params(*input_params)

        self.__import_dialog = PydidasFileDialog(
            parent=self,
            dialog_type="open_file",
            caption="Import image",
            formats=IoMaster.get_string_of_formats(),
            qsettings_ref=import_reference,
        )

        self.setFixedWidth(CONFIG_WIDGET_WIDTH)
        _button_params = dict(
            fixedWidth=CONFIG_WIDGET_WIDTH,
            fixedHeight=25,
        )
        _param_config = dict(
            visible=False,
            width_total=CONFIG_WIDGET_WIDTH,
            width_io=100,
            width_text=CONFIG_WIDGET_WIDTH - 130,
            width_unit=30,
        )
        self.create_label(
            "label_title",
            "Input file",
            fontsize=STANDARD_FONT_SIZE + 1,
            fixedWidth=CONFIG_WIDGET_WIDTH,
            bold=True,
        )

        self.create_button(
            "but_open",
            "Select image file",
            icon=self.style().standardIcon(42),
            **_button_params,
        )
        self.create_param_widget(
            self.get_param("filename"),
            **(
                DEFAULT_TWO_LINE_PARAM_CONFIG
                | dict(persistent_qsettings_ref=import_reference)
            ),
        )
        self.create_param_widget(
            self.get_param("hdf5_key"),
            **(DEFAULT_TWO_LINE_PARAM_CONFIG | dict(visible=False)),
        )
        self.create_param_widget(
            self.get_param("hdf5_frame"), **(_param_config | dict(width_unit=0))
        )
        self.create_button(
            "but_confirm_file",
            "Confirm file selection",
            **_button_params,
            visible=False,
        )
        self._widgets["but_open"].clicked.connect(self.open_image_dialog)
        self._widgets["but_confirm_file"].clicked.connect(self._selected_new_file)
        self.param_widgets["filename"].io_edited.connect(
            self.process_new_filename_input
        )

    @QtCore.Slot()
    def open_image_dialog(self):
        """
        Open the image selected through the filename.
        """
        _fname = self.__import_dialog.get_user_response()
        self.set_param_value_and_widget("filename", _fname)
        self.process_new_filename_input(_fname)

    @QtCore.Slot(str)
    def process_new_filename_input(self, filename):
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
            if not self.get_param_value("hdf5_key", dtype=str) in _dsets:
                _dset = Hdf5DatasetSelectionPopup(self, filename).get_dset()
                if _dset is not None:
                    self.set_param_value_and_widget("hdf5_key", _dset)
        if not is_hdf5_filename(filename):
            self._selected_new_file()

    def _toggle_file_selected(self, is_selected):
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
        for _name in ["hdf5_key", "hdf5_frame"]:
            self.param_composite_widgets[_name].setVisible(is_selected and _is_hdf5)
        self.sig_file_valid.emit(is_selected)

    @QtCore.Slot()
    def _selected_new_file(self):
        """
        Open a new file / frame based on the input Parameters.
        """
        _fname = self.get_param_value("filename", dtype=str)
        _options = dict(
            dataset=self.get_param_value("hdf5_key", dtype=str),
            frame=self.get_param_value("hdf5_frame"),
        )
        self.sig_new_file_selection.emit(_fname, _options)
