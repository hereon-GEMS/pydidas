# This file is part of pydidas.
#
# Copyright 2025 - 2026, Helmholtz-Zentrum Hereon
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

"""Unit tests for pydidas modules."""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2025 - 2026, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"


import h5py
import numpy as np
import pytest
from qtpy import QtCore

from pydidas.core import Dataset, UserConfigError
from pydidas.unittest_objects import create_dataset
from pydidas.widgets.data_viewer.axes_selector import AxesSelector
from pydidas.widgets.data_viewer.data_axis_selector import (
    DataAxisSelector,
)
from pydidas.widgets.data_viewer.data_viewer import DataViewer
from pydidas.widgets.silx_plot.pydidas_plot1d import PydidasPlot1D
from pydidas_qtcore import PydidasQApplication


_DATA = create_dataset(5, dtype=float)


@pytest.fixture
def data():
    return _DATA.copy()


@pytest.mark.gui
@pytest.mark.parametrize("explicit_view", [False, True])
@pytest.mark.parametrize("hdf5", [False, True])
@pytest.mark.parametrize("existing_data", [False, True])
def test_set_data__restores_configuration_before_first_render(
    monkeypatch, tmp_path, explicit_view: bool, hdf5: bool, existing_data: bool
) -> None:
    ### This test was written by an AI tool.
    _source = AxesSelector()
    _viewer = DataViewer()
    _file = h5py.File(tmp_path / "axes.h5", "w") if hdf5 else None
    try:
        _data = Dataset(np.arange(20 * 30).reshape(20, 30))
        _source.set_metadata_from_dataset(_data)
        _source.define_additional_choices("show all curves;;use as curves' x")
        _curves = _source.findChildren(DataAxisSelector)[0]
        _curves._widgets["combo_range"].setCurrentText("select range by indices")
        _edit = _curves._widgets["edit_range_index"]
        _edit.setText("2:4")
        _edit.editingFinished.emit()
        _source.process_new_slicing()
        _config = _source.export_configuration()
        _rendered = []

        def display_data(plot, data, **kwargs) -> None:
            if data.ndim == 2 and data.shape[0] > 3:
                raise UserConfigError("Too many curves")
            _rendered.append(data.array.copy())

        monkeypatch.setattr(PydidasPlot1D, "display_data", display_data)
        if existing_data:
            _viewer.set_data(Dataset(np.ones((2, 30))), view="view-curve-group")
            _rendered.clear()
        _input = _file.create_dataset("data", data=_data.array) if hdf5 else _data
        _viewer.set_data(
            _input,
            axes_config=_config,
            view="view-curve-group" if explicit_view else None,
        )
        assert len(_rendered) == 1
        np.testing.assert_array_equal(_rendered[0], _data.array[2:5])
        _target = _viewer.findChild(AxesSelector)
        assert _target.export_configuration() == _config
        _viewer._widgets["button_pop-out"].click()
        assert len(_rendered) == 2
        np.testing.assert_array_equal(_rendered[1], _data.array[2:5])
    finally:
        _viewer.deleteLater()
        _source.deleteLater()
        PydidasQApplication.instance().processEvents()
        if _file is not None:
            _file.close()


@pytest.mark.gui
def test_pop_out__copies_axis_selection() -> None:
    ### This test was written by an AI tool.
    _viewer = DataViewer()
    try:
        _viewer.set_data(Dataset(np.arange(7 * 8 * 9).reshape(7, 8, 9)))
        _selector = _viewer.findChild(AxesSelector)
        _selector.assign_index_use_to_dims([0])
        _axes = _selector.findChildren(DataAxisSelector)
        _axes[1].display_choice = _axes[2].display_choice
        _axes[0].display_choice = "slice at index"
        _axes[0].set_to_value(3)
        _selector.process_new_slicing()
        _viewer._widgets["button_pop-out"].click()
        _child = _viewer._pop_out_viewers[0]
        _child_selector = _child.findChild(AxesSelector)
        assert _child_selector.current_slice == _selector.current_slice
        assert (
            _child_selector.current_display_selection
            == _selector.current_display_selection
        )
        assert _child_selector.transpose_required == _selector.transpose_required
    finally:
        _viewer.deleteLater()
        PydidasQApplication.instance().processEvents()


@pytest.mark.gui
@pytest.mark.parametrize("parent_visible", [False, True])
def test_pop_out__opens_independent_window(parent_visible: bool) -> None:
    _viewer = DataViewer()
    try:
        _viewer.set_data(Dataset(np.arange(24).reshape(4, 6)))
        _viewer.setVisible(parent_visible)
        _viewer._widgets["button_pop-out"].click()
        PydidasQApplication.instance().processEvents()
        _child = _viewer._pop_out_viewers[0]
        assert _child is not None
        assert _child.isWindow()
        assert _child.isVisible()
        assert _child.window() is _child
        assert _child.current_slice == _viewer.current_slice
        assert _child.active_dims == _viewer.active_dims
    finally:
        _viewer.deleteLater()
        PydidasQApplication.instance().processEvents()


@pytest.mark.gui
@pytest.mark.parametrize("closed_index", [0, 1])
def test_pop_out__deletes_on_close(data, closed_index: int) -> None:
    _viewer = DataViewer()
    try:
        _viewer.set_data(data)
        _viewer._widgets["button_pop-out"].click()
        _viewer._widgets["button_pop-out"].click()
        PydidasQApplication.instance().processEvents()
        _child = _viewer._pop_out_viewers[closed_index]
        _remaining = _viewer._pop_out_viewers[1 - closed_index]
        assert _child.testAttribute(QtCore.Qt.WidgetAttribute.WA_DeleteOnClose)
        _child.close()
        PydidasQApplication.instance().processEvents()
        PydidasQApplication.instance().sendPostedEvents(
            None, QtCore.QEvent.DeferredDelete
        )
        assert _viewer._pop_out_viewers == [_remaining]
        assert _remaining.isVisible()
        _remaining.close()
        PydidasQApplication.instance().sendPostedEvents(
            None, QtCore.QEvent.DeferredDelete
        )
        assert _viewer._pop_out_viewers == []
    finally:
        _viewer.deleteLater()
        PydidasQApplication.instance().processEvents()


if __name__ == "__main__":
    pytest.main([__file__])
