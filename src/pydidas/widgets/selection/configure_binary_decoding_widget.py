# This file is part of pydidas
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
# along with pydidas If not, see <http://www.gnu.org/licenses/>.

"""
Module with the ConfigureBinaryDecodingWidget widget which allows to select the metadata
for raw encoded files.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2024 - 2025, Helmholtz-Zentrum Hereon"
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
from pydidas.widgets.utilities import get_pyqt_icon_from_str
from pydidas.widgets.widget_with_parameter_collection import (
    WidgetWithParameterCollection,
)


class ConfigureBinaryDecodingWidget(WidgetWithParameterCollection, AssociatedFileMixin):
    """
    A widget to configure the decoding of raw binary files. The widget allows
    to set the datatype, shape, and header offset of the binary file which is
    required to decode the file correctly.

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
        "filename", "raw_datatype", "raw_n_y", "raw_n_x", "raw_header"
    )
    sig_new_binary_image = QtCore.Signal(Path, dict)
    sig_new_binary_config = QtCore.Signal(dict)

    def __init__(self, **kwargs: Any):
        WidgetWithParameterCollection.__init__(self, **kwargs)
        if "params" in kwargs:
            self.add_params(kwargs["params"])
        self.set_default_params()
        AssociatedFileMixin.__init__(self, filename_param=self.get_param("filename"))
        self._config = {
            "decode_kwargs": {},
            "filesize": 0,
            "display_details": True,
        }
        self.__create_widgets()

    def __create_widgets(self):
        """
        Create all required widgets.
        """
        for _key in ["raw_datatype", "raw_n_y", "raw_n_x", "raw_header"]:
            self.create_param_widget(_key, gridPos=(-1, 0, 1, 1))
            self.param_composite_widgets[_key].sig_value_changed.connect(
                self._check_decoding_params
            )
        self.create_label(
            "decode_info",
            "",
            font_metric_height_factor=2,
            font_metric_width_factor=FONT_METRIC_PARAM_EDIT_WIDTH,
            gridPos=(4, 0, 1, 1),
            policy=POLICY_EXP_FIX,
        )
        self.create_button(
            "button_toggle_details",
            "Hide detailed options",
            clicked=self._toggle_details,
            icon="qt-std::SP_TitleBarShadeButton",
            gridPos=(4, 1, 1, 1),
        )

    @QtCore.Slot(str)
    def set_new_filename(self, name: str | Path):
        """
        Process a new filename.

        If the new filename has a suffix associated with raw binary files,
        show the widget.

        Parameters
        ----------
        name : Path or str
            The full file system path to the new file.
        """
        self.set_param_value("filename", name)
        self.setVisible(self.binary_file and self.current_filename_is_valid)
        if self.binary_file and self.current_filename_is_valid:
            self._config["filesize"] = self.current_filepath.stat().st_size
            self._check_decoding_params()

    @QtCore.Slot()
    def _check_decoding_params(self):
        """
        Check if the decoding parameters are valid for the current file size.
        """
        _dtype = NUMPY_HUMAN_READABLE_DATATYPES[self.get_param_value("raw_datatype")]
        _dtype_bytesize = np.dtype(_dtype).itemsize
        _n = self.get_param_value("raw_n_y") * self.get_param_value("raw_n_x")
        _expected_size = _n * _dtype_bytesize + self.get_param_value("raw_header")
        if _expected_size != self._config["filesize"]:
            _color = COLOR_RED
            self._widgets["decode_info"].setText(
                f"File size: {self._config['filesize']:,} bytes\n"
                f"decoder settings: {_expected_size:,} bytes."
            )
        else:
            _color = COLOR_GREEN
            self._widgets["decode_info"].setText("Decoding parameters are valid.")
            self._emit_new_image_settings()
        self._widgets["decode_info"].setStyleSheet("QLabel {color: " + _color + ";}")

    @QtCore.Slot()
    def _emit_new_image_settings(self):
        """
        Confirm the decoder settings and emit the signal.
        """
        self._config["decode_kwargs"] = {
            "datatype": NUMPY_HUMAN_READABLE_DATATYPES[
                self.get_param_value("raw_datatype")
            ],
            "offset": self.get_param_value("raw_header"),
            "shape": (self.get_param_value("raw_n_y"), self.get_param_value("raw_n_x")),
        }
        self.sig_new_binary_image.emit(
            self.current_filepath, self._config["decode_kwargs"]
        )
        self.sig_new_binary_config.emit(self._config["decode_kwargs"])

    @QtCore.Slot()
    def _toggle_details(self):
        """
        Toggle the visibility of the detailed dataset selection options.
        """
        _show = not self._config["display_details"]
        for _key in self.param_composite_widgets:
            self.toggle_param_widget_visibility(_key, _show)
        self._config["display_details"] = _show
        self._widgets["button_toggle_details"].setText(
            "Hide detailed options" if _show else "Show detailed options"
        )
        self._widgets["button_toggle_details"].setIcon(
            get_pyqt_icon_from_str("qt-std::SP_TitleBarShadeButton")
            if _show
            else get_pyqt_icon_from_str("qt-std::SP_TitleBarUnshadeButton")
        )
