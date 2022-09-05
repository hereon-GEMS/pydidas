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
Module with the MaskEditorWindow class which is a wrapper window to use the pyFAI
mask editor in pydidas.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2021-2022, Malte Storm, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0"
__maintainer__ = "Malte Storm"
__status__ = "Development"
__all__ = ["MaskEditorWindow"]

import os

from qtpy import QtCore, QtWidgets
from silx.gui.plot.MaskToolsWidget import MaskToolsWidget

from ...core import get_generic_param_collection, UserConfigError
from ...core.constants import (
    DEFAULT_TWO_LINE_PARAM_CONFIG,
    CONFIG_WIDGET_WIDTH,
    HDF5_EXTENSIONS,
)
from ...core.utils import get_extension
from ...data_io import import_data
from ...widgets import dialogues, silx_plot, parameter_config
from .pydidas_window import PydidasWindow


PARAM_CONFIG = dict(
    width_io=100,
    width_unit=0,
    width_text=CONFIG_WIDGET_WIDTH - 100,
    width_total=CONFIG_WIDGET_WIDTH,
)


class MaskEditorWindow(PydidasWindow):
    """
    Window with a simple dialogue to select a number of files and
    """

    show_frame = False
    default_params = get_generic_param_collection(
        "filename",
        "hdf5_key",
        "hdf5_frame",
    )

    def __init__(self, parent=None, **kwargs):
        PydidasWindow.__init__(self, parent, title="Average images", **kwargs)
        self.setWindowTitle("Mask editor")

    def build_frame(self):
        """
        Build the frame and create all widgets.
        """
        self.create_any_widget(
            "param_frame",
            parameter_config.ParameterEditFrame,
            gridPos=(0, 0, 1, 1),
        )
        self.create_label(
            "title",
            "Input reference data file (not the mask)",
            fontSize=11,
            bold=True,
            parent_widget=self._widgets["param_frame"],
        )
        self.create_param_widget(
            self.params["filename"],
            parent_widget=self._widgets["param_frame"],
            **DEFAULT_TWO_LINE_PARAM_CONFIG.copy(),
        )
        self.create_param_widget(
            self.params["hdf5_key"],
            parent_widget=self._widgets["param_frame"],
            visible=False,
            **DEFAULT_TWO_LINE_PARAM_CONFIG.copy(),
        )
        self.create_param_widget(
            self.params["hdf5_frame"],
            parent_widget=self._widgets["param_frame"],
            visible=False,
            **PARAM_CONFIG,
        )
        self.create_button(
            "button_open_file",
            "Open selected image file",
            parent_widget=self._widgets["param_frame"],
            enabled=False
        )
        self.create_spacer(None, parent_widget=self._widgets["param_frame"])
        self.create_label(
            "title",
            "Mask parameters",
            fontSize=11,
            bold=True,
            parent_widget=self._widgets["param_frame"],
        )

        self.create_any_widget("plot_2d", silx_plot.PydidasPlot2D, gridPos=(0, 1, 2, 1))

        self._widgets["mask_tools"] = MaskToolsWidget(
            self, plot=self._widgets["plot_2d"]
        )
        self._widgets["mask_tools"].setDirection(QtWidgets.QBoxLayout.TopToBottom)
        self._widgets["mask_tools"].setMultipleMasks("single")
        self._widgets["mask_tools"].setFixedWidth(CONFIG_WIDGET_WIDTH + 10)
        self.add_any_widget(
            "mask_tools", self._widgets["mask_tools"], gridPos=(1, 0, 1, 1)
        )

    def connect_signals(self):
        """
        Build the frame and create all widgets.
        """
        self._widgets["button_open_file"].clicked.connect(self._open_new_file)
        self.param_widgets["filename"].io_edited.connect(self.__selected_filename)

    @QtCore.Slot(str)
    def __selected_filename(self, fname):
        """
        Perform required actions after selecting the image filename.

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
        if not os.path.isfile(fname):
            return
        self._widgets["button_open_file"].setEnabled(True)
        hdf5_flag = get_extension(self.get_param_value("filename")) in HDF5_EXTENSIONS
        for _key in ["hdf5_key", "hdf5_frame"]:
            self.toggle_param_widget_visibility(_key, hdf5_flag)
            self.param_widgets[_key].set_value(self.params[_key].default)
        if not hdf5_flag:
            return
        dset = dialogues.Hdf5DatasetSelectionPopup(self, fname).get_dset()
        if dset is not None:
            self.set_param_value_and_widget("hdf5_key", dset)

    @QtCore.Slot()
    def _open_new_file(self):
        """
        Open a new file in the plot window.
        """
        _fname = self.get_param_value("filename")
        if not os.path.isfile(_fname):
            raise UserConfigError("The selected file cannot be found.")
        _dset = self.get_param_value("hdf5_key")
        _frame = self.get_param_value("hdf5_frame")
        _data = import_data(_fname, dataset=_dset, frame=_frame)
        self._widgets["plot_2d"].setData(_data)
