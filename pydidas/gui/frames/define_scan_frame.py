# This file is part of pydidas.
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
# along with Pydidas. If not, see <http://www.gnu.org/licenses/>.

"""
Module with the DefineScanFrame which is used to manage and modify the scan
settings like dimensionality, number of points and labels.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2024, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"
__all__ = ["DefineScanFrame"]


from functools import partial

from qtpy import QtCore, QtWidgets

from ...contexts import ScanContext, ScanIo
from ...plugins import PluginCollection
from ...widgets import PydidasFileDialog
from ...widgets.framework import BaseFrame
from ...widgets.windows import ScanDimensionInformationWindow
from ...workflow import WorkflowTree
from .builders import DefineScanFrameBuilder


SCAN = ScanContext()
PLUGINS = PluginCollection()
WORKFLOW = WorkflowTree()


DIM_LABELS = {
    1: {i: "\nScan dimension 0:" for i in range(4)},
    2: {0: "\nScan dimension 0 (slow):", 1: "\nScan dimension 1 (fast):"},
    3: {
        0: "\nScan dimension 0 (slowest):",
        1: "\nScan dimension 1:",
        2: "\nScan dimension 2 (fastest):",
    },
    4: {
        0: "\nScan dimension 0 (slowest):",
        1: "\nScan dimension 1:",
        2: "\nScan dimension 2:",
        3: "\nScan dimension 3 (fastest):",
    },
}


class DefineScanFrame(BaseFrame):
    """
    Frame for managing the global scan setup.
    """

    menu_icon = "pydidas::frame_icon_define_scan"
    menu_title = "Define\nscan"
    menu_entry = "Workflow processing/Define scan"

    def __init__(self, **kwargs: dict):
        BaseFrame.__init__(self, **kwargs)
        self._io_dialog = PydidasFileDialog()
        self._qtapp = QtWidgets.QApplication.instance()
        self.__info_window = ScanDimensionInformationWindow()

    def build_frame(self):
        """
        Populate the frame with widgets.
        """
        DefineScanFrameBuilder.build_frame(self)

    def connect_signals(self):
        """
        Connect all required signals and slots.
        """
        self._widgets["but_save"].clicked.connect(self.export_to_file)
        self._widgets["but_load"].clicked.connect(self.load_from_file)
        self._widgets["but_reset"].clicked.connect(self.reset_entries)
        self._widgets["but_more_scan_dim_info"].clicked.connect(self._show_info_window)
        self.param_widgets["scan_dim"].currentTextChanged.connect(
            self.update_dim_visibility
        )
        for _index in range(4):
            self._widgets[f"button_up_{_index}"].clicked.connect(
                partial(self.move_dim, _index, -1)
            )
            self._widgets[f"button_down_{_index}"].clicked.connect(
                partial(self.move_dim, _index, 1)
            )
        self.param_widgets["scan_base_directory"].io_edited.connect(
            self.set_new_base_directory
        )
        self._qtapp.sig_exit_pydidas.connect(self.__info_window.close)

    def finalize_ui(self):
        """
        Finalize the UI initialization.
        """
        self.__info_window.frame_activated(self.__info_window.frame_index)
        self.update_dim_visibility()
        for param in SCAN.params.values():
            self.param_widgets[param.refkey].set_value(param.value)

    def update_dim_visibility(self):
        """
        Update the visibility of dimensions based on the selected number
        of scan dimensions.
        """
        _prefixes = [
            "scan_dim{n}_label",
            "scan_dim{n}_n_points",
            "scan_dim{n}_delta",
            "scan_dim{n}_unit",
            "scan_dim{n}_offset",
        ]
        _dim = int(self.param_widgets["scan_dim"].currentText())
        for i in range(4):
            _toggle = i < _dim
            self._widgets[f"title_{i}"].setVisible(_toggle)
            self._widgets[f"button_up_{i}"].setVisible(0 < i < _dim)
            self._widgets[f"button_down_{i}"].setVisible(i < _dim - 1)
            for _pre in _prefixes:
                self.toggle_param_widget_visibility(_pre.format(n=i), _toggle)
            if i in DIM_LABELS[_dim].keys():
                self._widgets[f"title_{i}"].setText(DIM_LABELS[_dim][i])
        _total_width = DefineScanFrameBuilder.width_factor(_dim in [3, 4])
        self._widgets["master"].font_metric_width_factor = _total_width
        self._widgets["config_B"].setVisible(_dim in [3, 4])
        self._widgets["config_area"].force_width_from_size_hint()

    @QtCore.Slot()
    def load_from_file(self):
        """
        Load ScanContext from a file.

        This method will open a QFileDialog to select the file to be read.
        """
        _fname = self._io_dialog.get_existing_filename(
            caption="Import scan context file",
            formats=ScanIo.get_string_of_formats(),
            qsettings_ref="DefineScanFrame__import",
        )
        if _fname is not None:
            SCAN.import_from_file(_fname)
            for param in SCAN.params.values():
                self.param_widgets[param.refkey].set_value(param.value)

    @QtCore.Slot()
    def export_to_file(self):
        """
        Save ScanContext to a file.

        This method will open a QFileDialog to select a filename for the
        file in which the information shall be written.
        """
        _fname = self._io_dialog.get_saving_filename(
            caption="Export scan context file",
            formats=ScanIo.get_string_of_formats(),
            default_extension="yaml",
            qsettings_ref="DefineScanFrame__export",
        )
        if _fname is not None:
            SCAN.export_to_file(_fname, overwrite=True)

    @QtCore.Slot()
    def reset_entries(self):
        """
        Reset all ScanSetting entries to their default values.
        """
        SCAN.restore_all_defaults(True)
        for param in SCAN.params.values():
            self.param_widgets[param.refkey].set_value(param.value)

    @QtCore.Slot(int, int)
    def move_dim(self, dim_index: int, direction: int):
        """
        Move the selected dimension' position in the scan.

        Parameters
        ----------
        dim_index : int
            The index of the selected dimension.
        direction : int
            The direction. Use -1 for up and 1 for down.
        """
        _previous_dim_entries = {
            _key: SCAN.get_param_value(f"scan_dim{dim_index + direction}_{_key}")
            for _key in ["label", "n_points", "delta", "unit", "offset"]
        }
        for _key in ["label", "n_points", "delta", "unit", "offset"]:
            SCAN.set_param_value(
                f"scan_dim{dim_index + direction}_{_key}",
                SCAN.get_param_value(f"scan_dim{dim_index}_{_key}"),
            )
            SCAN.set_param_value(
                f"scan_dim{dim_index}_{_key}", _previous_dim_entries[f"{_key}"]
            )
            self.update_widget_value(
                f"scan_dim{dim_index + direction}_{_key}",
                SCAN.get_param_value(f"scan_dim{dim_index + direction}_{_key}"),
            )
            self.update_widget_value(
                f"scan_dim{dim_index}_{_key}",
                SCAN.get_param_value(f"scan_dim{dim_index}_{_key}"),
            )

    @QtCore.Slot(str)
    def set_new_base_directory(self, basedir: str):
        """
        Set the new base directory for the scan.

        Parameters
        ----------
        basedir : str
            The new base directory
        """
        self.q_settings_set("dialogues/DefineScanFrame__scan_name_pattern", basedir)

    @QtCore.Slot()
    def _show_info_window(self):
        """
        Show the information window about scan dimensions.
        """
        self.__info_window.show()
        self.__info_window.raise_()
