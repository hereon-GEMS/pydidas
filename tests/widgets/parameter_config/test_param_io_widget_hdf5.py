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

"""
Module with unittests for pydidas.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2025 - 2026, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"


from unittest.mock import patch

import h5py
import numpy as np
import pytest

from pydidas.core import Hdf5key, NXdataKey, Parameter, get_generic_parameter
from pydidas.unittest_objects import SignalSpy
from pydidas.widgets.parameter_config.param_io_widget_hdf5 import (
    ParamIoWidgetHdf5Key,
    ParamIoWidgetNXdata,
)
from pydidas_qtcore import PydidasQApplication


_POPULATED_KEYS = {
    "/entry/data/data_0001": (3, 4, 5),
    "/entry/data/data_0002": (10, 10),
    "/entry/metadata/experiment": (5,),
    "/entry/data2/test": (4, 6),
}

_PARAMS = [get_generic_parameter("hdf5_key"), get_generic_parameter("nxdata_key")]


def widget_instance(qtbot, param: Parameter = _PARAMS[0], qref: str | None = None):
    param.restore_default()
    if param.dtype == Hdf5key:
        _widget_class = ParamIoWidgetHdf5Key
    elif param.dtype == NXdataKey:
        _widget_class = ParamIoWidgetNXdata
    widget = _widget_class(param, persistent_qsettings_ref=qref)
    widget.spy_new_value = SignalSpy(widget.sig_new_value)
    widget.spy_value_changed = SignalSpy(widget.sig_value_changed)
    widget.show()
    qtbot.add_widget(widget)
    qtbot.wait_until(lambda: widget.isVisible(), timeout=500)
    return widget


@pytest.fixture(scope="module")
def test_dir(temp_path):
    dir_path = temp_path / "param_io_widget_hdf5key_tests"
    dir_path.mkdir()
    with h5py.File(dir_path / "test_file.h5", "w") as f:
        for _key, _shape in _POPULATED_KEYS.items():
            f[_key] = np.random.random(_shape)
    return dir_path


@pytest.fixture(autouse=True)
def _cleanup():
    yield
    app = PydidasQApplication.instance()
    for widget in [
        _w for _w in app.topLevelWidgets() if isinstance(_w, ParamIoWidgetHdf5Key)
    ]:
        widget.deleteLater()
    app.processEvents()


@pytest.mark.gui
@pytest.mark.parametrize("qref", [None, "test_ref_hdf5_key"])
@pytest.mark.parametrize("param", _PARAMS)
def test__creation(qtbot, param, test_dir, qref):
    widget = widget_instance(qtbot, param, qref=qref)
    if param.dtype == Hdf5key:
        assert isinstance(widget, ParamIoWidgetHdf5Key)
    if param.dtype == NXdataKey:
        assert isinstance(widget, ParamIoWidgetNXdata)
    assert hasattr(widget, "sig_new_value")
    assert hasattr(widget, "sig_value_changed")
    if qref is None:
        assert widget._io_qsettings_ref is None
    else:
        assert widget._io_qsettings_ref == qref


@pytest.mark.gui
@pytest.mark.parametrize("fname", [None, "test_file.h5"])
@pytest.mark.parametrize("selected_dset", [None, list(_POPULATED_KEYS)[0]])
def test_button_function(qtbot, test_dir, fname, selected_dset):
    widget = widget_instance(qtbot)
    if fname is not None:
        fname = test_dir / fname
    _entry = widget.current_text
    with (
        patch(
            "pydidas.widgets.file_dialog.PydidasFileDialog.get_existing_filename",
            return_value=fname,
        ),
        patch(
            "pydidas.widgets.dialogues.Hdf5DatasetSelectionPopup.get_dset",
            return_value=selected_dset,
        ),
    ):
        widget.button_function()
        if fname is not None and selected_dset is not None:
            assert widget.current_text == selected_dset
            assert widget.spy_value_changed.n == 1
            assert widget.spy_new_value.n == 1
        else:
            assert widget.current_text == _entry
            assert widget.spy_value_changed.n == 0
            assert widget.spy_new_value.n == 0


if __name__ == "__main__":
    pytest.main([])
