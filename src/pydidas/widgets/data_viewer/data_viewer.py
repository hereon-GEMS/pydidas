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
from typing import Optional, Union

import h5py
import numpy as np
from qtpy import QtCore, QtWidgets
from silx.gui.data.DataViewer import DataSelection
from silx.gui.data.DataViews import DataInfo, _RawView
from silx.gui.hdf5 import H5Node

from pydidas.core import Dataset, UserConfigError
from pydidas.widgets.data_viewer import AxesSelector
from pydidas.widgets.data_viewer.data_viewer_utils import (
    DATA_VIEW_CONFIG,
    DATA_VIEW_REFS,
    DATA_VIEW_TITLES,
)
from pydidas.widgets.widget_with_parameter_collection import (
    WidgetWithParameterCollection,
)


class DataViewer(WidgetWithParameterCollection):
    """
    The DataViewer allows to display data in multiple display modes.
    """

    def __init__(self, parent: Optional[QtWidgets.QWidget] = None, **kwargs: dict):
        WidgetWithParameterCollection.__init__(self, parent=parent, **kwargs)

        self._data = None
        self._active_view = None
        self._view_selectors_updated = []
        self._button_group = QtWidgets.QButtonGroup()
        self._view_objects = {
            _key: DATA_VIEW_CONFIG[_key]["view"](None)
            for _key in DATA_VIEW_CONFIG.keys()
        }
        self._create_widgets()

    def _create_widgets(self):
        """Create all required widgets"""
        self.add_any_widget(
            "view_stack",
            QtWidgets.QStackedWidget(),
            gridPos=(0, 0, 1, 1),
            minimumHeight=400,
        )
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

    @QtCore.Slot(int)
    def _select_view(self, view_id: int):
        """Select the view to display"""
        self._active_view = view_id
        self.__create_view_widgets_if_required(view_id)
        self.__update_view_selectors_if_required(view_id)
        self._widgets["view_stack"].setCurrentWidget(self._widgets[f"view_{view_id}"])
        self._update_view(view_id)

    def __create_view_widgets_if_required(self, view_id: int):
        """Create the widgets for the selected view, if required"""
        if f"view_{view_id}" in self._widgets:
            return
        _view_config = DATA_VIEW_CONFIG[view_id]
        self.create_empty_widget(f"view_{view_id}", parent_widget=None)
        self._widgets[f"view_{view_id}"].layout().setRowStretch(0, 1)
        self._widgets["view_stack"].addWidget(self._widgets[f"view_{view_id}"])
        self.add_any_widget(
            f"view_{view_id}_vis",
            self._view_objects[view_id].getWidget(),
            parent_widget=f"view_{view_id}",
        )
        if _view_config["use_axes_selector"]:
            _selector = AxesSelector(
                allow_less_dims=DATA_VIEW_REFS["view-table"] == view_id
            )
            self.add_any_widget(
                f"view_{view_id}_ax_selector",
                _selector,
                parent_widget=f"view_{view_id}",
            )
            _selector.define_additional_choices(_view_config["additional choices"])
            _selector.sig_new_slicing.connect(partial(self._update_view, view_id))

    def __update_view_selectors_if_required(self, view_id: int):
        """Update the view selectors if required"""
        if (
            view_id not in self._view_selectors_updated
            and DATA_VIEW_CONFIG[view_id]["use_axes_selector"]
        ):
            self._widgets[f"view_{view_id}_ax_selector"].set_metadata_from_dataset(
                self._data
            )
            self._view_selectors_updated.append(view_id)

    @QtCore.Slot()
    def _update_view(self, view_id: int):
        """
        Update the selected view with the current data.

        Parameters
        ----------
        view_id : int
            The id of the view to update
        """
        _view = self._view_objects[view_id]
        if DATA_VIEW_CONFIG[view_id]["use_axes_selector"]:
            _ax_selector = self._widgets[f"view_{view_id}_ax_selector"]
            _data = self._data[*_ax_selector.current_slice].squeeze()
            _display_selection = _ax_selector.current_display_selection
            if _ax_selector.transpose_required:
                _data = _data.T
        else:
            _data = self._data
        self._view_objects[view_id].setData(_data)
        if isinstance(_view, _RawView):
            _data_selection = DataSelection(None, None, None, None)
            _matching_views = _view.getMatchingViews(_data, DataInfo(_data))
            _best_view = _view._SelectOneDataView__getBestView(_data, DataInfo(data))
            _view._SelectOneDataView__currentView = _best_view
            _view.select()
            _view.setData(_data)

    def set_data(self, data: Union[H5Node, h5py.Dataset, np.ndarray]):
        """
        Set the data to display

        Parameters
        ----------
        data : np.ndarray
            The data to display. A ndarray is acceptable but will be converted to a
            Dataset object.
        """
        self._view_selectors_updated = []
        if isinstance(data, h5py.Dataset):
            # TODO: Implement the loading of HDF5 datasets
            raise NotImplementedError("HDF5 datasets are not supported yet.")
        elif isinstance(data, H5Node):
            # TODO: Implement the loading of HDF5 nodes
            raise NotImplementedError("HDF5 nodes are not supported yet.")
            self._load_silx_h5node(data)
            return
        elif isinstance(data, np.ndarray):
            if not isinstance(data, Dataset):
                data = Dataset(data)
            self._data = data

        _buffersize = self.q_settings_get("global/data_buffer_size", dtype=float)
        if self._data.nbytes > _buffersize * 1e6:
            raise UserConfigError(
                "The dataset is too large to display. Please check the dataset or "
                "increase the data buffer size in the global settings."
            )
        for _id, _view in DATA_VIEW_CONFIG.items():
            self._widgets[f"button_{_id}"].setVisible(_view["min_dims"] <= data.ndim)
        self._widgets[f"button_{DATA_VIEW_REFS['view-h5']}"].setVisible(False)
        _preferred_view = data.metadata.get("preferred_view", None)
        if _preferred_view is not None:
            self._select_view(DATA_VIEW_TITLES[_preferred_view])
            return
        if data.ndim == 0:
            self._select_view(4)
        elif data.ndim == 1:
            self._select_view(1)

    def deleteLater(self):
        for _widget in self.findChildren(QtWidgets.QWidget):
            _widget.deleteLater()


if __name__ == "__main__":
    import sys

    import pydidas_qtcore
    from pydidas.gui import gui_excepthook
    from pydidas.unittest_objects import create_dataset

    sys.excepthook = gui_excepthook
    data = create_dataset(5, float)
    app = pydidas_qtcore.PydidasQApplication([])
    window = DataViewer()
    window.set_data(data)
    window.show()
    app.exec_()
