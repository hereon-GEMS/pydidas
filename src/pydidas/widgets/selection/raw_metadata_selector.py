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
Module with the RawMetadataSelector widget which allows to select the metadata
for raw encoded files.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2024 - 2025, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"
__all__ = ["RawMetadataSelector"]


from pathlib import Path

from qtpy import QtCore, QtWidgets

from pydidas.core import get_generic_param_collection
from pydidas.core.constants.file_extensions import BINARY_EXTENSIONS
from pydidas.core.constants.numpy_names import NUMPY_HUMAN_READABLE_DATATYPES
from pydidas.core.utils import get_extension
from pydidas.widgets.utilities import get_pyqt_icon_from_str
from pydidas.widgets.widget_with_parameter_collection import (
    WidgetWithParameterCollection,
)


class RawMetadataSelector(WidgetWithParameterCollection):
    """
    A compound widget to select metadata in raw image files.

    Parameters
    ----------
    **kwargs : dict
        Any additional keyword arguments. In addition to all QAttributes supported
        by QWidget, see below for supported arguments:
    """

    default_params = get_generic_param_collection(
        "raw_datatype", "raw_shape_y", "raw_shape_x", "raw_header"
    )
    sig_decode_params = QtCore.Signal(object)

    def __init__(self, **kwargs: dict):
        WidgetWithParameterCollection.__init__(self, **kwargs)
        self.add_params(self.default_params.copy())
        self._config = {
            "filename": Path(),
            "decode_kwargs": {},
            "display_details": True,
        }
        self.__create_widgets()

    def __create_widgets(self):
        """
        Create all required widgets.
        """
        for _key, _param in self.params.items():
            self.create_param_widget(_param, gridPos=(-1, 0, 1, 3))

        _row = self.layout().rowCount()
        self.create_check_box(
            "auto_load",
            "Automatically load files with these settings",
            gridPos=(_row, 0, 1, 1),
            font_metric_width_factor=50,
        )
        self.create_button(
            "confirm",
            "Decode raw data file",
            clicked=self._emit_decoder_settings,
            gridPos=(_row, 2, 1, 1),
            font_metric_width_factor=30,
        )
        self.create_spacer(
            "spacer",
            gridPos=(0, 4, 1, 1),
            policy=QtWidgets.QSizePolicy.Expanding,
            vertical_policy=QtWidgets.QSizePolicy.Fixed,
        )
        self.create_button(
            "button_toggle_details",
            "Hide detailed options",
            clicked=self._toggle_details,
            icon="qt-std::SP_TitleBarShadeButton",
            gridPos=(_row, 4, 1, 1),
        )

        self.setVisible(False)

    @QtCore.Slot(str)
    def new_filename(self, name: str):
        """
        Process the new filename.

        If the new filename has a suffix associated with raw files,
        show the widget.

        Parameters
        ----------
        name : str
            The full file system path to the new file.
        """
        self._config["filename"] = Path(name)
        if not self._config["filename"].is_file():
            return
        _is_raw = get_extension(Path(name), lowercase=True) in BINARY_EXTENSIONS
        self.setVisible(_is_raw)
        if not _is_raw:
            return
        if self._widgets["auto_load"].isChecked():
            self.sig_decode_params.emit(self._config["decode_kwargs"])

    @QtCore.Slot()
    def _emit_decoder_settings(self):
        """
        Confirm the decoder settings and emit the signal.
        """
        _dtype = NUMPY_HUMAN_READABLE_DATATYPES[self.get_param_value("raw_datatype")]
        _shape = (
            self.get_param_value("raw_shape_y"),
            self.get_param_value("raw_shape_x"),
        )
        self._config["decode_kwargs"] = {
            "datatype": _dtype,
            "offset": self.get_param_value("raw_header"),
            "shape": _shape,
        }
        self.sig_decode_params.emit(self._config["decode_kwargs"])

    def _toggle_details(self):
        """
        Toggle the visibility of the detailed dataset selection options.
        """
        _show = not self._config["display_details"]
        for _widget in self.param_composite_widgets.values():
            _widget.setVisible(_show)
        self._config["display_details"] = _show
        self._widgets["button_toggle_details"].setText(
            "Hide detailed options" if _show else "Show detailed options"
        )
        self._widgets["button_toggle_details"].setIcon(
            get_pyqt_icon_from_str("qt-std::SP_TitleBarShadeButton")
            if _show
            else get_pyqt_icon_from_str("qt-std::SP_TitleBarUnshadeButton")
        )
