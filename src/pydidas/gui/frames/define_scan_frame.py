# This file is part of pydidas.
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
# along with Pydidas. If not, see <http://www.gnu.org/licenses/>.

"""
Module with the DefineScanFrame which is used to manage and modify the scan
settings like dimensionality, number of points and labels.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2024 - 2026, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"
__all__ = ["DefineScanFrame"]


from functools import partial
from typing import Any

import numpy as np
from qtpy import QtCore, QtGui

from pydidas.contexts import ScanContext, ScanIo
from pydidas.core import Parameter, UserConfigError, constants, utils
from pydidas.core.constants import (
    FONT_METRIC_CONFIG_WIDTH,
    FONT_METRIC_SPACER,
    FONT_METRIC_WIDE_CONFIG_WIDTH,
)
from pydidas.core.utils import doc_qurl_for_rel_address
from pydidas.gui.frames.builders.define_scan_frame_builder import (
    DEFINE_SCAN_FRAME_BUILD_CONFIG,
)
from pydidas.widgets import PydidasFileDialog
from pydidas.widgets.dialogues import ItemInListSelectionWidget
from pydidas.widgets.framework import BaseFrame
from pydidas_qtcore import PydidasQApplication


SCAN = ScanContext()


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
_DERIVED_N_FRAMES_PARAM = Parameter(
    "derived_n_frames", int, 0, name="Derived total number of frames/spectra"
)


class DefineScanFrame(BaseFrame):
    """
    Frame for managing the global scan setup.
    """

    menu_icon = "pydidas::frame_icon_define_scan"
    menu_title = "Define\nscan"
    menu_entry = "Workflow processing/Define scan"

    def __init__(self, **kwargs: Any) -> None:
        BaseFrame.__init__(self, **kwargs)
        self._io_dialog = PydidasFileDialog()
        self._qtapp = PydidasQApplication.instance()
        self.params.update(SCAN.params)
        self.add_param(_DERIVED_N_FRAMES_PARAM)

    def build_frame(self) -> None:
        """
        Populate the frame with widgets.
        """
        utils.apply_qt_properties(
            self.layout(),
            horizontalSpacing=25,
            alignment=constants.ALIGN_TOP_LEFT,
        )
        for _name, _args, _kwargs in DEFINE_SCAN_FRAME_BUILD_CONFIG:
            getattr(self, _name)(*_args, **_kwargs)
        for _name in ["scan_base_directory", "scan_name_pattern"]:
            self.param_widgets[_name].set_unique_ref_name(f"DefineScanFrame__{_name}")
        self.param_composite_widgets["derived_n_frames"].io_widget.setEnabled(False)

    def connect_signals(self) -> None:
        """
        Connect all required signals and slots.
        """
        self._widgets["but_save"].clicked.connect(self.export_to_file)
        self._widgets["but_import_from_pydidas"].clicked.connect(
            self._import_from_pydidas_file
        )
        self._widgets["but_import_bl_metadata"].clicked.connect(
            self._import_from_beamline_file_format
        )
        self._widgets["but_reset"].clicked.connect(self.reset_entries)
        self._widgets["but_more_scan_dim_info"].clicked.connect(self._show_scan_dim_doc)
        self._widgets["but_file_naming_help"].clicked.connect(
            self._show_file_naming_doc
        )
        self._widgets["but_multi_frame_help"].clicked.connect(
            self._show_multi_frame_doc
        )
        self.param_widgets["scan_dim"].sig_value_changed.connect(
            self.update_dim_visibility
        )
        for _index in range(4):
            self._widgets[f"button_up_{_index}"].clicked.connect(
                partial(self.move_dim, _index, -1)
            )
            self._widgets[f"button_down_{_index}"].clicked.connect(
                partial(self.move_dim, _index, 1)
            )
        self.param_widgets["scan_base_directory"].sig_new_value.connect(
            self.set_new_base_directory
        )
        for _widget in self.param_composite_widgets.values():
            _widget.sig_value_changed.connect(self._update_derived_n_frames)

    def finalize_ui(self) -> None:
        """
        Finalize the UI initialization.
        """
        self.update_dim_visibility()
        for param in SCAN.params.values():
            self.param_widgets[param.refkey].set_value(param.value)
        self._update_derived_n_frames()

    @QtCore.Slot()
    def update_dim_visibility(self) -> None:
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
        _dim = int(self.param_widgets["scan_dim"].get_value())
        for i in range(4):
            _toggle = i < _dim
            self._widgets[f"title_{i}"].setVisible(_toggle)
            self._widgets[f"button_up_{i}"].setVisible(0 < i < _dim)
            self._widgets[f"button_down_{i}"].setVisible(i < _dim - 1)
            for _pre in _prefixes:
                self.toggle_param_widget_visibility(_pre.format(n=i), _toggle)
            if i in DIM_LABELS[_dim].keys():
                self._widgets[f"title_{i}"].setText(DIM_LABELS[_dim][i])
        self._widgets["main"].font_metric_width_factor = (
            FONT_METRIC_WIDE_CONFIG_WIDTH
            + 2 * FONT_METRIC_SPACER
            + int(FONT_METRIC_CONFIG_WIDTH * max(1.5, np.ceil(_dim / 2)))
        )
        self._widgets["config_B"].setVisible(_dim in [3, 4])
        self._widgets["config_area"].force_width_from_size_hint()

    @QtCore.Slot()
    def _import_from_pydidas_file(self) -> None:
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
    def _import_from_beamline_file_format(self) -> None:
        """
        Load ScanContext from a file or multiple files in the beamline format.

        This method will open a QFileDialog to select the file to be read.
        """
        _fnames = self._io_dialog.get_existing_filenames(
            caption="Import scan context files",
            formats=ScanIo.get_string_of_beamline_formats(),
            info_string=(
                "Please select all files which belong to the scan. Please note "
                "that only 1d or 2d scans can be imported from beamline file "
                "formats."
            ),
            qsettings_ref="DefineScanFrame__import",
        )
        if len(_fnames) > 0:
            _return = ScanIo.check_multiple_files(_fnames, scan=SCAN)
            if _return[0] == "::no_error::":
                _return = ScanIo.import_from_multiple_files(_fnames, scan=SCAN)
            elif _return[0] == "::multiple_motors::":
                _choice = ItemInListSelectionWidget(
                    _return[1:],
                    title="Select motor",
                    label=(
                        "Multiple motors/devices have changed values in the "
                        "selected beamline files.\n"
                        "Please select motor to use for first scan dimension:"
                    ),
                ).get_item()
                if _choice is None:
                    raise UserConfigError(
                        "No motor selected for scan dimension 0. Aborting import of "
                        "Scan from beamline files."
                    )
                ScanIo.import_from_multiple_files(
                    _fnames, scan=SCAN, scan_dim0_motor=_choice
                )
            else:
                raise UserConfigError(
                    "An unknown error occurred during the import of the scan."
                )
            for param in SCAN.params.values():
                self.param_widgets[param.refkey].set_value(param.value)

    @QtCore.Slot()
    def export_to_file(self) -> None:
        """
        Save ScanContext to a file.

        This method will open a QFileDialog to select a filename where
        the scan context information will be written.
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
    def reset_entries(self) -> None:
        """
        Reset all ScanSetting entries to their default values.
        """
        SCAN.restore_all_defaults(True)
        for param in SCAN.params.values():
            self.param_widgets[param.refkey].set_value(param.value)

    @QtCore.Slot(int, int)
    def move_dim(self, dim_index: int, direction: int) -> None:
        """
        Move the selected dimension's position in the scan.

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
            self.update_param_widget_value(
                f"scan_dim{dim_index + direction}_{_key}",
                SCAN.get_param_value(f"scan_dim{dim_index + direction}_{_key}"),
            )
            self.update_param_widget_value(
                f"scan_dim{dim_index}_{_key}",
                SCAN.get_param_value(f"scan_dim{dim_index}_{_key}"),
            )

    @QtCore.Slot(str)
    def set_new_base_directory(self, basedir: str) -> None:
        """
        Set the new base directory for the scan.

        Parameters
        ----------
        basedir : str
            The new base directory
        """
        self.q_settings_set("dialogues/DefineScanFrame__scan_name_pattern", basedir)

    @QtCore.Slot()
    def _show_scan_dim_doc(self) -> None:
        """Show the documentation about scan dimensions."""
        _qurl = doc_qurl_for_rel_address("manuals/global/scan/dimension_help.html")
        _ = QtGui.QDesktopServices.openUrl(_qurl)

    @QtCore.Slot()
    def _show_multi_frame_doc(self) -> None:
        """Show the documentation window about multi-frame handling in scans."""
        _qurl = doc_qurl_for_rel_address("manuals/global/scan/multi_frame_help.html")
        _ = QtGui.QDesktopServices.openUrl(_qurl)

    @QtCore.Slot()
    def _show_file_naming_doc(self) -> None:
        """Show the documentation about scan file naming."""
        _qurl = doc_qurl_for_rel_address("manuals/global/scan/file_naming_help.html")
        _ = QtGui.QDesktopServices.openUrl(_qurl)

    @QtCore.Slot()
    def _update_derived_n_frames(self) -> None:
        """Update the derived total number of frames/spectra in the scan."""
        self.set_param_and_widget_value("derived_n_frames", SCAN.n_frames_required)
