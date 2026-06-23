# This file is part of pydidas.
#
# Copyright 2023 - 2026, Helmholtz-Zentrum Hereon
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
__copyright__ = "Copyright 2023 - 2026, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"


from numbers import Integral, Real

import numpy as np
import pytest

from pydidas.contexts.scan import Scan, ScanContext
from pydidas.contexts.scan.scan_io_base import ScanIoBase
from pydidas.core import UserConfigError
from pydidas.core.utils import get_random_string


SCAN = ScanContext()


@pytest.fixture
def populated_scan() -> Scan:
    """Return a Scan with randomized parameter values."""
    _scan = Scan()
    for _param in _scan.params.values():
        if _param.dtype == str and _param.choices is None:
            _param.value = get_random_string(6)
        elif _param.dtype == Real:
            _param.value = np.random.random()
        elif _param.dtype == Integral and _param.refkey != "scan_dim":
            _param.value = int(100 * np.random.random())
    return _scan


def test_verify_all_entries_present__correct() -> None:
    _params = {param: True for param in SCAN.params}
    ScanIoBase._verify_all_entries_present(_params)


def test_verify_all_entries_present__missing_keys() -> None:
    with pytest.raises(UserConfigError):
        ScanIoBase._verify_all_entries_present({})


def test_write_to_scan_settings__generic_ScanContext(populated_scan: Scan) -> None:
    _params = populated_scan.get_param_values_as_dict()
    ScanIoBase._write_to_scan_settings(_params)
    for _key, _value in _params.items():
        assert SCAN.get_param_value(_key) == _value


def test_write_to_scan_settings__given_scan(populated_scan: Scan) -> None:
    _new_scan = Scan()
    _params = populated_scan.get_param_values_as_dict()
    ScanIoBase._write_to_scan_settings(_params, scan=_new_scan)
    SCAN.restore_all_defaults(True)
    for _key, _value in _params.items():
        assert _new_scan.get_param_value(_key) == _value
    assert SCAN.get_param_value("scan_dim1_label") == ""


def test_convert_legacy_param_names__w_scan_start_index() -> None:
    _params = {"scan_start_index": 42}
    ScanIoBase._convert_legacy_param_names(_params)
    assert _params["pattern_number_offset"] == 42
    assert _params["pattern_number_delta"] == 1
    assert "scan_start_index" not in _params


def test_convert_legacy_param_names__w_scan_start_index__duplicate() -> None:
    _params = {"scan_start_index": 42, "pattern_number_offset": 0}
    with pytest.raises(UserConfigError):
        ScanIoBase._convert_legacy_param_names(_params)


def test_convert_legacy_param_names__w_scan_index_stepping() -> None:
    _params = {"scan_index_stepping": 2}
    ScanIoBase._convert_legacy_param_names(_params)
    assert _params["frame_indices_per_scan_point"] == 2
    assert "scan_index_stepping" not in _params


def test_convert_legacy_param_names__w_scan_index_stepping__duplicate() -> None:
    _params = {"scan_index_stepping": 2, "frame_indices_per_scan_point": 0}
    with pytest.raises(UserConfigError):
        ScanIoBase._convert_legacy_param_names(_params)


def test_convert_legacy_param_names__w_scan_multiplicity() -> None:
    _params = {"scan_multiplicity": 7}
    ScanIoBase._convert_legacy_param_names(_params)
    assert _params["scan_frames_per_point"] == 7
    assert "scan_multiplicity" not in _params


def test_convert_legacy_param_names__w_scan_multiplicity__duplicate() -> None:
    _params = {"scan_multiplicity": 7, "scan_frames_per_point": 2}
    with pytest.raises(UserConfigError):
        ScanIoBase._convert_legacy_param_names(_params)


def test_convert_legacy_param_names__w_scan_multi_image_handling() -> None:
    _params = {"scan_multi_image_handling": "Average"}
    ScanIoBase._convert_legacy_param_names(_params)
    assert _params["scan_multi_frame_handling"] == "Average"
    assert "scan_multi_image_handling" not in _params


def test_convert_legacy_param_names__w_scan_multi_image_handling__duplicate() -> None:
    _params = {
        "scan_multi_image_handling": "Average",
        "scan_multi_frame_handling": "Sum",
    }
    with pytest.raises(UserConfigError):
        ScanIoBase._convert_legacy_param_names(_params)


def test_check_file_list() -> None:
    _res = ScanIoBase.check_file_list(["scan_0001.h5", "scan_0002.h5"])
    assert _res == ["::no_error::"]


if __name__ == "__main__":
    pytest.main([__file__])
