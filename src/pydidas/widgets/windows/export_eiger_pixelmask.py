# This file is part of pydidas.
#
# Copyright 2023 - 2025, Helmholtz-Zentrum Hereon
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
Module with the ExportEigerPixelmaskWindow class which is a stand-alone frame
to store the pixel mask.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2023 - 2025, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"
__all__ = ["ExportEigerPixelmaskWindow"]


import os
from pathlib import Path

from qtpy import QtCore, QtWidgets

from pydidas.core import Parameter, ParameterCollection
from pydidas.core.constants import FONT_METRIC_PARAM_EDIT_WIDTH
from pydidas.core.utils.dectris_utils import store_eiger_pixel_mask_from_master_file
from pydidas.data_io import IoManager
from pydidas.widgets.dialogues import critical_warning
from pydidas.widgets.framework import PydidasWindow


class ExportEigerPixelmaskWindow(PydidasWindow):
    """
    Window with a simple dialogue to export the Pixelmask from an Eiger
    "master" file.
    """

    show_frame = False
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

    def __init__(self, **kwargs: dict):
        PydidasWindow.__init__(self, title="Export Eiger pixelmask", **kwargs)

    def build_frame(self):
        """
        Build the frame and create all widgets.
        """
        self.create_empty_widget(
            "config_canvas",
            font_metric_width_factor=FONT_METRIC_PARAM_EDIT_WIDTH,
        )

        self.create_label(
            "label_title",
            "Export Eiger pixelmask",
            fontsize_offset=4,
            bold=True,
            parent_widget="config_canvas",
        )

        self.create_param_widget(
            self.get_param("master_filename"),
            linebreak=True,
            parent_widget="config_canvas",
        )

        self.create_param_widget(
            self.get_param("output_filename"),
            linebreak=True,
            parent_widget="config_canvas",
        )
        _supported_formats = IoManager.get_string_of_formats("export")
        self.param_widgets["output_filename"]._file_selection = _supported_formats

        self.create_button(
            "but_exec", "Export pixelmask", parent_widget="config_canvas"
        )
        self.process_new_font_metrics()

    def connect_signals(self):
        """
        Build the frame and create all widgets.
        """
        self._widgets["but_exec"].clicked.connect(self._export)
        QtWidgets.QApplication.instance().sig_font_metrics_changed.connect(
            self.process_new_font_metrics
        )

    @QtCore.Slot()
    def process_new_font_metrics(self):
        """
        Process the user input of the new font size.
        """
        self.setFixedWidth(self._widgets["config_canvas"].sizeHint().width() + 20)
        self.adjustSize()

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
                (f'The specified input file "{_master_fname}" could not be found.'),
            )
            return
        if not os.path.exists(_out_dir):
            critical_warning(
                "Output directory not found",
                f"The specified output directory '{_out_dir}' could not be found.",
            )
            return
        store_eiger_pixel_mask_from_master_file(_master_fname, _export_fname)
        self.close()
