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
Module with the ImageSeriesOperationsWindow class which allows to perform mathematical
operations on a number of images.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2021-2022, Malte Storm, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0"
__maintainer__ = "Malte Storm"
__status__ = "Development"
__all__ = ["ImageSeriesOperationsWindow"]

import os
import numbers

from qtpy import QtCore, QtWidgets
import numpy as np

from ...core import get_generic_param_collection, UserConfigError, Parameter
from ...core.constants import (
    DEFAULT_TWO_LINE_PARAM_CONFIG,
    CONFIG_WIDGET_WIDTH,
    HDF5_EXTENSIONS,
)
from ...core.utils import get_hdf5_metadata, get_extension, ShowBusyMouse
from ...data_io import import_data, export_data
from ...managers import FilelistManager
from ...widgets import dialogues
from .pydidas_window import PydidasWindow


_operation = Parameter(
    "operation",
    str,
    "mean",
    name="Image series operator",
    choices=["mean", "sum", "max"],
    tooltip=("The mathematical operation to be applied to the image series."),
)


class ImageSeriesOperationsWindow(PydidasWindow):
    """
    Window with a simple dialogue to select a number of files and
    """

    show_frame = False
    default_params = get_generic_param_collection(
        "first_file",
        "last_file",
        "hdf5_key",
        "hdf5_first_image_num",
        "hdf5_last_image_num",
        "output_fname",
    )
    default_params.add_param(_operation)

    def __init__(self, parent=None, **kwargs):
        PydidasWindow.__init__(self, parent, title="Average images", **kwargs)
        self._filelist = FilelistManager(*self.get_params("first_file", "last_file"))
        self.setWindowTitle("Image series operations")
        self._config["num_frames_per_file"] = 1

    def build_frame(self):
        """
        Build the frame and create all widgets.
        """

        def get_config(param_key):
            if param_key in ["first_file", "last_file", "hdf5_key", "output_fname"]:
                _config = DEFAULT_TWO_LINE_PARAM_CONFIG.copy()
            else:
                _config = dict(
                    width_io=100,
                    width_unit=0,
                    width_text=CONFIG_WIDGET_WIDTH - 100,
                    width_total=CONFIG_WIDGET_WIDTH,
                )
            _config["visible"] = param_key in [
                "first_file",
                "output_fname",
                "operation",
            ]
            return _config

        self.create_label(
            "label_title",
            "File series operations",
            fontsize=14,
            bold=True,
        )
        self.create_spacer(None)
        self.create_label(
            "label_input",
            "Input selection",
            fontsize=11,
            bold=True,
        )
        for _key in [
            "first_file",
            "last_file",
            "hdf5_key",
            "hdf5_first_image_num",
            "hdf5_last_image_num",
        ]:
            self.create_param_widget(self.params[_key], **get_config(_key))

        self.create_spacer(None)
        self.create_label(
            "label_operation",
            "Operation",
            fontsize=11,
            bold=True,
        )
        self.create_param_widget(self.params["operation"], **get_config("operation"))
        self.create_spacer(None)
        self.create_label(
            "label_output",
            "Output",
            fontsize=11,
            bold=True,
        )
        self.create_param_widget(
            self.params["output_fname"], **get_config("output_fname")
        )
        self.create_spacer(None)
        self.create_button("but_exec", "Process and save image")

    def connect_signals(self):
        """
        Build the frame and create all widgets.
        """
        self._widgets["but_exec"].clicked.connect(self.process_file_series)
        self.param_widgets["first_file"].io_edited.connect(self.__selected_first_file)

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
        self.__clear_entries(
            ["last_file", "hdf5_key", "hdf5_first_image_num", "hdf5_last_image_num"]
        )
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
        for _key in [
            "hdf5_key",
            "hdf5_first_image_num",
            "hdf5_last_image_num",
            "last_file",
        ]:
            if _key in keys:
                self.toggle_param_widget_visibility(_key, not hide)

    def __update_widgets_after_selecting_first_file(self):
        """
        Update widget visibilty after selecting the first file based on the
        file format (hdf5 or not).
        """
        hdf5_flag = get_extension(self.get_param_value("first_file")) in HDF5_EXTENSIONS
        for _key in ["hdf5_key", "hdf5_first_image_num", "hdf5_last_image_num"]:
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
        self._filelist.update()
        if get_extension(self.get_param_value("first_file")) in HDF5_EXTENSIONS:
            self._calculate_hdf5_frame_limits()
        _n_frames = self._filelist.n_files * self._config["num_frames_per_file"]
        _hdf5_dset = self.get_param_value("hdf5_key")
        self._data = None
        self._dtype = None
        with ShowBusyMouse():
            for _index in range(0, _n_frames):
                _fname, _frame_number = self._get_fname_and_frame_number(_index)
                _frame = import_data(_fname, dataset=_hdf5_dset, frame=_frame_number)
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
            _max_index = get_hdf5_metadata(_fname, ["shape"], dset=_key)[0]
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
            self._data += frame
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
        if not numbers.Integral.__subclasscheck__(self._data.dtype.type):
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
