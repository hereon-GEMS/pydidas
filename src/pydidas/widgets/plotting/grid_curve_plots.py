# This file is part of pydidas.
#
# Copyright 2025, Helmholtz-Zentrum Hereon
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
Module with the GridCurvePlot which allows to plot a number of curves on a grid.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2025, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"
__all__ = ["GridCurvePlot"]


from functools import partial
from itertools import product
from numbers import Integral, Real
from typing import Any

import numpy as np
from qtpy import QtCore

from pydidas.contexts import Scan
from pydidas.core import Dataset, UserConfigError
from pydidas.core.constants import (
    ALIGN_BOTTOM_CENTER,
    POLICY_EXP_EXP,
    QT_REG_EXP_POS_INT_VALIDATOR,
)
from pydidas.core.utils import apply_qt_properties
from pydidas.widgets import WidgetWithParameterCollection, delete_all_items_in_layout


_BUTTON_WIDTH = 25


class GridCurvePlot(WidgetWithParameterCollection):
    """
    A widget to display curve plots in a grid layout.
    """

    init_kwargs = ["n_hor", "n_vert"]

    @staticmethod
    def __check_scaling(scaling: Any) -> None:
        """
        Check if the scaling is valid (i.e. a 2-tuple of float).

        Parameters
        ----------
        scaling : Any
            The scaling to check.

        Raises
        ------
        UserConfigError
            If the scaling is not a tuple of two floats.
        """
        if not isinstance(scaling, tuple) or len(scaling) != 2:
            raise UserConfigError("Scaling must be a tuple of (min, max).")
        if not all(isinstance(_val, Real) for _val in scaling):
            raise UserConfigError("Scaling values must be real numbers (floats).")

    def __init__(self, **kwargs: Any):
        WidgetWithParameterCollection.__init__(self, **kwargs)
        self._config = {
            "n_hor": kwargs.pop("n_hor", 2),
            "n_vert": kwargs.pop("n_vert", 2),
            "max_index": -1,
            "num_dataset_plots": 0,
            "num_plots_in_grid": 0,
            "num_grid_spaces": 0,
            "active_plot_indices": [],
            "active_plot_keys": [],
            "plot_visibility_changed": True,
        }
        self.set_default_params()
        self._datasets = {}
        self._yscaling = {}
        self._xscaling = {}
        self._plot_titles = {}
        self._local_scan = Scan()

        self._current_index = -1
        self.setSizePolicy(*POLICY_EXP_EXP)  # noqa E1120, E1121
        self.create_empty_widget("grid", parent_widget=self, sizePolicy=POLICY_EXP_EXP)
        apply_qt_properties(
            self._widgets["grid"].layout(), horizontalSpacing=30, verticalSpacing=0
        )

        self._create_config_bottom_widgets()
        self.__updated_n_plot_numbers()

    def _create_config_bottom_widgets(self):
        """Create the widgets in the bottom configuration"""
        self.create_empty_widget("config_bottom", parent_widget=self, visible=True)
        self.create_square_button(
            "button_start",
            clicked=partial(self._change_start_index, "::start::"),
            font_metric_height_factor=1,
            icon="mdi::skip-backward",
            gridPos=(0, -1, 1, 1),
            parent_widget="config_bottom",
            toolTip="Go to the start of the scan",
        )
        self.create_button(
            "button_back_page",
            "Go back one page",
            icon="pydidas::page-backward",
            clicked=partial(self._change_start_index, "::page-::"),
            font_metric_width_factor=_BUTTON_WIDTH,
            gridPos=(0, -1, 1, 1),
            parent_widget="config_bottom",
            toolTip="Go back one page (i.e. replace all current plots)",
        )
        self.create_square_button(
            "button_backward",
            clicked=partial(self._change_start_index, -1),
            font_metric_height_factor=1,
            icon="mdi::step-backward",
            gridPos=(0, -1, 1, 1),
            parent_widget="config_bottom",
            toolTop="Go back one scan point",
        )
        self.create_label(
            "label_current",
            "current selection:",
            font_metric_width_factor=17,
            gridPos=(0, -1, 1, 1),
            parent_widget="config_bottom",
        )
        self.create_lineedit(
            "edit_index_low",
            font_metric_width_factor=8,
            gridPos=(0, -1, 1, 1),
            parent_widget="config_bottom",
            validator=QT_REG_EXP_POS_INT_VALIDATOR,
        )
        self.create_label(
            "label_current",
            "-",
            font_metric_width_factor=1,
            gridPos=(0, -1, 1, 1),
            parent_widget="config_bottom",
        )
        self.create_lineedit(
            "edit_index_high",
            font_metric_width_factor=8,
            gridPos=(0, -1, 1, 1),
            parent_widget="config_bottom",
            validator=QT_REG_EXP_POS_INT_VALIDATOR,
        )
        self.create_square_button(
            "button_forward",
            clicked=partial(self._change_start_index, 1),
            font_metric_height_factor=1,
            icon="mdi::step-forward",
            gridPos=(0, -1, 1, 1),
            parent_widget="config_bottom",
            toolTip="Go forward one scan point",
        )
        self.create_button(
            "button_forward_page",
            "Go forward one page",
            clicked=partial(self._change_start_index, "::page+::"),
            icon="pydidas::page-forward",
            font_metric_width_factor=_BUTTON_WIDTH,
            gridPos=(0, -1, 1, 1),
            parent_widget="config_bottom",
            toolTip="Go forward one page (i.e. replace all current plots)",
        )
        self.create_square_button(
            "button_end",
            clicked=partial(self._change_start_index, "::end::"),
            font_metric_height_factor=1,
            icon="mdi::skip-forward",
            gridPos=(0, -1, 1, 1),
            parent_widget="config_bottom",
            toolTip="Go forward to the end of the scan",
        )
        _ncols = self._widgets["config_bottom"].layout().columnCount()
        self.create_spacer(
            None, parent_widget="config_bottom", fixedHeight=10, gridPos=(0, -1, 1, 1)
        )
        apply_qt_properties(
            self._widgets["config_bottom"].layout(), columnStretch=(_ncols, 1)
        )
        self._widgets["edit_index_low"].editingFinished.connect(
            partial(self._manual_index_change, "low")
        )
        self._widgets["edit_index_high"].editingFinished.connect(
            partial(self._manual_index_change, "high")
        )

    @property
    def n_plots(self) -> int:
        """Get the total number of plots in the grid."""
        return self._config["n_hor"] * self._config["n_vert"]

    @property
    def n_plots_hor(self) -> int:
        """Get the total number of plots in the horizontal grid."""
        return self._config["n_hor"]

    @n_plots_hor.setter
    def n_plots_hor(self, n_plots_hor: int) -> None:
        """Set the total number of plots in the horizontal grid."""
        if not isinstance(n_plots_hor, Integral):
            raise UserConfigError("The value of n_plots_hor must be an integer.")
        self._config["n_hor"] = int(n_plots_hor)
        self.__updated_n_plot_numbers()

    @property
    def n_plots_vert(self) -> int:
        """Get the total number of plots in the vertical grid."""
        return self._config["n_vert"]

    @n_plots_vert.setter
    def n_plots_vert(self, n_plots_vert: int) -> None:
        """Set the total number of plots in the vertical grid."""
        if not isinstance(n_plots_vert, Integral):
            raise UserConfigError("The value of n_plots_vert must be an integer.")
        self._config["n_vert"] = int(n_plots_vert)
        self.__updated_n_plot_numbers()

    def set_plot_numbers(self, n_vert: int, n_hor: int) -> None:
        """
        Set the number of plots in the grid.

        Parameters
        ----------
        n_vert : int
            The number of vertical plots.
        n_hor : int
            The number of horizontal plots.
        """
        if not isinstance(n_vert, Integral) or not isinstance(n_hor, Integral):
            raise UserConfigError(
                "The values for n_plots_vert and n_plots_hor must be integers."
            )
        self._config["n_vert"] = int(n_vert)
        self._config["n_hor"] = int(n_hor)
        self.__updated_n_plot_numbers()

    def __updated_n_plot_numbers(self) -> None:
        """Run housekeeping after changing the number of plots."""
        _indices = list(
            product(range(self._config["n_vert"]), range(self._config["n_hor"]))
        )
        self._config["active_plot_indices"] = _indices
        self._config["active_plot_keys"] = [f"plot_{_i}_{_j}" for _i, _j in _indices]
        #
        self._config["plot_visibility_changed"] = True
        self._current_index = min(
            self._config["max_index"] - (self.n_plots - 1), self._current_index
        )
        if self._datasets:
            self._update_navigation_widgets()
            self._update_plot()

    def _update_navigation_widgets(self) -> None:
        """Update the edit indices in the bottom configuration."""
        _max = self._config["max_index"] - (self.n_plots - 1)
        for _key in ["button_forward", "button_forward_page", "button_end"]:
            self._widgets[_key].setEnabled(self._current_index < _max)
        for _key in ["button_backward", "button_back_page", "button_start"]:
            self._widgets[_key].setEnabled(self._current_index > 0)
        with QtCore.QSignalBlocker(self._widgets["edit_index_low"]):
            self._widgets["edit_index_low"].setText(str(self._current_index))
        with QtCore.QSignalBlocker(self._widgets["edit_index_low"]):
            _high_index = self._current_index + self.n_plots - 1
            self._widgets["edit_index_high"].setText(str(_high_index))

    def clear(self):
        """
        Clear the datasets and reset the plot.
        """
        self._datasets = {}
        self._yscaling = {}
        self._xscaling = {}
        self._plot_titles = {}
        self._config["max_index"] = None
        self._update_plot()

    def set_scan(self, scan: Scan):
        """
        Set the scan context for the plot.

        Parameters
        ----------
        scan : Scan
            The Scan instance to set as the context for the plot.
        """
        if not isinstance(scan, Scan):
            raise UserConfigError("Provided scan is not a valid Scan instance.")
        self._local_scan.update_from_scan(scan)
        self._update_plot()

    def set_datasets(self, **datasets: Dataset | None):
        """
        Set the datasets to be plotted in the grid.

        The datasets must be either 2- or 3-dimensional, where the first dimension
        corresponds to the scan points. The datasets must all have the same size.

        Parameters
        ----------
        **datasets : Dataset | None
            The datasets to be plotted.
        """
        if not datasets:
            raise UserConfigError("No datasets provided for plotting.")
        _sizes = set(_data.shape[0] for _data in datasets.values() if _data is not None)
        if len(_sizes) > 1:
            raise UserConfigError(
                "All datasets must have the same size of the 1st dimension."
            )
        _ndims = set(_data.ndim for _data in datasets.values() if _data is not None)
        if not _ndims.issubset({2, 3}):
            raise UserConfigError(
                "All datasets must be 2- or 3-dimensional (i.e. have 2 or 3 axes)."
            )
        self._config["max_index"] = min(_sizes) - 1 if _sizes else 0
        self._config["plot_visibility_changed"] = True
        self._datasets = datasets
        for _key in self._datasets:
            if _key not in self._yscaling:
                self._yscaling[_key] = (None, None)
            if _key not in self._xscaling:
                self._xscaling[_key] = (None, None)
            if _key not in self._plot_titles:
                self._plot_titles[_key] = _key
        if self._current_index < 0:
            self._change_start_index("::start::")
        self._update_navigation_widgets()
        self._update_plot()

    def set_titles(self, **titles: str) -> None:
        """
        Set the titles for the plots in the grid.

        Parameters
        ----------
        titles : str
            The titles for the plots, where the keys are the dataset keys,
        """
        for _key, _title in titles.items():
            if _key not in self._datasets:
                raise UserConfigError(f"Dataset `{_key}` not found.")
            self._plot_titles[_key] = _title

    def set_xscaling(
        self, dataset_key: str, scaling: tuple[float, float], update_plot: bool = True
    ):
        """
        Set the x-scaling for a specific dataset.

        Parameters
        ----------
        dataset_key : str
            The key of the dataset to set the scaling for.
        scaling : tuple[float, float]
            The x-scaling as a tuple (min, max).
        update_plot : bool, optional
            Flag whether to update the plot after setting the scaling. Default is True.
        """
        if dataset_key not in self._datasets:
            raise UserConfigError(f"Dataset `{dataset_key}` not found.")
        self.__check_scaling(scaling)
        self._xscaling[dataset_key] = scaling
        if update_plot:
            self._update_plot()

    def set_yscaling(
        self, dataset_key, scaling: tuple[float, float], update_plot: bool = True
    ):
        """
        Set the y-scaling for a specific dataset.

        Parameters
        ----------
        dataset_key : str
            The key of the dataset to set the scaling for.
        scaling : tuple[float, float]
            The y-scaling as a tuple (min, max).
        update_plot : bool, optional
            Flag whether to update the plot after setting the scaling. Default is True.
        """
        if dataset_key not in self._datasets:
            raise UserConfigError(f"Dataset `{dataset_key}` not found.")
        self.__check_scaling(scaling)
        self._yscaling[dataset_key] = scaling
        if update_plot:
            self._update_plot()

    def set_y_autoscaling(self, dataset_key: str, update_plot: bool = True):
        """
        Set the y-axis scaling to use autoscaling.

        Parameters
        ----------
        dataset_key : str
            The key of the dataset to set autoscaling for.
        update_plot : bool, optional
            Flag whether to update the plot after setting the scaling. Default is True.
        """
        if dataset_key not in self._datasets:
            raise UserConfigError(f"Dataset `{dataset_key}` not found.")
        self._yscaling[dataset_key] = (None, None)
        if update_plot:
            self._update_plot()

    def set_x_autoscaling(self, dataset_key: str, update_plot: bool = True):
        """
        Set the x-axis scaling to use autoscaling.

        Parameters
        ----------
        dataset_key : str
            The key of the dataset to set autoscaling for.
        update_plot : bool, optional
            Flag whether to update the plot after setting the scaling. Default is True.
        """
        if dataset_key not in self._datasets:
            raise UserConfigError(f"Dataset `{dataset_key}` not found.")
        self._xscaling[dataset_key] = (None, None)
        if update_plot:
            self._update_plot()

    @QtCore.Slot()
    def _change_start_index(self, value: int | str) -> None:
        """
        Change the start index of the scan point.

        A value can be given as an integer offset or as a string identifier.

        Possible identifiers are:

            '::start::' : Go to the start of the scan
            '::end::' : Go to the end of the scan
            '::page+::' : Go forward one page
            '::page-::' : Go back one page

        Parameters
        ----------
        value : int | str
            The new start index or a string identifier for the action to perform.
            If an integer is given, it will be added to the current index.
        """
        _start_index = self._current_index
        # The n_plots - 1 is done because the starting index is inclusive
        _max = self._config["max_index"] - (self.n_plots - 1)
        match value:
            case "::start::":
                self._current_index = 0
            case "::end::":
                self._current_index = _max
            case "::page+::":
                self._current_index = min(self._current_index + self.n_plots, _max)
            case "::page-::":
                self._current_index = max(self._current_index - self.n_plots, 0)
            case _:
                if isinstance(value, Integral):
                    self._current_index = min(max(0, self._current_index + value), _max)
                else:
                    raise UserConfigError(
                        "The parameter for the start index could not be interpreted."
                    )
        if self._current_index != _start_index:
            self._update_navigation_widgets()
            self._update_plot()

    def _update_plot(self):
        """
        Update the plot with the current datasets and parameters.
        This method should be implemented to create the actual plot.
        """
        _should_be_visible = not all(_data is None for _data in self._datasets.values())
        self._widgets["grid"].setVisible(_should_be_visible)
        self._widgets["config_bottom"].setVisible(_should_be_visible)
        if not _should_be_visible:
            return
        if self.n_plots != self._config["num_grid_spaces"]:
            self.__update_grid_for_plots()
        if (
            len(self._datasets) != self._config["num_dataset_plots"]
            or self.n_plots != self._config["num_plots_in_grid"]
        ):
            self.__create_plots_in_grid_if_needed()
        self.__update_plot_visibility()
        self.__plot_datasets()
        self.__update_grid_titles()

    def __update_grid_for_plots(self):
        """
        Update the grid of the plots based on the currently selected numbers.
        """
        _plot_layout = self._widgets["grid"].layout()
        for _key in [_key for _key in self._widgets if _key.startswith("plot_")]:
            _comparator = _key.rstrip("_title") if _key.endswith("_title") else _key
            self._widgets[_key].setVisible(
                _comparator in self._config["active_plot_keys"]
            )
        for _index, _key in enumerate(self._config["active_plot_keys"]):
            if _key in self._widgets:
                continue
            _y, _x = self._config["active_plot_indices"][_index]
            self.create_label(
                f"{_key}_title",
                f"Plot {_x + 1}, {_y + 1}",
                font_metric_height_factor=3 if _y > 0 else 1,
                alignment=ALIGN_BOTTOM_CENTER,
                parent_widget=self._widgets["grid"],
                gridPos=(2 * _y, _x, 1, 1),
            )
            self.create_empty_widget(
                _key,
                parent_widget=self._widgets["grid"],
                gridPos=(2 * _y + 1, _x, 1, 1),
            )
        self._config["num_grid_spaces"] = self.n_plots

    def __create_plots_in_grid_if_needed(self):
        """Create the required plot widgets in the grid if they do not exist yet."""
        import pyqtgraph as pg

        pg.setConfigOption("background", (255, 255, 255, 0))

        _n_data = len(self._datasets)
        _plot_keys = [
            _key
            for _key in self._widgets
            if _key.startswith("plot_") and not _key.endswith("_title")
        ]
        for _plot_key in self._config["active_plot_keys"]:
            _widget = self._widgets[_plot_key]
            if _widget.layout().count() != _n_data:
                for _sub_key in [
                    _key for _key in self._widgets if _key.startswith(f"sub{_plot_key}")
                ]:
                    _sub_widget = self._widgets.pop(_sub_key)
                    _sub_widget.setParent(None)
                    _sub_widget.deleteLater()
                delete_all_items_in_layout(_widget.layout())
                for _index in range(_n_data):
                    self.add_any_widget(
                        f"sub{_plot_key}_{_index}",
                        pg.PlotWidget(parent=_widget),
                        gridPos=(0, -1, 1, 1),
                        parent_widget=_plot_key,
                    )
        self._config["num_dataset_plots"] = _n_data
        self._config["num_plots_in_grid"] = len(_plot_keys)

    def __update_plot_visibility(self):
        """Update the visibility of the plot widgets based on the datasets."""
        if self._config["plot_visibility_changed"]:
            for _idata, _data in enumerate(self._datasets.values()):
                for _key in self._config["active_plot_keys"]:
                    self._widgets[f"sub{_key}_{_idata}"].setVisible(_data is not None)
            self._config["plot_visibility_changed"] = False

    def __plot_datasets(self):
        """Plot the datasets in the grid layout."""
        for _idata, (_data_key, _data) in enumerate(self._datasets.items()):
            if _data is None:
                continue
            _xrange = _data.axis_ranges[_data.ndim - 1]
            _xmin, _xmax, _ymin, _ymax = self.__get_limits_for_data(_data_key)
            for _i_plot in range(self.n_plots):
                _key = f"sub{self._config['active_plot_keys'][_i_plot]}_{_idata}"
                self.__prepare_plot_for_new_data(
                    _data_key, _key, (_xmin, _xmax), (_ymin, _ymax)
                )
                _plot_widget = self._widgets[_key]
                _local_data = _data[self._current_index + _i_plot]
                if _local_data.ndim == 1:
                    _plot_widget.plot(_xrange, _local_data, pen="b")
                    continue
                _nitems = _local_data.shape[0]
                for _n in range(_nitems):
                    if _n < _nitems - 1:
                        _plot_widget.scatterPlot(
                            _xrange, _local_data[_n], pen=None, symbol="o"
                        )
                    else:
                        _plot_widget.plot(_xrange, _local_data[_n], pen="b")

    def __get_limits_for_data(self, data_key: str) -> tuple[float, float, float, float]:
        """
        Get the limits for the plot from the data.

        Parameters
        ----------
        data_key : str
            The key to identify the dataset.

        Returns
        -------
        tuple[float, float, float, float]
            The x-min, x-max, y-min, and y-max limits.
        """
        # Get the y and x scaling limits for the current dataset:
        _data = self._datasets[data_key]
        _xrange = _data.axis_ranges[_data.ndim - 1]
        _ymin, _ymax = self._yscaling[data_key]
        if _ymin is None or _ymax is None:
            _ymin, _ymax = np.nanmin(_data), np.nanmax(_data)
            _ymin -= 0.05 * abs(_ymax - _ymin)
            _ymax += 0.05 * abs(_ymax - _ymin)
        _xmin, _xmax = self._xscaling[data_key]
        if _xmin is None or _xmax is None:
            _xmin, _xmax = np.nanmin(_xrange), np.nanmax(_xrange)
            _xmin -= 0.05 * abs(_xmax - _xmin)
            _xmax += 0.05 * abs(_xmax - _xmin)
        return _xmin, _xmax, _ymin, _ymax

    def __prepare_plot_for_new_data(
        self,
        data_key: str,
        widget_key: str,
        xrange: tuple[float, float],
        yrange: tuple[float, float],
    ) -> None:
        """
        Prepare the plot for a new dataset by clearing it and setting the title.

        Parameters
        ----------
        data_key : str
            The key of the dataset to prepare the plot for.
        widget_key : str
            The key of the plot widget to prepare.
        xrange : tuple[float, float]
            The x-range to set for the plot.
        yrange : tuple[float, float]
            The y-range to set for the plot.
        """

        _title = self._plot_titles.get(data_key, data_key)
        _plot_widget = self._widgets[widget_key]
        _plot_widget.clear()
        _plot_widget.setMouseEnabled(x=False, y=False)
        _plot_widget.setRange(xRange=xrange, yRange=yrange)
        _plot_widget.setTitle(_title)

    def __update_grid_titles(self) -> None:
        """Update the titles of the grid layout items."""
        for _iplot in range(self.n_plots):
            _key = self._config["active_plot_keys"][_iplot] + "_title"
            _scan_index = _iplot + self._current_index
            _indices = self._local_scan.get_indices_from_ordinal(_scan_index)
            _indices_str = " / ".join(str(_i) for _i in _indices)
            _label = self._widgets[_key]
            _label.setText(f"Scan point #{_scan_index} (indices {_indices_str})")

    @QtCore.Slot()
    def _manual_index_change(self, source: str) -> None:
        """
        Change the start index based on manual input.

        Parameters
        ----------
        source : str
            The source of the manual input, either 'low' or 'high'.
        """
        _start_index = self._current_index
        _low = int(self._widgets[f"edit_index_{source}"].text())
        if source == "high":
            _low -= self.n_plots - 1
        self._current_index = max(
            0, min(_low, self._config["max_index"] - (self.n_plots - 1))
        )
        self._update_navigation_widgets()
        if self._current_index != _start_index:
            self._update_plot()
