# This file is part of pydidas.
#
# Copyright 2026, Helmholtz-Zentrum Hereon
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
Module with the SelectDataFrameDialog class for selecting a single frame from a file.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2026, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"
__all__ = ["SelectDataFrameDialog"]


from functools import partial
from pathlib import Path
from typing import Any

from qtpy import QtCore, QtWidgets

from pydidas.core import Dataset, FileReadError
from pydidas.core.constants import FONT_METRIC_CONFIG_WIDTH
from pydidas.core.utils import apply_qt_properties
from pydidas.data_io import import_data
from pydidas.resources.pydidas_icons import pydidas_icon
from pydidas.widgets.factory import CreateWidgetsMixIn


class SelectDataFrameDialog(QtWidgets.QDialog, CreateWidgetsMixIn):
    """
    A dialog for selecting and previewing a data frame from a file.

    The dialog combines a selection widget on the left (for HDF5 and
    binary file format options) and a 2D plot on the right for previewing
    the selected frame.

    After the dialog is accepted the loaded frame is accessible via the
    `selected_frame` property. If the dialog is aborted the property
    returns None.

    Parameters
    ----------
    **kwargs : Any
        Supported keyword arguments are:

        parent : QWidget or None, optional
            The parent widget. The default is None.
        filename : str or Path or None, optional
            The initial file name to be selected. If given, the dialog
            will pre-select the file and hide the file selection widget.
            The default is None.
    """

    def __init__(self, **kwargs: Any) -> None:
        QtWidgets.QDialog.__init__(self, kwargs.get("parent", None))
        CreateWidgetsMixIn.__init__(self)
        self._selected_frame: Dataset | None = None
        self.setWindowTitle("Select data frame")
        self.setWindowIcon(pydidas_icon())
        self.setLayout(QtWidgets.QGridLayout())
        self._create_widgets()
        self._connect_signals()
        _fname = kwargs.get("filename", None)
        if _fname is not None:
            self._widgets["selector"].set_param_value("filename", _fname)
            self._widgets["selector"].toggle_param_widget_visibility("filename", False)
            self._widgets["selector"].process_new_filename()

    # ========================================================================
    # Private initialization and setup methods
    # ========================================================================

    def _create_widgets(self) -> None:
        """Create and arrange all child widgets."""
        # need to import here to keep clean import order
        from pydidas.widgets.selection import SelectDataFrameWidget
        from pydidas.widgets.silx_plot.pydidas_plot2d import PydidasPlot2D

        self.create_empty_widget(
            "left_container", font_metric_width_factor=FONT_METRIC_CONFIG_WIDTH
        )
        self.create_label(
            "title",
            "Select data frame:",
            parent_widget="left_container",
            bold=True,
            underline=True,
            fontsize_offset=1,
        )
        self.create_any_widget(
            "selector",
            SelectDataFrameWidget,
            parent_widget="left_container",
            show_binary_checkbox=False,
        )
        self.create_any_widget("plot", PydidasPlot2D, gridPos=(0, 1, 1, 1))
        apply_qt_properties(self.layout(), columnStretch=(1, 10))
        self.create_empty_widget("bottom_container", gridPos=(1, 0, 1, 2))
        self.create_button(
            "but_confirm",
            "Confirm",
            gridPos=(0, 0, 1, 1),
            enabled=False,
            icon="qt-std::SP_DialogApplyButton",
            parent_widget="bottom_container",
        )
        self.create_button(
            "but_abort",
            "Abort",
            gridPos=(0, 1, 1, 1),
            icon="qt-std::SP_DialogCancelButton",
            parent_widget="bottom_container",
        )

    def _connect_signals(self) -> None:
        """Connect widget signals to the relevant slots."""
        self._widgets["selector"].sig_new_selection.connect(self._load_and_display)
        self._widgets["selector"].sig_file_valid.connect(self._process_file_validity)
        self._widgets["but_confirm"].clicked.connect(self._confirm)
        self._widgets["but_abort"].clicked.connect(self.reject)
        self.rejected.connect(partial(self._process_file_validity, False))

    # ========================================================================
    # Public methods and attributes
    # ========================================================================

    @property
    def selected_frame(self) -> Dataset | None:
        """
        The loaded data frame after the dialog was accepted.

        Returns
        -------
        Dataset or None
            The selected and loaded 2-D data frame, or None if the dialog
            was aborted or no valid file was confirmed.
        """
        return self._selected_frame

    @staticmethod
    def get_frame(
        parent: QtWidgets.QWidget | None = None,
        filename: str | Path | None = None,
    ) -> Dataset | None:
        """
        Open the dialog and return the selected frame.

        This convenience class method opens a modal
        :class:`SelectDataFrameDialog`, waits for the user to confirm or
        abort, and returns the result.

        Parameters
        ----------
        parent : QWidget or None, optional
            The parent widget. The default is None.
        filename : str or Path or None, optional
            The initial file name to be selected. If given, the dialog will
            pre-select the file and hide the file selection widget. The default
            is None.

        Returns
        -------
        Dataset or None
            The loaded frame, or None if the dialog was aborted.
        """
        _dialog = SelectDataFrameDialog(
            parent=parent,
            filename=filename,
        )
        _dialog.resize(1200, 700)
        if _dialog.exec_() == QtWidgets.QDialog.Accepted:
            return _dialog.selected_frame
        return None

    # ========================================================================
    # Private methods and slots
    # ========================================================================

    @QtCore.Slot(str, dict)
    def _load_and_display(self, fname: str, config: dict[str, Any]) -> None:
        """
        Load the selected frame and display it in the plot.

        Parameters
        ----------
        fname : str
            The file path of the selected file.
        config : dict[str, Any]
            Additional import options (e.g. HDF5 dataset key, indices).
        """
        try:
            _data = import_data(fname, **config)
            self._selected_frame = _data
            self._widgets["plot"].plot_pydidas_dataset(_data)
            self._process_file_validity(True)
        except FileReadError:
            self._process_file_validity(False)
            raise

    @QtCore.Slot()
    def _confirm(self) -> None:
        """Load the current selection, store the frame, and accept the dialog."""
        self.accept()

    @QtCore.Slot(bool)
    def _process_file_validity(self, is_valid: bool) -> None:
        """
        Enable or disable the confirm button based on file validity.

        Parameters
        ----------
        is_valid : bool
            Flag whether the selected file is valid.
        """
        self._widgets["but_confirm"].setEnabled(is_valid)
        if not is_valid:
            self._widgets["plot"].clear()
            self._selected_frame = None
