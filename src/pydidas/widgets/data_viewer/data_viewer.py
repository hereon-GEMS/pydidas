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
Module with the DataViewer which allows to slice a Dataset by its metadata.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2025, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"
__all__ = ["DataViewer"]


from functools import partial

import h5py
import numpy as np
from qtpy import QtCore, QtWidgets
from silx.gui.hdf5 import H5Node

from pydidas.core import Dataset, UserConfigError
from pydidas.widgets.data_viewer import AxesSelector
from pydidas.widgets.data_viewer.data_axis_selector import GENERIC_AXIS_SELECTOR_CHOICES
from pydidas.widgets.data_viewer.data_viewer_utils import (
    DATA_VIEW_CONFIG,
    DataViewConfig,
)
from pydidas.widgets.widget_with_parameter_collection import (
    WidgetWithParameterCollection,
)


_DATASET_TOO_LARGE_ERROR = (
    "The dataset is too large to display. Please check the dataset or "
    "increase the data buffer size in the global settings."
)


class DataViewer(WidgetWithParameterCollection):
    """
    The DataViewer allows to display data in multiple display modes.
    """

    init_kwargs = [
        "multiline_layout",
        "plot2d_diffraction_exp",
        "plot2d_use_data_info_action",
    ]
    sig_plot2d_get_more_info_for_data = QtCore.Signal(float, float)

    def __init__(self, parent: QtWidgets.QWidget | None = None, **kwargs: dict):
        WidgetWithParameterCollection.__init__(self, parent=parent, **kwargs)

        self._data = None
        self._h5node = None
        self._active_view = None
        self._button_group = QtWidgets.QButtonGroup()
        self._view_config = DATA_VIEW_CONFIG["view-table"]
        self._config["multiline_layout"] = kwargs.get("multiline_layout", False)
        self._config["plot_title"] = None
        self._plot2d_config = {
            "diffraction_exp": kwargs.get("plot2d_diffraction_exp", None),
            "use_data_info_action": kwargs.get("plot2d_use_data_info_action", False),
        }
        self._create_widgets()

    def _create_widgets(self):
        """Create all required widgets"""
        self.create_empty_widget(
            "view_container", gridPos=(0, 0, 1, 1), minimumHeight=600
        )
        self.add_any_widget(
            "view_stack",
            QtWidgets.QStackedWidget(),
            gridPos=(0, 0, 1, 1),
            minimumHeight=300,
            parent_widget="view_container",
        )
        self.add_any_widget(
            "axes_selector",
            AxesSelector(multiline_layout=self._config["multiline_layout"]),
            gridPos=(1, 0, 1, 1),
            parent_widget="view_container",
            visible=False,
        )
        self._widgets["axes_selector"].sig_new_slicing.connect(self._update_view)
        self.create_empty_widget(
            "container_for_buttons", gridPos=(-1, 0, 1, 1), visible=False
        )
        for _ref, _view in DATA_VIEW_CONFIG.items():
            self.create_button(
                f"button_{_ref}",
                _view.title,
                checkable=True,
                gridPos=(0, -1, 1, 1),
                icon=f"pydidas::{_ref}.svg",
                parent_widget="container_for_buttons",
                clicked=partial(self._select_view, _ref),
            )
            self._button_group.addButton(self._widgets[f"button_{_ref}"], _view.id)
        self.layout().setColumnStretch(0, 1)
        self.layout().setRowStretch(0, 1)

    @property
    def active_dims(self) -> tuple[int, ...]:
        """
        Get the active dimensions.

        Returns
        -------
        tuple[int, ...]
            The active dimensions.
        """
        _active_dims = tuple(
            _dim
            for _dim, _selection in enumerate(
                self._widgets["axes_selector"].current_display_selection
            )
            if _selection not in GENERIC_AXIS_SELECTOR_CHOICES
        )
        if self._widgets["axes_selector"].transpose_required:
            _active_dims = tuple(reversed(_active_dims))
        return _active_dims

    @property
    def current_slice(self) -> tuple[slice]:
        """
        Get the current slices.

        Returns
        -------
        tuple[slice]
            The current slice.
        """
        return self._widgets["axes_selector"].current_slice

    @property
    def current_selected_indices(self) -> list[int]:
        """
        Get the current selected indices.

        Returns
        -------
        list[int]
            The current selected indices.
        """
        _active_dims = self.active_dims
        return [
            (_dim_slice.start if _dim not in _active_dims else None)
            for _dim, _dim_slice in enumerate(self.current_slice)
        ]

    @property
    def data_is_set(self) -> bool:
        """
        Return a flag whether the data viewer currently has data associated with it.

        Returns
        -------
        bool :
            Flag whether data has been set.
        """
        return self._data is not None

    @QtCore.Slot(str)
    def _select_view(self, view_key: str):
        """Select the view to display"""
        self._view_config: DataViewConfig = DATA_VIEW_CONFIG[view_key]
        _ax_selector: AxesSelector = self._widgets["axes_selector"]
        _ax_selector.setVisible(
            self._data is not None and self._view_config.use_axes_selector
        )
        self._widgets["view_stack"].setVisible(self._data is not None)
        self._active_view = view_key
        self.__create_view_widget_if_required(view_key)
        self._widgets["view_stack"].setCurrentWidget(self._widgets[view_key])
        if self._view_config.use_axes_selector:
            _ax_selector.allow_fewer_dims = self._view_config.allow_fewer_dims
            _ax_selector.define_additional_choices(self._view_config.additional_choices)
        self.__update_ax_selector_for_h5py_data()
        self._update_view(view_key)

    def __create_view_widget_if_required(self, view_key: str):
        """Create the widgets for the selected view, if required"""
        if view_key in self._widgets:
            return
        _cfg_kwargs = self._plot2d_config if view_key == "view-image" else {}
        self._widgets[view_key] = self._view_config.widget(parent=None, **_cfg_kwargs)
        self._widgets["view_stack"].addWidget(self._widgets[view_key])
        if view_key == "view-image":
            self._widgets[view_key].sig_get_more_info_for_data.connect(
                self.sig_plot2d_get_more_info_for_data
            )

    def __update_ax_selector_for_h5py_data(self):
        """Update the axis selector if the data is a h5py dataset with chunking"""
        if isinstance(self._data, h5py.Dataset):
            _ax_selector: AxesSelector = self._widgets["axes_selector"]
            if self._data.chunks is not None:
                _sorted_chunking_dims = list(np.asarray(self._data.chunks).argsort())
                _used_index_dims = _sorted_chunking_dims[: -_ax_selector.n_choices]
            else:
                _used_index_dims = list(range(self._data.ndim - _ax_selector.n_choices))
            _ax_selector.assign_index_use_to_dims(_used_index_dims)

    @QtCore.Slot()
    def _update_view(self, view_key: str | None = None):
        """
        Update the selected view with the current data.

        Parameters
        ----------
        view_key : str | None
            The key of the view to update. If None, the currently active view
            will be updated.
        """
        if view_key is None:
            if self._active_view is None:
                return
            view_key = self._active_view
        _view = self._widgets[view_key]
        if self._button_group.checkedButton() != self._widgets[f"button_{view_key}"]:
            with QtCore.QSignalBlocker(self._widgets[f"button_{view_key}"]):
                self._widgets[f"button_{view_key}"].click()
        if view_key == "view-h5" and self._h5node is not None:
            _view.display_data(self._h5node)
            return
        if self._view_config.use_axes_selector:
            _ax_selector = self._widgets["axes_selector"]
            _data = self._data[*_ax_selector.current_slice].squeeze()
            if _ax_selector.transpose_required:
                _data = _data.T
        else:
            _data = self._data
        if not isinstance(_data, Dataset):
            _data = Dataset(_data)
        _view.display_data(_data, title=self._config["plot_title"])

    def set_data(
        self,
        data: H5Node | h5py.Dataset | np.ndarray | None,
        title: str | None = None,
        h5node: H5Node | None = None,
    ):
        """
        Set the data to display

        Parameters
        ----------
        data : H5Node | h5py.Dataset | np.ndarray | None
            The data to display. A ndarray is acceptable but will be converted to a
            Dataset object.
        title : str | None, optional
            The title of the data. If None, the title will not be updated.
        h5node : H5Node | None, optional
            The H5Node associated with the data. If provided, metadata about
            the data can be read from the H5Node.
        """
        self._widgets["container_for_buttons"].setVisible(data is not None)
        # Remove the data reference from the h5 view:
        if "view-h5" in self._widgets:
            self._widgets["view-h5"].setData(None)
        if data is None:
            if self._active_view is not None:
                self._widgets[self._active_view].clear()
            return
        if isinstance(data, H5Node):
            h5node = data
        # if isinstance(h5node, H5Node):
        self._h5node = h5node
        if title is not None:
            self._config["plot_title"] = title
        self._import_data(data)
        self._update_widgets_from_data()
        self._set_new_view()

    # Set up an alias for plotting
    plot_data = set_data

    def _import_data(self, data: Dataset | H5Node | h5py.Dataset | np.ndarray):
        """
        Store an internal reference to the imported data.

        Parameters
        ----------
        data : Dataset | H5Node | h5py.Dataset | np.ndarray
            The data to import.
        """
        _buffer_size = self.q_settings_get("global/data_buffer_size", dtype=float)
        if isinstance(data, h5py.Dataset):
            pass
        elif isinstance(data, H5Node):
            data = data.h5py_object
        elif isinstance(data, np.ndarray):
            if data.nbytes > _buffer_size * 1e6:
                raise UserConfigError(_DATASET_TOO_LARGE_ERROR)
            if not isinstance(data, Dataset):
                data = Dataset(data)
        else:
            raise UserConfigError(
                "The data to display must be a numpy array, a h5py.Dataset or a "
                "H5Node object."
            )
        self._data = data

    def _update_widgets_from_data(self):
        """Update the widgets based on the current data."""
        for _ref, _view in DATA_VIEW_CONFIG.items():
            self._widgets[f"button_{_ref}"].setVisible(
                _view.min_dims <= self._data.ndim
            )
        self._widgets["button_view-h5"].setVisible(self._h5node is not None)
        # reset the view if the data dimensionality is too low for the current view
        if (
            self._active_view is not None
            and self._data.ndim < self._view_config.min_dims
        ):
            self._active_view = None
            self._widgets["axes_selector"].define_additional_choices("")
        self._widgets["axes_selector"].set_metadata_from_dataset(self._data)

    def _set_new_view(self):
        """Set or update the current view."""
        _preferred_view: str | None = (
            self._data.metadata.get("preferred_view", None)
            if isinstance(self._data, Dataset)
            else None
        )
        if _preferred_view is not None:
            self._select_view(_preferred_view)
        elif self._data.ndim == 0 or self._data.size == 1:
            self._select_view("view-table")
        elif (
            self._data.ndim >= self._view_config.min_dims
            and self._active_view is not None
        ):
            self.__update_ax_selector_for_h5py_data()
            self._update_view()
        elif self._data.ndim == 1:
            self._select_view("view-curve")
        elif self._data.ndim >= 2 and self._active_view is None:
            self._select_view("view-image")
        else:
            self._update_view()

    def update_data(self, data: np.ndarray, title: str | None = None):
        """
        Update the stored data without updating the metadata.

        Parameters
        ----------
        data : np.ndarray
            The data.
        title : str | None, optional
            The title of the data. If None, the title will not be updated.
        """
        if title is not None:
            self._config["plot_title"] = title
        if not (isinstance(data, np.ndarray) and isinstance(self._data, np.ndarray)):
            raise UserConfigError(
                "Can only update data if both the stored data and the new data"
                "are np.ndarrays."
            )
        if data.shape != self._data.shape:
            raise UserConfigError(
                "Updated data must have the same shape as the previous data. "
                "Please check the input and try again. If the data does have "
                "a different shape, please use the `set_data` method."
            )
        self._data = data
        self._update_view()

    def deleteLater(self):
        for _widget in self.findChildren(QtWidgets.QWidget):
            _widget.deleteLater()
