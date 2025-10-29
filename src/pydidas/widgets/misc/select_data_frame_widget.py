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
Module with the SelectDataFrameWidget class which allows select a filename and (for
hdf5) files dataset and frame.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2024 - 2025, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"
__all__ = ["SelectDataFrameWidget"]


from pathlib import Path
from typing import Any

import numpy as np
from qtpy import QtCore

from pydidas.core import UserConfigError, get_generic_param_collection
from pydidas.core.utils import (
    get_hdf5_metadata,
    get_hdf5_populated_dataset_keys,
    is_hdf5_filename,
)
from pydidas.data_io import IoManager
from pydidas.widgets.data_viewer import DataAxisSelector
from pydidas.widgets.dialogues import Hdf5DatasetSelectionPopup
from pydidas.widgets.file_dialog import PydidasFileDialog
from pydidas.widgets.widget_with_parameter_collection import (
    WidgetWithParameterCollection,
)


class SelectDataFrameWidget(WidgetWithParameterCollection):
    """
    A widget which allows to select a data frame from a file.

    Parameters
    ----------
    **kwargs : Any
        Supported keyword arguments are;

        parent : QWidget | None, optional
            The parent widget. The default is None.
        import_reference : str | None, optional
            The reference for the file dialogue to store persistent settings.
            If None, no persistent settings are stored. The default is None.
        ndim : int, optional
            The number of dimensions of the data to be imported. The default is 2.
    """

    sig_new_file_selection = QtCore.Signal(str, dict)
    sig_file_valid = QtCore.Signal(bool)
    init_kwargs = WidgetWithParameterCollection.init_kwargs + [
        "import_reference",
        "ndim",
    ]
    default_params = get_generic_param_collection(
        "filename",
        "hdf5_key",
        "hdf5_slicing_axis",
    )

    def __init__(self, **kwargs: Any):
        WidgetWithParameterCollection.__init__(self, **kwargs)
        self.set_default_params()
        self.params["hdf5_slicing_axis"].update_value_and_choices(None, [None])
        self.__import_dialog = PydidasFileDialog()
        self.__import_qref = kwargs.get("import_reference", None)
        self.__ndim = kwargs.get("ndim", 2)
        self.__frame = 0
        self._create_widgets()
        self.connect_signals()
        for _key in ["filename", "hdf5_key", "hdf5_slicing_axis"]:
            self.update_widget_value(_key, self.get_param_value(_key))
        with QtCore.QSignalBlocker(self):
            self._toggle_file_selected(self.get_param_value("filename").is_file())

    def _create_widgets(self):
        """Create the widgets for the data frame selection."""
        self.create_param_widget(
            "filename", linebreak=True, persistent_qsettings_ref=self.__import_qref
        )
        self.create_param_widget("hdf5_key", linebreak=False, visible=False)
        self.create_param_widget("hdf5_slicing_axis", visible=False)
        self.create_any_widget("ax_selector", DataAxisSelector, 0, multiline=True)

    def connect_signals(self):
        """Connect the widget signals to the relevant slots."""
        #        self._widgets["but_open"].clicked.connect(self.open_image_dialog)
        self.param_widgets["filename"].sig_new_value.connect(self.process_new_filename)
        for _key in ["hdf5_key", "hdf5_slicing_axis"]:
            self.param_widgets[_key].sig_value_changed.connect(self._selected_new_frame)
        self._widgets["ax_selector"].sig_new_slicing.connect(self._new_frame_index)

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
            self.process_new_filename(_fname)

    @QtCore.Slot(str)
    def process_new_filename(self, filename: Path | str):
        """
        Process the input of a new filename in the Parameter widget.

        Parameters
        ----------
        filename : Path | str
            The filename for the new input data.
        """
        if not isinstance(filename, Path):
            filename = Path(filename)
        if not filename.is_file():
            self._toggle_file_selected(False)
            self.sig_file_valid.emit(False)
            raise UserConfigError(
                "The selected filename is not a valid file. Please check the input "
                "and correct the path."
            )
        if is_hdf5_filename(filename):
            _dset_key = self.get_param_value("hdf5_key", dtype=str)
            _dsets = get_hdf5_populated_dataset_keys(
                filename, min_dim=self.__ndim, max_dim=self.__ndim + 1
            )
            if _dset_key not in _dsets:
                _dset = Hdf5DatasetSelectionPopup(self, filename).get_dset()
                if _dset:
                    self.set_param_value_and_widget("hdf5_key", _dset)
                else:
                    return
            _shape = get_hdf5_metadata(f"{str(filename)}://{_dset_key}", "shape")
            _data_ndim = len(_shape)
            if _data_ndim == self.__ndim:
                self.params["hdf5_slicing_axis"].update_value_and_choices(None, [None])
                self.param_widgets["hdf5_slicing_axis"].update_choices([None])
                self._widgets["ax_selector"].setVisible(False)
            elif _data_ndim == self.__ndim + 1:
                _choices = list(range(_data_ndim))
                self.params["hdf5_slicing_axis"].update_value_and_choices(0, _choices)
                self.param_widgets["hdf5_slicing_axis"].update_choices(_choices)
                self._widgets["ax_selector"].setVisible(True)
                self._widgets["ax_selector"].set_axis_metadata(np.arange(_shape[0]))
                self._widgets["ax_selector"]._widgets["label_axis"].setText("Frame:")
                self._widgets["ax_selector"]._widgets["combo_axis_use"].setVisible(
                    False
                )

            else:
                self._toggle_file_selected(False)
                self.sig_file_valid.emit(False)
                raise UserConfigError(
                    "The selected dataset has an incompatible number of "
                    "dimensions. Please select a different dataset."
                )
        self._toggle_file_selected(True)
        self._selected_new_frame()

    def _toggle_file_selected(self, is_selected: bool):
        """
        Modify widgets visibility and activation based on the file selection.

        Parameters
        ----------
        is_selected : bool
            Flag to process.
        """
        _is_hdf5 = is_hdf5_filename(self.get_param_value("filename"))
        for _name in ["hdf5_key", "hdf5_slicing_axis"]:
            self.param_composite_widgets[_name].setVisible(is_selected and _is_hdf5)
        self._widgets["ax_selector"].setVisible(is_selected and _is_hdf5)
        self.sig_file_valid.emit(is_selected)

    @QtCore.Slot()
    def _selected_new_frame(self):
        """
        Open a new file / frame based on the input Parameters.
        """
        _fname = self.get_param_value("filename", dtype=str)
        _slice_ax = self.get_param_value("hdf5_slicing_axis")
        _options = {
            "dataset": self.get_param_value("hdf5_key", dtype=str),
            "indices": (
                None if _slice_ax is None else ((None,) * _slice_ax + (self.__frame,))
            ),
        }
        self.sig_new_file_selection.emit(_fname, _options)

    def reset_selection(self):
        """
        Reset the file selection to default values.
        """
        self.set_param_value_and_widget("filename", "")
        self.set_param_value_and_widget("hdf5_key", "")
        with QtCore.QSignalBlocker(self):
            self._toggle_file_selected(self.get_param_value("filename").is_file())

    @QtCore.Slot(int, str)
    def _new_frame_index(self, ax_index: int, frame_slice_str: str):
        """
        Process a new frame index from the axis selector.

        Parameters
        ----------
        ax_index : int
            The axis index (not used here).
        frame_slice_str : str
            The frame index as string.
        """
        del ax_index
        _index = int(frame_slice_str.split(":")[0])
        self.__frame = _index
        self._selected_new_frame()
