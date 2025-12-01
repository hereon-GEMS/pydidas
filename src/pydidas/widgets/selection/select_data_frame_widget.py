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

from pydidas.core import ParameterCollection, get_generic_param_collection
from pydidas.core.utils import (
    get_hdf5_metadata,
    get_hdf5_populated_dataset_keys,
)
from pydidas.core.utils._frame_slice_handler import FrameSliceHandler
from pydidas.core.utils.associated_file_mixin import AssociatedFileMixin
from pydidas.core.utils.hdf5_dataset_utils import get_generic_dataset
from pydidas.widgets.data_viewer import DataAxisSelector
from pydidas.widgets.file_dialog import PydidasFileDialog
from pydidas.widgets.selection import ConfigureBinaryDecodingWidget
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
        filename : Parameter | None, optional
            A Parameter to use for the filename selection. If None, a default
            Parameter will be created. The default is None.
        font_metric_width_factor : int | None, optional
            An optional factor to modify the width of text elements in the
            widget based on the font metrics. If None, the default width for
            the used Parameter widgets is applied. The default is None.
    """

    sig_new_selection = QtCore.Signal(str, dict)
    sig_file_valid = QtCore.Signal(bool)

    init_kwargs = WidgetWithParameterCollection.init_kwargs + [
        "import_reference",
        "ndim",
        "import_hdf5_metadata",
        "font_metric_width_factor",
    ]
    default_params = get_generic_param_collection(
        "filename",
        "hdf5_key_str",
        "slicing_axis",
    )

    def __init__(self, **kwargs: Any):
        WidgetWithParameterCollection.__init__(self, **kwargs)
        self.set_default_params()
        AssociatedFileMixin.__init__(self, filename_param=self.params["filename"])
        self.set_param_value_and_choices("slicing_axis", None, [None])
        self.__import_dialog = PydidasFileDialog()
        self.__import_qref = kwargs.get("import_reference", None)
        self.__ndim = kwargs.get("ndim", 2)
        self.__file_valid = False
        self.__import_hdf5_metadata = kwargs.get("import_hdf5_metadata", False)
        self._selection = FrameSliceHandler()
        self._create_widgets(kwargs)
        self.connect_signals()
        self._toggle_file_selection(False, emit_signal=False)

    def _create_widgets(self, kwargs: dict[str, Any]):
        """Create the widgets for the data frame selection."""
        _font_metric_width = kwargs.get("font_metric_width_factor", None)
        self.create_param_widget(
            "filename",
            font_metric_width_factor=_font_metric_width,
            linebreak=True,
            persistent_qsettings_ref=self.__import_qref,
        )
        self.create_param_widget(
            "hdf5_key_str",
            font_metric_width_factor=_font_metric_width,
            width_text=0.4,
        )
        self.create_param_widget(
            "slicing_axis",
            font_metric_width_factor=_font_metric_width,
            width_text=0.4,
        )
        self.create_any_widget(
            "index_selector",
            DataAxisSelector,
            0,
            multiline=True,
            allow_axis_use_modification=False,
        )
        self.add_any_widget(
            "binary_decoder",
            ConfigureBinaryDecodingWidget(
                params=ParameterCollection(self.get_param("filename"))
            ),
        )

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
        self._widgets["binary_decoder"].sig_new_binary_config.connect(
            self._new_valid_binary_config
        )
        self._widgets["binary_decoder"].sig_decoding_invalid.connect(
            self._process_binary_decoding_invalid
        )

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
            self._widgets["binary_decoder"].set_new_filename(_fname)
        else:
            self._toggle_file_selection(True)
            self._selected_new_frame()

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
        self._widgets["binary_decoder"].setVisible(selected and self.binary_file)
        self.__file_valid = selected
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
        self._toggle_file_selection(bool(_dsets))
        if not _dsets:
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

    @QtCore.Slot(dict)
    def _selected_new_frame(self, config: dict | None = None):
        """
        Open a new file / frame based on the input Parameters.

        Parameters
        ----------
        config : dict or None, optional
            Additional configuration options from external sources,
            (e.g. used for binary data). If None, a new config dict is
            created. The default is None.
        """
        if config is None:
            config = {}
        config["indices"] = self._selection.indices
        if self.hdf5_file:
            config["dataset"] = self.get_param_value("hdf5_key_str", dtype=str)
            config["import_metadata"] = self.__import_hdf5_metadata
        self.sig_new_selection.emit(self.current_filename, config)

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

    @QtCore.Slot(dict)
    def _new_valid_binary_config(self, config: dict):
        """
        Process a new binary image selection.

        Parameters
        ----------
        config : dict
            The binary decoding configuration.
        """
        if not self.__file_valid:
            self.__file_valid = True
            self.sig_file_valid.emit(True)
        self._selected_new_frame(config)

    @QtCore.Slot()
    def _process_binary_decoding_invalid(self):
        """Process invalid binary decoding settings."""
        self.__file_valid = False
        self.sig_file_valid.emit(False)
