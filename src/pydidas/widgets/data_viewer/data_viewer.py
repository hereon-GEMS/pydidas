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
from silx.gui.data.DataViewer import DataSelection
from silx.gui.data.DataViews import DataInfo, _RawView
from silx.gui.hdf5 import H5Node

from pydidas.core import Dataset, UserConfigError
from pydidas.widgets.data_viewer import AxesSelector
from pydidas.widgets.data_viewer.data_axis_selector import GENERIC_AXIS_SELECTOR_CHOICES
from pydidas.widgets.data_viewer.data_viewer_utils import (
    DATA_VIEW_CONFIG,
    DATA_VIEW_REFS,
    DATA_VIEW_TITLES,
)
from pydidas.widgets.silx_plot import PydidasPlot2D
from pydidas.widgets.widget_with_parameter_collection import (
    WidgetWithParameterCollection,
)


DATASET_TOO_LARGE_ERROR = (
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
        self._metadata_updated = False
        self._title = None
        self._active_view = None
        self._button_group = QtWidgets.QButtonGroup()
        self._view_objects = {
            _key: DATA_VIEW_CONFIG[_key]["view"](None)
            for _key in DATA_VIEW_CONFIG.keys()
        }
        self.__use_multilines = kwargs.get("multiline_layout", False)
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
            AxesSelector(multiline_layout=self.__use_multilines),
            gridPos=(1, 0, 1, 1),
            parent_widget="view_container",
            visible=False,
        )
        self._widgets["axes_selector"].sig_new_slicing.connect(self._update_view)
        self.create_empty_widget("container_for_buttons", gridPos=(-1, 0, 1, 1))
        for _id, _view in DATA_VIEW_CONFIG.items():
            self.create_button(
                f"button_{_id}",
                _view["title"],
                checkable=True,
                gridPos=(0, -1, 1, 1),
                icon=f"pydidas::{_view['ref']}.svg",
                parent_widget="container_for_buttons",
                clicked=partial(self._select_view, _id),
            )
            self._button_group.addButton(self._widgets[f"button_{_id}"], _id)
        self.layout().setColumnStretch(0, 1)
        self.layout().setRowStretch(0, 1)

    @property
    def active_dims(self) -> tuple[int]:
        """
        Get the active dimensions.

        Returns
        -------
        tuple[int]
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

    @QtCore.Slot(int)
    def _select_view(self, view_id: int):
        """Select the view to display"""
        self._widgets["axes_selector"].setVisible(self._data is not None)
        self._widgets["view_stack"].setVisible(self._data is not None)
        self._active_view = view_id
        self.__create_view_widgets_if_required(view_id)
        self._widgets["view_stack"].setCurrentWidget(self._widgets[f"view_{view_id}"])
        self._widgets["axes_selector"].setVisible(
            DATA_VIEW_CONFIG[view_id]["use_axes_selector"]
        )
        if DATA_VIEW_CONFIG[view_id]["use_axes_selector"]:
            self._widgets["axes_selector"]._allow_less_dims = (
                DATA_VIEW_REFS["view-table"] == view_id
            )
            self._widgets["axes_selector"].define_additional_choices(
                DATA_VIEW_CONFIG[view_id]["additional choices"]
            )
        self._update_view(view_id)

    def __create_view_widgets_if_required(self, view_id: int):
        """Create the widgets for the selected view, if required"""
        if f"view_{view_id}" in self._widgets:
            return
        _view_config = DATA_VIEW_CONFIG[view_id]
        self.create_empty_widget(f"view_{view_id}", parent_widget=None)
        self._widgets[f"view_{view_id}"].layout().setRowStretch(0, 1)
        self._widgets["view_stack"].addWidget(self._widgets[f"view_{view_id}"])
        _vis_widget = self._view_objects[view_id].getWidget()
        self.add_any_widget(
            f"view_{view_id}_vis",
            _vis_widget,
            parent_widget=f"view_{view_id}",
        )
        if isinstance(_vis_widget, PydidasPlot2D):
            if self._plot2d_config["diffraction_exp"] is not None:
                _vis_widget._config["diffraction_exp"] = self._plot2d_config[
                    "diffraction_exp"
                ]
            if self._plot2d_config["use_data_info_action"]:
                _vis_widget._config["use_data_info_action"] = True
                _vis_widget._add_data_info_action()
                _vis_widget.sig_get_more_info_for_data.connect(
                    self.sig_plot2d_get_more_info_for_data
                )

    @QtCore.Slot()
    def _update_view(self, view_id: int | None = None):
        """
        Update the selected view with the current data.

        Parameters
        ----------
        view_id : int
            The id of the view to update
        """
        if view_id is None:
            if self._active_view is None:
                return
            view_id = self._active_view
        if self._button_group.checkedButton() != self._widgets[f"button_{view_id}"]:
            self._widgets[f"button_{view_id}"].click()
        _view = self._view_objects[view_id]
        if not self._metadata_updated:
            self._widgets["axes_selector"].set_metadata_from_dataset(self._data)
            self._metadata_updated = True
        if DATA_VIEW_CONFIG[view_id]["use_axes_selector"]:
            _ax_selector = self._widgets["axes_selector"]
            _data = self._data[*_ax_selector.current_slice].squeeze()
            _display_selection = _ax_selector.current_display_selection
            if _ax_selector.transpose_required:
                _data = _data.T
        else:
            _data = self._data
        self._view_objects[view_id].setData(_data)
        if DATA_VIEW_CONFIG[view_id]["ref"] in [
            "view-image",
            "view-curve",
            "view-curve-group",
        ]:
            _view.getWidget().setGraphTitle(self._title)
        if isinstance(_view, _RawView):
            _data_selection = DataSelection(None, None, None, None)
            _matching_views = _view.getMatchingViews(_data, DataInfo(_data))
            _best_view = _view._SelectOneDataView__getBestView(_data, DataInfo(_data))
            _view._SelectOneDataView__currentView = _best_view
            _view.select()
            _view.setData(_data)

    def set_data(
        self, data: H5Node | h5py.Dataset | np.ndarray | None, title: str | None = None
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
        """
        if data is None:
            return
        self._import_data(data)
        if title is not None:
            self._title = title
        for _id, _view in DATA_VIEW_CONFIG.items():
            self._widgets[f"button_{_id}"].setVisible(_view["min_dims"] <= data.ndim)
        self._widgets[f"button_{DATA_VIEW_REFS['view-h5']}"].setVisible(False)
        _preferred_view = self._data.metadata.get("preferred_view", None)
        if _preferred_view is not None:
            self._select_view(DATA_VIEW_TITLES[_preferred_view])
        elif self._data.ndim == 0 or self._data.size == 1:
            self._select_view(DATA_VIEW_TITLES["Table"])
        elif self._data.ndim == 1:
            self._select_view(DATA_VIEW_TITLES["Curve"])
        elif self._data.ndim >= 2 and self._active_view is None:
            self._select_view(DATA_VIEW_TITLES["Image"])
        else:
            self._update_view()

    def _import_data(self, data: H5Node | h5py.Dataset | np.ndarray):
        """
        Import the data to a Dataset object.

        Parameters
        ----------
        data : H5Node | h5py.Dataset | np.ndarray
            The data to import.
        """
        _buffersize = self.q_settings_get("global/data_buffer_size", dtype=float)
        if isinstance(data, h5py.Dataset):
            # TODO: Implement the loading of HDF5 datasets
            raise NotImplementedError("HDF5 datasets are not supported yet.")
        elif isinstance(data, H5Node):
            # TODO: Implement the loading of HDF5 nodes
            raise NotImplementedError("HDF5 nodes are not supported yet.")
        elif isinstance(data, np.ndarray):
            if data.nbytes > _buffersize * 1e6:
                raise UserConfigError(DATASET_TOO_LARGE_ERROR)
            if not isinstance(data, Dataset):
                data = Dataset(data)
            self._data = data
            self._metadata_updated = False
        else:
            raise UserConfigError(
                "The data to display must be a numpy array, a h5py dataset or a "
                "H5Node object."
            )

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
            self._title = title
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
