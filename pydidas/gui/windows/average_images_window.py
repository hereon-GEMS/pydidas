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
Module with the AverageImagesWindow class which allows to average all images
from a number of files.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2021-2022, Malte Storm, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0"
__maintainer__ = "Malte Storm"
__status__ = "Development"
__all__ = ["AverageImagesWindow"]

import os

from qtpy import QtCore, QtWidgets
import numpy as np

from ...core import get_generic_param_collection, UserConfigError
from ...core.constants import (
    DEFAULT_TWO_LINE_PARAM_CONFIG,
    CONFIG_WIDGET_WIDTH,
    HDF5_EXTENSIONS,
)
from ...core.utils import get_hdf5_metadata, get_extension
from ...data_io import import_data, export_data
from ...managers import FilelistManager
from ...widgets import dialogues
from .pydidas_window import PydidasWindow


class AverageImagesWindow(PydidasWindow):
    """
    Window with a simple dialogue to export the average of several frames from
    one or multiple files.
    """

    show_frame = False
    default_params = get_generic_param_collection(
        "first_file",
        "last_file",
        "hdf5_key",
        "hdf5_first_image_num",
        "hdf5_last_image_num",
        "use_global_det_mask",
        "output_fname",
    )

    def __init__(self, parent=None, **kwargs):
        PydidasWindow.__init__(self, parent, title="Average images", **kwargs)
        self.set_param_value("use_global_det_mask", False)
        self._filelist = FilelistManager(*self.get_params("first_file", "last_file"))

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
                "use_global_det_mask",
            ]
            return _config

        self.create_label(
            "label_title",
            "Average images",
            fontsize=14,
            bold=True,
            gridPos=(0, 0, 1, 1),
        )
        self.create_spacer(None)
        self.create_label(
            "label_input",
            "Input selection",
            fontsize=12,
            bold=True,
            gridPos=(-1, 0, 1, 1),
        )
        for _key in self.params:
            _options = get_config(_key)
            if _key == "output_fname":
                self.create_spacer(None)
                self.create_label(
                    "label_output",
                    "Export filename",
                    fontsize=12,
                    bold=True,
                    gridPos=(-1, 0, 1, 1),
                )
            self.create_param_widget(self.params[_key], **_options)

        self.create_button("but_exec", "Store averaged image")

    def connect_signals(self):
        """
        Build the frame and create all widgets.
        """
        self._widgets["but_exec"].clicked.connect(self._export)
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
    def _export(self):
        """
        Export the averaged images.
        """
        self._filelist.update()
        _n = self._filelist.n_files
        _data = None
        _nimages = 0
        for _index in range(0, _n):
            _fname = self._filelist.get_filename(_index)
            if get_extension(_fname) in HDF5_EXTENSIONS:
                _tmpdata, _n_in_file = self.__read_hdf5_images(_fname)
                _nimages += _n_in_file
            else:
                _tmpdata = import_data(_fname)
                _nimages += 1
            if _data is None:
                _data = 1.0 * _tmpdata
            else:
                _data += _tmpdata
        if self.get_param_value("use_global_det_mask"):
            _mask_qsetting = self.q_settings_get_global_value("det_mask")
            if os.path.isfile(_mask_qsetting):
                _mask = import_data(_mask_qsetting)
                _data = np.where(_mask, 0, _data)
        _data /= _nimages
        export_data(self.get_param_value("output_fname"), _data.astype(np.float32))
        self.close()

    def __read_hdf5_images(self, fname):
        _start_index = self.get_param_value("hdf5_first_image_num")
        _max_index = self.get_param_value("hdf5_last_image_num") + 1
        _key = self.get_param_value("hdf5_key")
        if _max_index == 0:
            _max_index = get_hdf5_metadata(fname, ["shape"], dset=_key)[0]
        _data = None
        for _frame in range(_start_index, _max_index):
            _tmp = import_data(fname, frame=_frame, dataset=_key)
            if _data is None:
                _data = 1.0 * _tmp
            else:
                _data += _tmp
        return _data, (_max_index - _start_index)
