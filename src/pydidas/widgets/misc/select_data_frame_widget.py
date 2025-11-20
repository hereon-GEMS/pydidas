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

from typing import Any

from qtpy import QtCore

from pydidas.core import get_generic_param_collection
from pydidas.core.utils import (
    get_hdf5_metadata,
    get_hdf5_populated_dataset_keys,
    is_hdf5_filename,
)
from pydidas.core.utils._frame_slice_handler import FrameSliceHandler
from pydidas.core.utils.associated_file_mixin import AssociatedFileMixin
from pydidas.core.utils.hdf5_dataset_utils import get_generic_dataset
from pydidas.widgets.data_viewer import DataAxisSelector
from pydidas.widgets.file_dialog import PydidasFileDialog
from pydidas.widgets.widget_with_parameter_collection import (
    WidgetWithParameterCollection,
)


class SelectDataFrameWidget(WidgetWithParameterCollection, AssociatedFileMixin):
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

    sig_new_selection = QtCore.Signal(str, dict)
    sig_file_valid = QtCore.Signal(bool)
    init_kwargs = WidgetWithParameterCollection.init_kwargs + [
        "import_reference",
        "ndim",
    ]
    default_params = get_generic_param_collection(
        "filename",
        "hdf5_key_str",
        "slicing_axis",
        "raw_datatype",
        "raw_n_x",
        "raw_n_y",
        "raw_header",
    )

    def __init__(self, **kwargs: Any):
        WidgetWithParameterCollection.__init__(self, **kwargs)
        self.set_default_params()
        AssociatedFileMixin.__init__(self, filename_param=self.params["filename"])
        self.set_param_value_and_choices("slicing_axis", None, [None])
        self.__import_dialog = PydidasFileDialog()
        self.__import_qref = kwargs.get("import_reference", None)
        self.__ndim = kwargs.get("ndim", 2)
        self._selection = FrameSliceHandler()
        self._raw_filesize = 0
        self._create_widgets()
        self.connect_signals()
        self._toggle_file_selection(False, emit_signal=False)

    def _create_widgets(self):
        """Create the widgets for the data frame selection."""
        self.create_param_widget(
            "filename", linebreak=True, persistent_qsettings_ref=self.__import_qref
        )
        self.create_param_widget("hdf5_key_str", width_text=0.4)
        self.create_param_widget("slicing_axis", width_text=0.4)
        self.create_any_widget(
            "index_selector",
            DataAxisSelector,
            0,
            multiline=True,
            allow_axis_use_modification=False,
        )
        self.create_param_widget("raw_datatype", visible=False)
        self.create_param_widget("raw_n_x", visible=False)
        self.create_param_widget("raw_n_y", visible=False)
        self.create_param_widget("raw_header", visible=False)

    def connect_signals(self):
        """Connect the widget signals to the relevant slots."""
        self.param_composite_widgets["filename"].sig_value_changed.connect(
            self.process_new_filename
        )
        self.param_composite_widgets["hdf5_key_str"].sig_new_value.connect(
            self._selected_new_dset
        )
        self.param_composite_widgets["slicing_axis"].sig_new_value.connect(
            self._selected_new_slicing_axis
        )
        self._widgets["index_selector"].sig_new_slicing.connect(self._new_frame_index)

    @QtCore.Slot()
    def process_new_filename(self):
        """Process the input of a new filename in the Parameter widget."""
        _fname = self.get_param_value("filename")
        if not _fname.is_file():
            self._toggle_file_selection(False)
            self.raise_UserConfigError(
                "The selected filename is not a valid file. Please check the input "
                "and correct the path."
            )
        if self.hdf5_file:
            self._process_new_hdf5_filename()
        elif self.binary_file:
            self._store_raw_size()
        else:
            self._selected_new_frame()
        self._toggle_file_selection(True)

    def _toggle_file_selection(self, selected: bool, emit_signal: bool = True):
        """
        Modify widgets visibility and activation based on the file selection.

        Parameters
        ----------
        selected : bool
            Flag to process.
        emit_signal : bool, optional
            Flag to emit the file valid signal. The default is True.
        """
        _hdf5_ax_selection = (
            selected and self.hdf5_file and self._selection.ndim > self.__ndim
        )
        self.param_composite_widgets["hdf5_key_str"].setVisible(
            selected and self.hdf5_file
        )
        self.param_composite_widgets["slicing_axis"].setVisible(_hdf5_ax_selection)
        self._widgets["index_selector"].setVisible(_hdf5_ax_selection)
        for _key in ["raw_datatype", "raw_n_x", "raw_n_y", "raw_header"]:
            self.param_composite_widgets[_key].setVisible(self.binary_file)
        if emit_signal:
            self.sig_file_valid.emit(selected)

    def _process_new_hdf5_filename(self):
        """Process a new HDF5 filename: update dataset keys and axis selector."""
        _current_dset = self.get_param_value("hdf5_key_str", dtype=str)
        _dsets = get_hdf5_populated_dataset_keys(
            self.get_param_value("filename"),
            min_dim=self.__ndim,
            max_dim=self.__ndim + 1,
        )
        if not _dsets:
            self._toggle_file_selection(False)
            self.raise_UserConfigError(
                "The selected HDF5 file does not contain any datasets with "
                f"{self.__ndim} or {self.__ndim + 1} dimensions. Please select "
                "a different file."
            )
        if _current_dset not in _dsets:
            _current_dset = get_generic_dataset(_dsets)
        self.set_param_and_widget_value_and_choices(
            "hdf5_key_str", _current_dset, _dsets, emit_signal=False
        )
        self._selected_new_dset(_current_dset)

    @QtCore.Slot(str)
    def _selected_new_dset(self, dataset: str):
        """
        Process a new dataset selection.

        Parameters
        ----------
        dataset : str
            The selected dataset key.
        """
        _filename = self.get_param_value("filename", dtype=str)
        _meta = get_hdf5_metadata(f"{_filename}://{dataset}", ["shape", "ndim"])
        self._selection.shape = _meta["shape"]
        if self._selection.ndim == self.__ndim:
            self._selection.axis = None
            self.set_param_and_widget_value_and_choices("slicing_axis", None, [None])
        else:  #  self._selection.ndim == self.__ndim + 1
            _curr_ax = self.get_param_value("slicing_axis") or 0
            _choices = list(range(self._selection.ndim))
            self.set_param_and_widget_value_and_choices(
                "slicing_axis", _curr_ax, _choices, emit_signal=False
            )
            self._selected_new_slicing_axis(_curr_ax, emit_signal=False)
        self._widgets["index_selector"].setVisible(self._selection.ndim > self.__ndim)
        self.toggle_param_widget_visibility(
            "slicing_axis", self._selection.ndim > self.__ndim
        )
        self._selected_new_frame()

    @QtCore.Slot(str)
    def _selected_new_slicing_axis(self, axis_str: str, emit_signal: bool = True):
        """
        Process a new slicing axis selection.

        Parameters
        ----------
        axis_str : str
            The selected axis as string.
        emit_signal : bool, optional
            Flag to emit the new frame signal. The default is True.
        """
        if axis_str == "None":
            return
        _ax = int(axis_str)
        self._selection.axis = _ax
        with QtCore.QSignalBlocker(self._widgets["index_selector"]):
            self._widgets["index_selector"].set_axis_metadata(
                None, npoints=self._selection.shape[_ax], ndim=1, dim_label="Frame:"
            )
            self._widgets["index_selector"].set_to_value(self._selection.frame)
        if emit_signal:
            self._selected_new_frame()

    @QtCore.Slot()
    def _selected_new_frame(self):
        """
        Open a new file / frame based on the input Parameters.
        """
        _fname = self.get_param_value("filename", dtype=str)
        _options = {"indices": self._selection.indices}
        if is_hdf5_filename(_fname):
            _options["dataset"] = self.get_param_value("hdf5_key_str", dtype=str)
        self.sig_new_selection.emit(_fname, _options)

    @QtCore.Slot(int, str)
    def _new_frame_index(self, ax_index: int, frame_slice_str: str):  # noqa ARG001
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
        self._selection.frame = _index
        self._selected_new_frame()

    def _store_raw_size(self):
        """Store the raw file size in the relevant Parameter."""
        try:
            self._raw_filesize = self.get_param_value("filename").stat().st_size
        except Exception as e:
            self._raw_filesize = 0
            self._toggle_file_selection(False)
            self.raise_UserConfigError(
                "Could not access the selected raw file. Please check the input "
                f"and correct the path. Original error message:\n\n{e}"
            )
        self._decode_binary_file()

    def _decode_binary_file(self):
        """Decode the raw binary file settings and update Parameters."""
        # _datatype = NUMPY_HUMAN_READABLE_DATATYPES[self.get_param_value("raw_datatype")]
        # _shape_x = self.get_param_value("raw_n_x", dtype=int)
        # _shape_y = self.get_param_value("raw_n_y", dtype=int)
        # _header = self.get_param_value("raw_header", dtype=int)
        pass
