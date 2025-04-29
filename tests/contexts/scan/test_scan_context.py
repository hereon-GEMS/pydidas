# This file is part of pydidas.
#
# Copyright 2023 - 2025, Helmholtz-Zentrum Hereon
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
__copyright__ = "Copyright 2023 - 2025, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"

import shutil
import tempfile
from pathlib import Path

import numpy as np
import pytest

from pydidas.contexts import ScanContext
from pydidas.contexts.scan import Scan
from pydidas.core.utils import get_random_string


@pytest.fixture(scope="module")
def temp_dir():
    _temp_path = Path(tempfile.mkdtemp())
    yield _temp_path
    shutil.rmtree(_temp_path)


def randomize_scan(obj: Scan):
    obj.set_param_value("scan_dim", 3)
    obj.set_param_value("scan_title", get_random_string(12))
    for _i in [0, 1, 2]:
        for _key in ["label", "unit"]:
            obj.set_param_value(f"scan_dim{_i}_{_key}", get_random_string(5))
        for _key in ["offset", "delta"]:
            obj.set_param_value(f"scan_dim{_i}_{_key}", 2 + 5 * np.random.random())
        obj.set_param_value(f"scan_dim{_i}_n_points", np.random.choice([9, 10, 11, 21]))


def test_init():
    scan = ScanContext()
    assert isinstance(scan, Scan)


def test__repeated_calls():
    scan = ScanContext()
    scan2 = ScanContext()
    assert id(scan) == id(scan2)


def test_copy():
    scan = ScanContext()
    _copy = scan.copy()
    assert id(_copy) != id(scan)
    assert isinstance(_copy, Scan)


def test_import_from_file(temp_dir):
    scan = Scan()
    randomize_scan(scan)
    scan.export_to_file(temp_dir / "test.yml")
    obj = ScanContext()
    obj.import_from_file(temp_dir / "test.yml")
    for _key, _val in scan.get_param_values_as_dict(
        filter_types_for_export=True
    ).items():
        assert obj.get_param_value(_key, for_export=True) == _val


if __name__ == "__main__":
    pytest.main()
