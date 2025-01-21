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
Module with the ImageSeriesOperationsWindow class which allows to perform mathematical
operations on a number of images.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2024 - 2025, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"
__all__ = ["ImageSeriesOperationsWindow"]

import numbers
import os

import numpy as np
from qtpy import QtCore, QtWidgets

from pydidas.core import Parameter, UserConfigError, get_generic_param_collection
from pydidas.core.constants import FONT_METRIC_PARAM_EDIT_WIDTH, HDF5_EXTENSIONS
from pydidas.core.utils import ShowBusyMouse, get_extension, get_hdf5_metadata
from pydidas.data_io import IoManager, export_data, import_data
from pydidas.managers import FilelistManager
from pydidas.widgets import dialogues
from pydidas.widgets.framework import PydidasWindow


_operation = Parameter(
    "operation",
    str,
    "mean",
    name="Image series operator",
    choices=["mean", "sum", "max"],
    tooltip=("The mathematical operation to be applied to the image series."),
)

_HDF5_PARAM_KEYS = [
    "hdf5_key",
    "hdf5_slicing_axis",
    "hdf5_first_image_num",
    "hdf5_last_image_num",
]


class ImageSeriesOperationsWindow(PydidasWindow):
    """
    Window with a simple dialogue to select a number of files and perform basic
    mathematical operations on them.
    """

    show_frame = False
    default_params = get_generic_param_collection(
        "first_file",
        "last_file",
        *_HDF5_PARAM_KEYS,
        "output_fname",
    )
    default_params.add_param(_operation)

    def __init__(self, **kwargs: dict):
        PydidasWindow.__init__(self, title="Image series operations", **kwargs)
        self._filelist = FilelistManager(*self.get_params("first_file", "last_file"))
        self._config["num_frames_per_file"] = 1

    def build_frame(self):
        """
        Build the frame and create all widgets.
        """

        def get_config(param_key):
            _config = {
                "linebreak": param_key
                in ["first_file", "last_file", "hdf5_key", "output_fname"],
                "visible": param_key
                in [
                    "first_file",
                    "output_fname",
                    "operation",
                ],
                "parent_widget": "config_canvas",
            }
            if param_key == "first_file":
                _config["persistent_qsettings_ref"] = (
                    "ImageSeriesOperationsWindow__import_file"
                )
            if param_key == "last_file":
                _config["persistent_qsettings_ref"] = (
                    "ImageSeriesOperationsWindow__import_file"
                )
            if param_key == "output_fname":
                _config["persistent_qsettings_ref"] = (
                    "ImageSeriesOperationsWindow__export_file"
                )
            return _config

        _sub_section_config = {
            "fontsize_offset": 1,
            "font_metric_width_factor": FONT_METRIC_PARAM_EDIT_WIDTH,
            "bold": True,
            "parent_widget": "config_canvas",
        }
        self.create_empty_widget(
            "config_canvas",
            font_metric_width_factor=FONT_METRIC_PARAM_EDIT_WIDTH,
        )

        self.create_label(
            "label_title",
            "Image series operations",
            fontsize_offset=4,
            bold=True,
            font_metric_width_factor=FONT_METRIC_PARAM_EDIT_WIDTH,
            parent_widget="config_canvas",
        )
        self.create_spacer(None, parent_widget="config_canvas")
        self.create_label("label_input", "Input selection", **_sub_section_config)
        for _key in ["first_file", "last_file", *_HDF5_PARAM_KEYS]:
            self.create_param_widget(self.params[_key], **get_config(_key))

        self.create_spacer(None)
        self.create_label("label_operation", "Operation", **_sub_section_config)
        self.create_param_widget(self.params["operation"], **get_config("operation"))
        self.create_spacer(None)
        self.create_label("label_output", "Output", **_sub_section_config)
        self.create_param_widget(
            self.params["output_fname"], **get_config("output_fname")
        )
        self.create_spacer(None)
        self.create_check_box(
            "check_keep_open", "Close window after processing", checked=True
        )
        self.create_button("but_exec", "Process and export image")
        self.process_new_font_metrics()

    def connect_signals(self):
        """
        Build the frame and create all widgets.
        """
        self._widgets["but_exec"].clicked.connect(self.process_file_series)
        self.param_widgets["first_file"].io_edited.connect(self.__selected_first_file)
        QtWidgets.QApplication.instance().sig_font_metrics_changed.connect(
            self.process_new_font_metrics
        )

    @QtCore.Slot()
    def process_new_font_metrics(self):
        """
        Process the user input of the new font size.
        """
        self.setFixedWidth(self._widgets["config_canvas"].sizeHint().width() + 20)
        self.adjustSize()

    @QtCore.Slot(str)
    def __selected_first_file(self, fname):
        """
        Perform required actions after selecting the first image file.

        This method checks whether a hdf5 file has been selected and shows/
        hides the required fields for selecting the dataset or the last file
        in case of a file series.
        If an hdf5 image file has been selected, this method also opens a
        pop-up for dataset selection.

        Parameters
        ----------
        fname : str
            The filename of the first image file.
        """
        self.__clear_entries(["last_file", *_HDF5_PARAM_KEYS])
        if not os.path.isfile(fname):
            return
        self.__update_widgets_after_selecting_first_file()
        self.__update_file_selection()
        if get_extension(self.get_param_value("first_file")) in HDF5_EXTENSIONS:
            self.__popup_select_hdf5_key(fname)

    def __clear_entries(self, keys="all", hide=True):
        """
        Clear the Parameter entries and reset to default for selected keys.

        Parameters
        ----------
        keys : Union['all', list, tuple], optional
            The keys for the Parameters to be reset. The default is 'all'.
        hide : bool, optional
            Flag for hiding the reset keys. The default is True.
        """
        keys = keys if keys != "all" else list(self.params.keys())
        for _key in keys:
            param = self.params[_key]
            param.restore_default()
            self.param_widgets[_key].set_value(param.default)
        for _key in ["last_file", *_HDF5_PARAM_KEYS]:
            if _key in keys:
                self.toggle_param_widget_visibility(_key, not hide)

    def __update_widgets_after_selecting_first_file(self):
        """
        Update widget visibilty after selecting the first file based on the
        file format (hdf5 or not).
        """
        hdf5_flag = get_extension(self.get_param_value("first_file")) in HDF5_EXTENSIONS
        for _key in _HDF5_PARAM_KEYS:
            self.toggle_param_widget_visibility(_key, hdf5_flag)
        self.toggle_param_widget_visibility("last_file", True)

    def __update_file_selection(self):
        """
        Update the filelist based on the current selection.
        """
        try:
            self._filelist.update()
        except UserConfigError as _ex:
            self.__clear_entries(["last_file"], hide=False)
            QtWidgets.QMessageBox.critical(self, "Could not create filelist.", str(_ex))

    def __popup_select_hdf5_key(self, fname):
        """
        Create a popup window which asks the user to select a dataset.

        Parameters
        ----------
        fname : str
            The filename to the hdf5 data file.
        """
        dset = dialogues.Hdf5DatasetSelectionPopup(self, fname).get_dset()
        if dset is not None:
            self.set_param_value_and_widget("hdf5_key", dset)

    @QtCore.Slot()
    def process_file_series(self):
        """
        Process the file series.
        """
        if not IoManager.is_extension_registered(
            self.get_param_value("output_fname").suffix
        ):
            raise UserConfigError(
                "The output filename does not have a valid extension. Please choose "
                "a valid filename."
            )
        self._filelist.update()
        if get_extension(self.get_param_value("first_file")) in HDF5_EXTENSIONS:
            self._calculate_hdf5_frame_limits()
        _n_frames = self._filelist.n_files * self._config["num_frames_per_file"]
        _hdf5_dset = self.get_param_value("hdf5_key")
        _base_indices = (None,) * self.get_param_value("hdf5_slicing_axis")
        self._data = None
        self._dtype = None
        with ShowBusyMouse():
            for _index in range(0, _n_frames):
                _fname, _i_frame = self._get_fname_and_frame_number(_index)
                _frame = import_data(
                    _fname, dataset=_hdf5_dset, indices=_base_indices + (_i_frame,)
                )
                if self._data is None:
                    self._data = _frame.astype(np.uint64)
                    self._dtype = _frame.dtype.type
                else:
                    self._apply_operation(_frame)
            self._final_operation()
            self._reduce_integer_dtype()
            export_data(
                self.get_param_value("output_fname"), self._data, overwrite=True
            )
        if self._widgets["check_keep_open"].isChecked():
            self.close()

    def _calculate_hdf5_frame_limits(self):
        """
        Calculate the limits for the hdf5 frame indices.
        """
        _start_index = self.get_param_value("hdf5_first_image_num")
        _max_index = self.get_param_value("hdf5_last_image_num") + 1
        _key = self.get_param_value("hdf5_key")
        if _max_index == 0:
            _fname = self._filelist.get_filename(0)
            _max_index = get_hdf5_metadata(_fname, ["shape"], dset=_key)[
                self.get_param_value("hdf5_slicing_axis")
            ]
        self._config["hdf5_frames"] = [_start_index, _max_index]
        self._config["num_frames_per_file"] = _max_index - _start_index

    def _get_fname_and_frame_number(self, index):
        """
        Get the filename and frame number for an image index.

        Parameters
        ----------
        index : int
            The frame index.

        Returns
        -------
        tuple
            The filename and frame number for the selected index.
        """
        _i_file = index // self._config["num_frames_per_file"]
        _frame = index % self._config["num_frames_per_file"]
        _fname = self._filelist.get_filename(_i_file)
        return (_fname, _frame)

    def _apply_operation(self, frame):
        """
        Apply the selected operation on the input frame and the global data.

        Parameters
        ----------
        frame : pydidas.core.Dataset
            The current frame.
        data : pydidas.core.Dataset
            The stored global processing data.
        """
        _op = self.get_param_value("operation")
        if _op in ["sum", "mean"]:
            self._data = self._data + frame
        elif _op == "max":
            self._data = np.maximum(self._data, frame)

    def _final_operation(self):
        """
        Apply the final operation to the data, e.g. normalization for average.
        """
        _op = self.get_param_value("operation")
        if _op == "mean":
            _n_frames = self._filelist.n_files * self._config["num_frames_per_file"]
            self._data = self._data / _n_frames

    def _reduce_integer_dtype(self):
        """
        Reduce the datatype of integer values to use as little disk space as possible.
        """
        if not issubclass(self._data.dtype.type, numbers.Integral):
            return
        _min = np.amin(self._data)
        _max = np.amax(self._data)
        # handle unsigned case:
        if _min >= 0:
            for _bytes in [8, 16, 32]:
                if _max < 2**_bytes:
                    _type = getattr(np, f"uint{_bytes}")
                    self._data = self._data.astype(_type)
                    return
        # handle signed case:
        else:
            for _bytes in [8, 16, 32]:
                if -(2 ** (_bytes - 1)) <= _min and _max < 2 ** (_bytes - 1):
                    _type = getattr(np, f"int{_bytes}")
                    self._data = self._data.astype(_type)
                    return
