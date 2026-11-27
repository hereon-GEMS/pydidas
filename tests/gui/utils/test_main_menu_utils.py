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

"""Unit tests for pydidas modules."""

__author__ = "Nonni Heere"
__copyright__ = "Copyright 2026, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"


from unittest.mock import patch

import pytest
from qtpy import QtCore

from pydidas import VERSION
from pydidas.contexts import GLOBAL_CONTEXTS, DiffractionExperimentContext
from pydidas.core import UserConfigError
from pydidas.gui.frames.define_diffraction_exp_frame import DefineDiffractionExpFrame
from pydidas.gui.utils.main_menu_utils import (
    get_available_exit_states,
    restore_global_objects,
)
from pydidas.unittest_objects.signal_spy import SignalSpy


@pytest.fixture
def mock_config_dir_exit_states(tmp_path):
    """
    Creates a temporary configuration directory with valid and invalid files,
    then patches PYDIDAS_CONFIG_PATHS to point only to this directory.
    """

    valid_files = [
        "pydidas_gui_exit_state_01.02.03.yaml",
        "pydidas_gui_exit_state_02.00.00.yaml",
        "pydidas_gui_exit_state_00.45.12.yaml",
    ]

    invalid_files = [
        "pydidas_gui_exit_state_1.2.3.yaml",
        "pydidas_gui_exit_state_01.02.03.txt",
        f"custom_gui_exit_state_{VERSION}.yaml",
        "custom_gui_exit_state_01.02.03.yaml",
        "other_config_file.yaml",
    ]

    for filename in valid_files + invalid_files:
        file_path = tmp_path / filename
        file_path.write_text("")

    with patch("pydidas.gui.utils.main_menu_utils.PYDIDAS_CONFIG_PATHS", [tmp_path]):
        yield valid_files


@pytest.mark.gui
def test_get_available_exit_states__w_standard_name(mock_config_dir_exit_states):
    """
    Test that get_available_exit_states only returns valid filenames.
    """
    expected_filenames = mock_config_dir_exit_states

    actual_filenames = get_available_exit_states(
        f"pydidas_gui_exit_state_{VERSION}.yaml"
    )

    assert actual_filenames == sorted(expected_filenames)


@pytest.mark.gui
def test_get_available_exit_states__w_custom_name(mock_config_dir_exit_states):
    """
    Test that get_available_exit_states returns the custom name.
    """
    actual_filenames = get_available_exit_states(
        f"custom_gui_exit_state_{VERSION}.yaml"
    )

    assert actual_filenames == [
        "custom_gui_exit_state_01.02.03.yaml",
    ]


@pytest.fixture
def context_state(qapp):
    ### This fixture was written by an AI tool
    _state = {
        f"context::{_key}": _context.get_param_values_as_dict()
        for _key, _context in GLOBAL_CONTEXTS.items()
    }
    _state["context::workflow_tree"] = "[]"
    try:
        yield _state
    finally:
        for _key, _context in GLOBAL_CONTEXTS.items():
            with QtCore.QSignalBlocker(_context):
                for _param, _value in _state[f"context::{_key}"].items():
                    _context.set_param_value(_param, _value)


@pytest.mark.gui
@pytest.mark.parametrize("invalid_parameter", [False, True])
def test_restore_global_objects__batches_notifications(
    context_state, invalid_parameter: bool
) -> None:
    ### This test was written by an AI tool
    _state = {
        _key: dict(_value) if isinstance(_value, dict) else _value
        for _key, _value in context_state.items()
    }
    _params = _state["context::diffraction_experiment_context"]
    _params.update(detector_name="detector", detector_npixx=0, detector_npixy=0)
    if invalid_parameter:
        _params["detector_pxsizex"] = "invalid"
    _spy = SignalSpy(DiffractionExperimentContext().sig_params_changed)
    with patch("pydidas.gui.utils.main_menu_utils.TREE.restore_from_string"):
        if invalid_parameter:
            with pytest.raises(UserConfigError, match="detector_pxsizex"):
                restore_global_objects(_state)
        else:
            restore_global_objects(_state)
    assert _spy.n == 1
    assert not DiffractionExperimentContext().detector_is_valid


@pytest.mark.gui
def test_restore_global_objects__legacy_detector_updates_beamcenter(
    context_state, qapp
) -> None:
    ### This test was written by an AI tool
    _exp = DiffractionExperimentContext()
    _frame = DefineDiffractionExpFrame()
    try:
        _frame.frame_activated(_frame.frame_index + 1)
        _frame.frame_activated(_frame.frame_index)
        _state = {
            _key: dict(_value) if isinstance(_value, dict) else _value
            for _key, _value in context_state.items()
        }
        _state["context::diffraction_experiment_context"].update(
            detector_name="detector",
            detector_npixx=0,
            detector_npixy=0,
            detector_pxsizex=100.0,
            detector_pxsizey=100.0,
            detector_poni1=0.0,
            detector_poni2=0.0,
            detector_rot1=0.0,
            detector_rot2=0.0,
            detector_rot3=0.0,
        )
        with patch("pydidas.gui.utils.main_menu_utils.TREE.restore_from_string"):
            restore_global_objects(_state)
        for _key in ("beamcenter_x", "beamcenter_y"):
            _widget = _frame.param_widgets[_key]
            assert not _widget.isEnabled()
            assert _widget.text() == ""
            assert _widget.placeholderText() == "Unavailable"
        with pytest.raises(UserConfigError, match="detector is invalid"):
            _exp.as_fit2d_geometry_values()
        _exp.set_param_value("detector_npixx", 100)
        _exp.set_param_value("detector_npixy", 100)
        for _key in ("beamcenter_x", "beamcenter_y"):
            _widget = _frame.param_widgets[_key]
            assert _widget.isEnabled()
            assert float(_widget.text()) == 0.0
    finally:
        _frame.deleteLater()
        qapp.sendPostedEvents(None, QtCore.QEvent.DeferredDelete)


if __name__ == "__main__":
    pytest.main([__file__])
