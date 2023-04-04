# This file is part of pydidas.
#
# Copyright 2021-, Helmholtz-Zentrum Hereon
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
Module with the ShowInformationForResult class which is a widget to display detailed
information about a datapoint from a pydidas result.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2021-, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Development"
__all__ = ["ShowInformationForResult"]


from pathlib import Path

from qtpy import QtCore, QtWidgets

from ...core import UserConfigError
from ...core.utils import (
    ShowBusyMouse,
    apply_qt_properties,
    get_fixed_length_str,
    get_pydidas_icon_w_bg,
)
from ..factory import CreateWidgetsMixIn
from ..silx_plot import create_silx_plot_stack, get_2d_silx_plot_ax_settings
from .read_only_text_widget import ReadOnlyTextWidget


class ShowInformationForResult(QtWidgets.QWidget, CreateWidgetsMixIn):
    """
    Window to display detailed plugin results in combination with all Plugin
    Parameters to allow running the Plugin with different values.
    """

    show_frame = False
    sig_closed = QtCore.Signal()
    sig_this_frame_activated = QtCore.Signal()

    def __init__(self, parent=None):
        QtWidgets.QWidget.__init__(self, parent)
        CreateWidgetsMixIn.__init__(self)
        _layout = QtWidgets.QGridLayout()
        _layout.setAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignTop)
        self.setLayout(_layout)

        self.setWindowIcon(get_pydidas_icon_w_bg())
        self.setWindowTitle("Information for data point")
        self._frame = None
        self._loader_plugin = None
        self.create_label(
            "label_title",
            "Information for selected data point:",
            fontsize=14,
            bold=True,
        )
        self.create_any_widget(
            "info_field", ReadOnlyTextWidget, fixedWidth=600, fixedHeight=250
        )
        self.create_button("but_show_input", "Show input frame")
        create_silx_plot_stack(self)
        apply_qt_properties(
            self._widgets["plot_stack"], visible=False, minimumHeight=600
        )
        self._widgets["but_show_input"].clicked.connect(self.show_input_image)

    def display_information(
        self, data, selection_config, result_metadata, loader_plugin
    ):
        """
        Display the information about the selected datapoint.

        Parameters
        ----------
        data : tuple
            A 2-tuple with the data position selected in the image.
        selection_config : dict
            Dictionary with information about the data selection.
        result_metadata : dict
            The metadata of the results.
        loader_plugin : pydidas.plugins.BaseInputPlugin
            The input plugin associated with the results. Required to display the
            input image.
        param_values : dict
            The parameter values of the result selections.
        """
        self._loader_plugin = loader_plugin.copy()
        self._loader_plugin._SCAN = loader_plugin._SCAN.copy()
        self._loader_plugin.update_filename_string()
        _scan = self._loader_plugin._SCAN
        _ax_ranges = result_metadata["axis_ranges"]
        _dim_selections = []
        for _dim in range(len(result_metadata["shape"])):
            if _dim == selection_config["active_dims"][0]:
                _index = (abs(_ax_ranges[_dim] - data[0])).argmin()
            elif _dim == selection_config["active_dims"][1]:
                _index = (abs(_ax_ranges[_dim] - data[1])).argmin()
            else:
                _val = float(selection_config[f"plot_slice_{_dim}"])
                _index = (
                    abs(_ax_ranges[_dim] - _val).argmin()
                    if selection_config["selection_by_data_values"]
                    else int(_val)
                )
            _dim_selections.append(_index)

        _info_str = "Selected data position:\n" + "\n".join(
            get_fixed_length_str(
                f"{result_metadata['axis_labels'][_dim]}:", 18, final_space=False
            )
            + get_fixed_length_str(
                _ax_ranges[_dim][_index], 12, formatter="{:.5f}", fill_back=False
            )
            + f" {result_metadata['axis_units'][_dim]}"
            for _dim, _index in enumerate(_dim_selections)
        )
        self._frame = (
            _dim_selections[0]
            if selection_config["use_timeline"]
            else _scan.get_frame_from_indices(_dim_selections[: _scan.ndim])
        )
        _scan_indices = _scan.get_frame_position_in_scan(self._frame)

        _info_str += (
            "\n\nPosition in scan:"
            + "\n"
            + get_fixed_length_str("Frame index:", 20, final_space=False)
            + get_fixed_length_str(self._frame, 6, fill_back=False, formatter="{:d}")
            + "\n"
            + "\n".join(
                get_fixed_length_str(f"Scan dim {_dim} index:", 20, final_space=False)
                + get_fixed_length_str(_index, 6, fill_back=False, formatter="{:d}")
                for _dim, _index in enumerate(_scan_indices)
            )
            + "\n\nFilename:\n... "
            + loader_plugin.get_filename(self._frame)
        )
        if "_counted_images_per_file" in loader_plugin.params:
            _index = self._frame % loader_plugin.get_param_value(
                "_counted_images_per_file"
            )
            _info_str += "\n" + get_fixed_length_str("Frame in file:", 18) + str(_index)
        self._widgets["info_field"].setText(_info_str)
        self._widgets["but_show_input"].setEnabled(True)
        self._widgets["plot_stack"].setVisible(False)
        self.show()

    @QtCore.Slot()
    def show_input_image(self):
        """
        Run the plugin with the current Parameters.
        """
        if not Path(self._loader_plugin.get_filename(self._frame)).is_file():
            self._widgets["but_show_input"].setEnabled(False)
            raise UserConfigError(
                "Cannot display the input image because the filename does not point to "
                "a valid file on this system."
            )
        self._widgets["plot_stack"].setVisible(True)
        with ShowBusyMouse():
            self._loader_plugin.pre_execute()
            _input, _kwargs = self._loader_plugin.execute(self._frame)
            self._widgets["plot_stack"].setCurrentIndex(_input.ndim - 1)
            if _input.ndim == 1:
                self._plot1d(_input)
            elif _input.ndim == 2:
                self._plot2d(_input)

    def _plot1d(self, data):
        """
        Plot a 1D-dataset in the 1D plot widget.

        Parameters
        ----------
        data : pydidas.core.Dataset
            The data to be plotted.
        """
        _axlabel = data.axis_labels[0] + (
            " / " + data.axis_units[0] if len(data.axis_units[0]) > 0 else ""
        )
        self._widgets["plot1d"].addCurve(
            data.axis_ranges[0],
            data.array,
            replace=True,
            linewidth=1.5,
            xlabel=_axlabel,
            ylabel=f"{self._loader_plugin.plugin_name} results",
        )

    def _plot2d(self, data):
        """
        Plot a 2D-dataset in the 2D plot widget.

        Parameters
        ----------
        data : pydidas.core.Dataset
            The data to be plotted.
        """
        _ax_labels = [
            data.axis_labels[i]
            + (" / " + data.axis_units[i] if len(data.axis_units[0]) > 0 else "")
            for i in [0, 1]
        ]
        _originx, _scalex = get_2d_silx_plot_ax_settings(data.axis_ranges[1])
        _originy, _scaley = get_2d_silx_plot_ax_settings(data.axis_ranges[0])
        self._widgets["plot2d"].addImage(
            data,
            replace=True,
            copy=False,
            origin=(_originx, _originy),
            scale=(_scalex, _scaley),
        )
        self._widgets["plot2d"].setGraphYLabel(_ax_labels[0])
        self._widgets["plot2d"].setGraphXLabel(_ax_labels[1])
