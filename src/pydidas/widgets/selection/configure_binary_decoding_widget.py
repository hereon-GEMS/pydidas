# This file is part of pydidas
#
# Copyright 2024 - 2026, Helmholtz-Zentrum Hereon
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
# along with pydidas If not, see <http://www.gnu.org/licenses/>.

"""
Module with the ConfigureBinaryDecodingWidget which allows configuration
of metadata for raw encoded binary files.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2024 - 2026, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"
__all__ = ["ConfigureBinaryDecodingWidget"]


from pathlib import Path
from typing import Any

import numpy as np
from qtpy import QtCore

from pydidas.core import get_generic_param_collection
from pydidas.core.constants import (
    COLOR_GREEN,
    COLOR_RED,
    FONT_METRIC_PARAM_EDIT_WIDTH,
    POLICY_EXP_FIX,
)
from pydidas.core.constants.numpy_names import NUMPY_HUMAN_READABLE_DATATYPES
from pydidas.core.utils.associated_file_mixin import AssociatedFileMixin
from pydidas.widgets.widget_with_parameter_collection import (
    WidgetWithParameterCollection,
)


class ConfigureBinaryDecodingWidget(WidgetWithParameterCollection, AssociatedFileMixin):
    """
    A widget to configure the decoding of raw binary files.

    The widget allows to set the datatype, shape, and header offset
    of the binary file which is required to decode the file correctly.

    Parameters
    ----------
    **kwargs : Any
        Any additional keyword arguments. In addition to all QAttributes supported
        by QWidget, see below for supported arguments:

        params : ParameterCollection, optional
            A ParameterCollection with Parameters to share with this widget.
            If not given, new Parameters will be created.
    """

    default_params = get_generic_param_collection(
        "filename", "raw_datatype", "raw_n_y", "raw_n_x", "raw_header_size"
    )
    init_kwargs = ["params"]
    sig_new_binary_image = QtCore.Signal(Path, dict)
    sig_new_binary_config = QtCore.Signal(dict)
    sig_decoding_invalid = QtCore.Signal()

    def __init__(self, **kwargs: Any) -> None:
        WidgetWithParameterCollection.__init__(self, **kwargs)
        if "params" in kwargs:
            self.add_params(kwargs["params"])
        self.set_default_params()
        AssociatedFileMixin.__init__(self, filename_param=self.get_param("filename"))
        self._config = {
            "decode_kwargs": {},
            "filesize": 0,
        }
        self.__create_widgets()

    def __create_widgets(self) -> None:
        """Create all required widgets."""
        self.create_check_box(
            "show_decoding_details",
            "Show binary decoder settings",
            checked=True,
            font_metric_width_factor=FONT_METRIC_PARAM_EDIT_WIDTH,
        )
        self._widgets["show_decoding_details"].clicked.connect(self._toggle_details)
        for _key in ["raw_datatype", "raw_n_y", "raw_n_x", "raw_header_size"]:
            self.create_param_widget(_key)
            self.param_composite_widgets[_key].sig_value_changed.connect(
                self._check_decoding_params
            )
        self.create_label(
            "decode_info",
            "",
            font_metric_height_factor=2,
            font_metric_width_factor=FONT_METRIC_PARAM_EDIT_WIDTH,
            policy=POLICY_EXP_FIX,
        )
        self.create_spacer(None, fixedWidth=1, gridPos=(0, 1, 1, 1))
        self.layout().setColumnStretch(1, 1)  # type: ignore[attr-defined]

    @property
    def decoding_is_valid(self) -> bool:
        """Get the flag whether the current decoding settings are valid."""
        return self._config.get("decoding_is_valid", False)

    @property
    def datatype(self) -> type[np.dtype]:
        """Get the current datatype selected for decoding."""
        return NUMPY_HUMAN_READABLE_DATATYPES[self.get_param_value("raw_datatype")]

    @QtCore.Slot(str)
    def set_new_filename(self, filename: str | Path) -> None:
        """
        Process a new filename.

        If the new filename has a suffix associated with raw binary files,
        show the widget.

        Parameters
        ----------
        filename : Path or str
            The full file system path to the new file.
        """
        self.current_filepath = filename
        self.setVisible(self.binary_file and self.current_filename_is_valid)
        if self.binary_file and self.current_filename_is_valid:
            self._config["filesize"] = self.current_filepath.stat().st_size
            self._check_decoding_params()

    @QtCore.Slot()
    def _check_decoding_params(self) -> None:
        """Check if the decoding parameters are valid for the current file size."""
        _n = self.get_param_value("raw_n_y") * self.get_param_value("raw_n_x")
        _dtype_bytesize = np.dtype(self.datatype).itemsize
        _expected_size = _n * _dtype_bytesize + self.get_param_value("raw_header_size")
        _decoding_was_valid = self._config.get("decoding_is_valid", True)
        self._config["decoding_is_valid"] = _expected_size == self._config["filesize"]
        _color = COLOR_GREEN if self._config["decoding_is_valid"] else COLOR_RED
        self._widgets["decode_info"].setStyleSheet("QLabel {color: " + _color + ";}")
        if self._config["decoding_is_valid"]:
            self._widgets["decode_info"].setText("Decoding parameters are valid.")
            self._emit_new_image_settings()
        else:
            self._widgets["decode_info"].setText(
                f"File size: {self._config['filesize']:,} bytes\n"
                f"decoder settings: {_expected_size:,} bytes."
            )
            if _decoding_was_valid:
                self.sig_decoding_invalid.emit()  # type: ignore[attr-defined]

    @QtCore.Slot()
    def _emit_new_image_settings(self) -> None:
        """Confirm the decoder settings and emit the signal."""
        self._config["decode_kwargs"] = {
            "datatype": self.datatype,
            "offset": self.get_param_value("raw_header_size"),
            "shape": (self.get_param_value("raw_n_y"), self.get_param_value("raw_n_x")),
        }
        self.sig_new_binary_image.emit(  # type: ignore[attr-defined]
            self.current_filepath, self._config["decode_kwargs"]
        )
        self.sig_new_binary_config.emit(  # type: ignore[attr-defined]
            self._config["decode_kwargs"]
        )

    @QtCore.Slot(bool)
    def _toggle_details(self, checked: bool) -> None:
        """
        Toggle the visibility of the detailed dataset selection options.

        Parameters
        ----------
        checked : bool
            The checked state of the toggle button.
        """
        for _key in self.param_composite_widgets:
            self.toggle_param_widget_visibility(_key, checked)
