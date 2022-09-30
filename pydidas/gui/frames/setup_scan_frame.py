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
Module with the SetupScanFrame which is used to manage and modify the scan
settings like dimensionality, number of points and labels.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2021-2022, Malte Storm, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0"
__maintainer__ = "Malte Storm"
__status__ = "Development"
__all__ = ["SetupScanFrame"]

from functools import partial

from qtpy import QtWidgets, QtCore

from ...experiment import SetupScan, SetupScanIoMeta
from ...plugins import PluginCollection
from ...workflow import WorkflowTree
from .builders import SetupScanFrameBuilder


SCAN = SetupScan()
PLUGINS = PluginCollection()
WORKFLOW = WorkflowTree()


class SetupScanFrame(SetupScanFrameBuilder):
    """
    Frame for managing the global scan settings.
    """

    menu_icon = "qta::ei.move"
    menu_title = "Scan settings"
    menu_entry = "Workflow processing/Scan settings"

    def __init__(self, parent=None, **kwargs):
        SetupScanFrameBuilder.__init__(self, parent, **kwargs)

    def connect_signals(self):
        """
        Connect all required signals and slots.
        """
        self._widgets["but_save"].clicked.connect(self.export_to_file)
        self._widgets["but_load"].clicked.connect(self.load_from_file)
        self._widgets["but_reset"].clicked.connect(self.reset_entries)
        self.param_widgets["scan_dim"].currentTextChanged.connect(
            self.update_dim_visibility
        )
        for _index in range(1, 5):
            self._widgets[f"button_up_{_index}"].clicked.connect(
                partial(self.move_dim, _index, -1)
            )
            self._widgets[f"button_down_{_index}"].clicked.connect(
                partial(self.move_dim, _index, 1)
            )

    def finalize_ui(self):
        """
        Finalize the UI initialization.
        """
        self.update_dim_visibility()
        for param in SCAN.params.values():
            self.param_widgets[param.refkey].set_value(param.value)

    def update_dim_visibility(self):
        """
        Update the visibility of dimensions based on the selected number
        of scan dimensions.
        """
        _prefixes = [
            "scan_label_{n}",
            "n_points_{n}",
            "delta_{n}",
            "unit_{n}",
            "offset_{n}",
        ]
        _dim = int(self.param_widgets["scan_dim"].currentText())
        for i in range(1, 5):
            _toggle = i <= _dim
            self._widgets[f"title_{i}"].setVisible(_toggle)
            self._widgets[f"button_up_{i}"].setVisible(1 < i <= _dim)
            self._widgets[f"button_down_{i}"].setVisible(i < _dim)
            for _pre in _prefixes:
                self.toggle_param_widget_visibility(_pre.format(n=i), _toggle)

    @QtCore.Slot()
    def load_from_file(self):
        """
        Load SetupScan from a file.

        This method will open a QFileDialog to select the file to be read.
        """
        _formats = SetupScanIoMeta.get_string_of_formats()
        fname = QtWidgets.QFileDialog.getOpenFileName(
            self, "Name of file", None, _formats
        )[0]
        if fname != "":
            SCAN.import_from_file(fname)
            for param in SCAN.params.values():
                self.param_widgets[param.refkey].set_value(param.value)

    @QtCore.Slot()
    def export_to_file(self):
        """
        Save SetupScan to a file.

        This method will open a QFileDialog to select a filename for the
        file in which the information shall be written.
        """
        _formats = SetupScanIoMeta.get_string_of_formats()
        fname = QtWidgets.QFileDialog.getSaveFileName(
            self, "Name of file", None, _formats
        )[0]
        if fname != "":
            SCAN.export_to_file(fname, overwrite=True)

    @QtCore.Slot()
    def reset_entries(self):
        """
        Reset all ScanSetting entries to their default values.
        """
        SCAN.restore_all_defaults(True)
        for param in SCAN.params.values():
            self.param_widgets[param.refkey].set_value(param.value)

    @QtCore.Slot(int, int)
    def move_dim(self, dim_index, direction):
        """
        Move the selected dimension up in the arrangement of scan dimensions in the
        defined direction.

        Parameters
        ----------
        dim_index : int
            The index of the selected dimension.
        direction : int
            The direction. Use -1 for up and 1 for down.
        """
        _previous_dim_entries = {
            _key: SCAN.get_param_value(f"{_key}_{dim_index + direction}")
            for _key in ["scan_label", "n_points", "delta", "unit", "offset"]
        }
        for _key in ["scan_label", "n_points", "delta", "unit", "offset"]:
            SCAN.set_param_value(
                f"{_key}_{dim_index + direction}",
                SCAN.get_param_value(f"{_key}_{dim_index}")
            )
            SCAN.set_param_value(
                f"{_key}_{dim_index}",
                _previous_dim_entries[f"{_key}"]
            )
            self.update_widget_value(
                f"{_key}_{dim_index + direction}",
                SCAN.get_param_value(f"{_key}_{dim_index + direction}")
            )
            self.update_widget_value(
                f"{_key}_{dim_index}",
                SCAN.get_param_value(f"{_key}_{dim_index}")
            )
