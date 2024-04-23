# This file is part of pydidas
#
# Copyright 2024, Helmholtz-Zentrum Hereon
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
__copyright__ = "Copyright 2024, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"
__all__ = ["RawMetadataSelector"]


from pathlib import Path

from qtpy import QtCore, QtWidgets

from ...core import PydidasGuiError, get_generic_param_collection
from ...core.constants.file_extensions import BINARY_EXTENSIONS
from ...core.constants.numpy_names import NUMPY_DATATYPES
from ...core.utils import get_extension
from ...data_io import import_data
from ..widget_with_parameter_collection import WidgetWithParameterCollection


class RawMetadataSelector(WidgetWithParameterCollection):
    """
    A compound widget to select metadata in raw image files.

    Parameters
    ----------
    **kwargs : dict
        Any additional keyword arguments. In addition to all QAttributes supported
        by QWidget, see below for supported arguments:

        plot_widget : Union[QWidget, None], optional
            A widget for plotting the data. It can also be registered later using
            the  *register_plot_widget* method. The default is None.
    """

    default_params = get_generic_param_collection(
        "raw_datatype", "raw_shape_y", "raw_shape_x", "raw_header"
    )
    sig_decode_params = QtCore.Signal(object, int, int)

    def __init__(self, **kwargs: dict):
        WidgetWithParameterCollection.__init__(self, **kwargs)
        self.add_params(self.default_params.copy())
        self._config = {"filename": None}
        self._show_image_method = None
        self.__plot = kwargs.get("plot_widget", None)
        if self.__plot is not None:
            self.register_plot_widget(self.__plot)
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
            clicked=self._decode_file,
            gridPos=(_row, 2, 1, 1),
            font_metric_width_factor=30,
        )
        self.setVisible(False)

    def register_plot_widget(self, widget: QtWidgets.QWidget):
        """
        Register a view widget to be used for full visualization of data.

        This method registers an external view widget for data visualization.
        Note that the widget must accept frames through a ``addImage`` method.

        Parameters
        ----------
        widget : QWidget
            A widget with a ``addImage`` method to pass frames.

        Raises
        ------
        TypeError
            If the widget does not have a ``addImage`` method.
        """
        if not isinstance(widget, QtWidgets.QWidget):
            raise TypeError("Error: Object must be a QWidget.")
        if not (hasattr(widget, "displayImage") or hasattr(widget, "addImage")):
            raise AttributeError(
                "Error: The selected widget is not supported, as it does not have an "
                "`addImage` or `displayImage` method."
            )
        self.__plot = widget
        if hasattr(widget, "displayImage"):
            self._show_image_method = widget.displayImage
        elif hasattr(widget, "addImage"):
            self._show_image_method = widget.addImage

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
        self.__filename = Path(name)
        if not self.__filename.is_file():
            return
        _is_raw = get_extension(self.__filename, lowercase=True) in BINARY_EXTENSIONS
        self.setVisible(_is_raw)
        if not _is_raw:
            return
        if self._widgets["auto_load"].isChecked():
            self._decode_file()

    @QtCore.Slot()
    def _decode_file(self):
        """
        Confirm the params and send them to the calling frame.
        """
        if not isinstance(self.__plot, QtWidgets.QWidget):
            raise PydidasGuiError("No plot widget has been registered.")
        _datatype = NUMPY_DATATYPES[self.get_param_value("raw_datatype")]
        _offset = self.get_param_value("raw_header")
        _shape = (
            self.get_param_value("raw_shape_y"),
            self.get_param_value("raw_shape_x"),
        )
        _data = import_data(
            self.__filename, datatype=_datatype, offset=_offset, shape=_shape
        )
        self._show_image_method(_data, legend="pydidas image")
