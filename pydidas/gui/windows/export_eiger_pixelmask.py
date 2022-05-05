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
Module with the ExportEigerPixelmaskWindow class which is a stand-alone frame
to store the pixel mask.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2021-2022, Malte Storm, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0"
__maintainer__ = "Malte Storm"
__status__ = "Development"
__all__ = ["ExportEigerPixelmaskWindow"]

import os
from pathlib import Path

from qtpy import QtCore

from ...core import Parameter, ParameterCollection
from ...core.constants import DEFAULT_TWO_LINE_PARAM_CONFIG
from ...core.utils.dectris_utils import store_eiger_pixel_mask_from_master_file
from ...widgets import BaseFrame
from ...widgets.dialogues import critical_warning


class ExportEigerPixelmaskWindow(BaseFrame):
    """
    Window with a simple dialogue to export the Pixelmask from an Eiger
    "master" file.
    """

    default_params = ParameterCollection(
        Parameter(
            "master_filename",
            Path,
            Path(),
            name="Master-file name",
            tooltip="The filename (and path) for the Eiger master file.",
        ),
        Parameter(
            "output_filename",
            Path,
            Path(),
            name="Export filename",
            tooltip="The filename (and path) for the new pixel mask file.",
        ),
    )

    def __init__(self, parent=None):
        super().__init__(parent)
        self.set_default_params()
        self.build_frame()
        self.connect_signals()

    def build_frame(self):
        """
        Build the frame and create all widgets.
        """
        self.create_label(
            "label_title",
            "Export Eiger pixelmask",
            fontsize=14,
            bold=True,
            gridPos=(0, 0, 1, 1),
        )

        self.create_param_widget(
            self.get_param("master_filename"), **DEFAULT_TWO_LINE_PARAM_CONFIG
        )

        self.create_param_widget(
            self.get_param("output_filename"), **DEFAULT_TWO_LINE_PARAM_CONFIG
        )
        self.param_widgets[
            "output_filename"
        ]._file_selection = "NPY files (*.npy *.npz)"

        self.create_button("but_exec", "Export pixelmask")

    def connect_signals(self):
        """
        Build the frame and create all widgets.
        """
        self._widgets["but_exec"].clicked.connect(self._export)

    @QtCore.Slot()
    def _export(self):
        """
        Export the pixelmask.
        """
        _master_fname = self.get_param_value("master_filename", str)
        _export_fname = self.get_param_value("output_filename", str)
        _out_dir = os.path.dirname(_export_fname)
        if not os.path.exists(_master_fname):
            critical_warning(
                "Input file not found",
                (f'The specified input file "{_master_fname}" ' "could not be found."),
            )
            return
        if not os.path.exists(_out_dir):
            critical_warning(
                "Output directory not found",
                (f'The specified output directory "{_out_dir}" ' "could not be found."),
            )
            return
        store_eiger_pixel_mask_from_master_file(_master_fname, _export_fname)
        self.close()
