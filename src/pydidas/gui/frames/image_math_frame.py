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
Module with the ImageMathFrame which allows to perform mathematical
operations on images.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2024 - 2025, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"
__all__ = ["ImageMathFrame"]


from pathlib import Path

import numpy as np
from qtpy import QtCore, QtWidgets

from pydidas.contexts import ScanContext
from pydidas.core import (
    ParameterCollection,
    UserConfigError,
    constants,
    get_generic_param_collection,
)
from pydidas.data_io import IoManager, export_data, import_data
from pydidas.gui.frames.builders import ImageMathFrameBuilder
from pydidas.widgets import PydidasFileDialog
from pydidas.widgets.framework import BaseFrame
from pydidas.workflow import WorkflowTree


SCAN_SETTINGS = ScanContext()
WORKFLOW_TREE = WorkflowTree()


_DEFAULTS = ParameterCollection(
    get_generic_param_collection(
        "filename",
        "hdf5_key",
        "hdf5_frame",
        "hdf5_slicing_axis",
        "current_filename",
    ),
)


_OPS = {"+": np.add, "-": np.subtract, "/": np.divide, "x": np.multiply}


class ImageMathFrame(BaseFrame):
    """
    The ImageMathFrame allows to perform mathematical operations on single
    frames or to combine multiple frames.
    """

    menu_icon = "pydidas::frame_icon_image_math"
    menu_title = "Image math"
    menu_entry = "Image math"

    default_params = _DEFAULTS.copy()
    BUFFER_SIZE = 3

    def __init__(self, **kwargs: dict):
        BaseFrame.__init__(self, **kwargs)
        self.set_default_params()
        self._image_buffer = {_key: None for _key in range(1, self.BUFFER_SIZE + 1)}
        self._input_image_buffer = {
            _key: None for _key in range(1, self.BUFFER_SIZE + 1)
        }
        self._input_image_names = {_key: "" for _key in range(1, self.BUFFER_SIZE + 1)}
        self._input_image_paths = {
            _key: None for _key in range(1, self.BUFFER_SIZE + 1)
        }
        self._ops = {"func": np.log, "param2": 0}
        self._input = {"data": None, "path": None, "name": None}
        self._current_image = None
        self.__export_dialog = PydidasFileDialog()

    def build_frame(self):
        """
        Build the frame and create all widgets.
        """
        ImageMathFrameBuilder.populate_frame(self)
        self._toggle_features_enabled(False)
        self._widgets["combo_display_image"].setEnabled(False)

    @property
    def active_index(self) -> int:
        """
        Get the active buffer index.

        Returns
        -------
        int
            The current buffer index.
        """
        return int(self.get_param_value("buffer_no").split("#")[1])

    def connect_signals(self):
        """
        Connect all signals.
        """
        self._widgets["file_selector"].sig_new_file_selection.connect(self.open_image)
        self._widgets["but_store_input_image"].clicked.connect(self._store_input_image)
        self._widgets["combo_display_image"].currentTextChanged.connect(
            self.new_buffer_selection
        )
        self._widgets["but_ops_arithmetic_execute"].clicked.connect(
            self._apply_arithmetic
        )

        self._widgets["ops_operator_func"].currentTextChanged.connect(
            self._operator_changed
        )
        self._widgets["but_ops_operator_execute"].clicked.connect(self._apply_operator)
        self._widgets["but_ops_image_arithmetic_execute"].clicked.connect(
            self._apply_image_arithmetic
        )
        self._widgets["but_export"].clicked.connect(self._export_image)

    def finalize_ui(self):
        """
        Finalizes the UI and restore the SelectImageFrameWidgets params.
        """
        self._widgets["file_selector"].restore_param_widgets()

    def restore_state(self, state: dict):
        """
        Restore the GUI state.

        Parameters
        ----------
        state : dict
            The frame's state dictionary.
        """
        BaseFrame.restore_state(self, state)
        if self._config["built"]:
            self._widgets["file_selector"].restore_param_widgets()

    @QtCore.Slot(str, dict)
    def open_image(self, filename: str, open_kwargs: dict):
        """
        Open an image with the given filename and display it in the plot.

        Parameters
        ----------
        filename : Union[str, Path]
            The filename and path.
        open_kwargs : dict
            Additional parameters to open a specific frame in a file.
        """
        _fname = Path(filename).name
        if Path(filename).suffix[1:] in constants.HDF5_EXTENSIONS:
            _fname += (
                f"::{self.get_param_value('hdf5_key', dtype=str)}"
                f"::{self.get_param_value('hdf5_frame')}"
            )
        self._input["data"] = import_data(filename, **open_kwargs).astype(np.float32)
        self._input["name"] = _fname
        self._input["path"] = filename
        self._plot_image(input_data=True)
        self._widgets["combo_display_image"].setEnabled(True)

    @QtCore.Slot()
    def _store_input_image(self):
        """
        Store the input image in the buffer.
        """
        _index = int(
            self._widgets["combo_store_input_image"].currentText().split("#")[1]
        )
        self._input_image_buffer[_index] = self._input["data"]
        self._input_image_names[_index] = self._input["name"]
        self._input_image_paths[_index] = self._input["path"]

    @QtCore.Slot(str)
    def new_buffer_selection(self, new_value: str):
        """
        Process the change in the buffer selection.

        Parameters
        ----------
        new_value : str
            The new value of the buffer.
        """
        _text = self._widgets["combo_display_image"].currentText()
        if _text != new_value:
            with QtCore.QSignalBlocker(self._widgets["combo_display_image"]):
                self._widgets["combo_display_image"].setCurrentText(new_value)
        if new_value == "Opened file":
            self._plot_image(input_data=True)
            return
        _type, _number = new_value.split("#")
        _index = int(_number)
        if _type.strip() == "Image":
            self._plot_image(index=_index)
        elif _type.strip() == "Input image":
            self._plot_image(input_index=_index)

    def _plot_image(
        self, index: int = 0, input_index: int = 0, input_data: bool = False
    ):
        """
        Plot the image given by the specified index.

        Images can be specified by the index for processed images, input_index for
        input images or by input_data=True for the currently loaded frame.

        Parameters
        ----------
        index : int, optional
            The index for processed images. The default is 0.
        input_index : int
            The index for input images. The default is 0.
        input_data : bool, optional
            Flag to display the input image. The default is False.
        """
        if input_data and self._input["data"] is not None:
            _image = self._input["data"]
            _title = self._input["name"]
        elif index > 0 and self._image_buffer[index] is not None:
            _image = self._image_buffer[index]
            _title = f"Image #{index}"
        elif input_index > 0 and self._input_image_buffer[input_index] is not None:
            _image = self._input_image_buffer[input_index]
            _title = self._input_image_names[input_index]
        else:
            self._widgets["viewer"].clear_plot()
            self._current_image = None
            return
        self._current_image = _image
        self._widgets["viewer"].plot_pydidas_dataset(_image)
        self._widgets["viewer"].setGraphTitle(_title)
        self._widgets["viewer"].changeCanvasToDataAction._actionTriggered()
        self._toggle_features_enabled(True)

    def _toggle_features_enabled(self, enable: bool):
        """
        Toggle the enable state of processing features based on the validity of input.

        Parameters
        ----------
        enable : bool
            Flag to enable/disable features.
        """
        for _name in [
            "ops_operator",
            "but_ops_operator_execute",
            "store_input_image",
            "ops_arithmetic",
            "but_ops_arithmetic_execute",
            "ops_image_arithmetic",
            "but_ops_image_arithmetic_execute",
            "but_export",
        ]:
            self._widgets[_name].setEnabled(enable)

    @QtCore.Slot()
    def _apply_arithmetic(self):
        """Apply the selected arithmetic operation to the image."""
        _index_out = int(
            self._widgets["ops_arithmetic_target"].currentText().split("#")[1]
        )
        _ops_key = self._widgets["combo_ops_arithmetic_operation"].currentText()
        _number = self._widgets["io_ops_arithmetic_input"].text()
        try:
            _number = float(_number)
        except ValueError as _err:
            raise UserConfigError(
                f"Cannot convert the input `{_number}` to a number. Please check the "
                "given input."
            ) from _err
        _input = self.get_input_image(
            self._widgets["combo_ops_arithmetic_input"].currentText()
        )
        self._image_buffer[_index_out] = _OPS[_ops_key](_input, _number)
        self.new_buffer_selection(f"Image #{_index_out}")

    def get_input_image(self, label: str) -> np.ndarray:
        """
        Get the input image specified by the given string.

        Parameters
        ----------
        label : str
            The input string.

        Raises
        ------
        UserConfigError :
            If the selected input image is not a valid image.

        Returns
        -------
        np.ndarray
            The image to be processed.
        """
        _image = None
        if label == "Current image":
            _image = self._current_image
        elif label.startswith("Input image"):
            _num = int(label.split("#")[1])
            _image = self._input_image_buffer[_num]
        elif label.startswith("Image"):
            _num = int(label.split("#")[1])
            _image = self._image_buffer[_num]
        if _image is None:
            raise UserConfigError(
                f"The selected input image `{label}` is not a valid image. Please "
                "check the input settings."
            )
        return _image

    @QtCore.Slot(str)
    def _operator_changed(self, name: str):
        """
        Handle the change of the operator.

        Parameters
        ----------
        name : str
            The new operator name.
        """
        _func = getattr(np, name)
        for _name in [
            "label_ops_operator_sep",
            "io_ops_operator_input",
        ]:
            self._widgets[_name].setVisible(_func.nin == 2)
        self._ops["func"] = _func

    @QtCore.Slot()
    def _apply_operator(self):
        """Apply the selected operator to the input image."""
        _index_out = int(
            self._widgets["ops_operator_target"].currentText().split("#")[1]
        )
        _input = self.get_input_image(
            self._widgets["combo_ops_operator_input"].currentText()
        )
        _func = self._ops["func"]
        if _func.nin == 2:
            _arg2 = self._widgets["io_ops_operator_input"].text()
            try:
                _arg2 = float(_arg2)
            except ValueError as _error:
                raise UserConfigError(
                    f"Cannot convert the value {_arg2} to a number."
                ) from _error
            self._image_buffer[_index_out] = _func(_input, _arg2, dtype=np.float32)
        else:
            self._image_buffer[_index_out] = _func(_input, dtype=np.float32)
        self.new_buffer_selection(f"Image #{_index_out}")

    @QtCore.Slot()
    def _apply_image_arithmetic(self):
        """Apply the selected arithmetic operation to the selected images."""
        _index_out = int(
            self._widgets["ops_image_arithmetic_target"].currentText().split("#")[1]
        )
        _ops_key = self._widgets["combo_ops_image_arithmetic_operation"].currentText()
        _input1 = self.get_input_image(
            self._widgets["combo_ops_image_arithmetic_input_1"].currentText()
        )
        _input2 = self.get_input_image(
            self._widgets["combo_ops_image_arithmetic_input_2"].currentText()
        )
        if _input1.shape != _input2.shape:
            raise UserConfigError(
                "The selected images have different shapes and cannot be processed. "
                "Please select two images with the same shape."
            )
        self._image_buffer[_index_out] = _OPS[_ops_key](_input1, _input2)
        self.new_buffer_selection(f"Image #{_index_out}")

    @QtCore.Slot()
    def _export_image(self):
        """Export the current image."""
        if self._current_image is None:
            return
        _fname = self.__export_dialog.get_saving_filename(
            caption="Export image",
            formats=IoManager.get_string_of_formats("export"),
            default_extension="tiff",
            dialog=QtWidgets.QFileDialog.getSaveFileName,
            qsettings_ref="ImageMathFrame__export",
        )
        if _fname is not None:
            export_data(_fname, self._current_image, overwrite=True)
