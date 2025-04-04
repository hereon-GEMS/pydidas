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

"""Unit tests for pydidas modules."""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2025, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"

import shutil
import tempfile
from pathlib import Path

import numpy as np
import pytest

from pydidas_plugins.output_plugins.spreadsheet_saver import SpreadsheetSaver

from pydidas.core import Dataset, UserConfigError


@pytest.fixture
def temp_dir():
    dirpath = tempfile.mkdtemp()
    yield dirpath
    shutil.rmtree(dirpath)


@pytest.fixture
def plugin(temp_dir):
    _plugin = SpreadsheetSaver()
    _plugin.set_param_value("directory_path", temp_dir)
    _plugin.node_id = 1
    return _plugin


@pytest.mark.parametrize(
    "delimiters",
    [
        ("Single space", " "),
        ("Tabulator", "\t"),
        ("Comma", ","),
        ("Double space", "  "),
        ("Comma and space", ", "),
        ("Semicolon", ";"),
        ("Semicolon and space", "; "),
    ],
)
@pytest.mark.parametrize("sig_digits", [2, 5, 12])
def test_pre_execute(plugin, delimiters, sig_digits):
    plugin.set_param_value("significant_digits", sig_digits)
    plugin.set_param_value("delimiter", delimiters[0])
    plugin.pre_execute()
    assert plugin._format == f"%.{sig_digits}e"
    assert plugin._delimiter == delimiters[1]


@pytest.mark.parametrize("sig_digits", [-1, 0])
def test_pre_execute__invalid_significant_digits(plugin, sig_digits):
    plugin.set_param_value("significant_digits", sig_digits)
    with pytest.raises(UserConfigError):
        plugin.pre_execute()


@pytest.mark.parametrize("output_fname_digits", [-1, 0])
def test_pre_execute__invalid_output_fname_digits(plugin, output_fname_digits):
    plugin.set_param_value("output_fname_digits", output_fname_digits)
    with pytest.raises(UserConfigError):
        plugin.pre_execute()


def test_execute__invalid_data_dim(plugin):
    data = np.random.rand(3, 3, 3)
    with pytest.raises(UserConfigError):
        plugin.execute(data)


def test_execute__test_case(plugin):
    data = Dataset(np.random.rand(3, 3))
    _new_data, _ = plugin.execute(data, test=True)
    assert np.allclose(_new_data, data)


@pytest.mark.parametrize(
    "delimiters",
    [
        ("Single space", " "),
        ("Tabulator", "\t"),
        ("Comma", ","),
        ("Double space", "  "),
        ("Comma and space", ", "),
        ("Semicolon", ";"),
        ("Semicolon and space", "; "),
    ],
)
@pytest.mark.parametrize(
    "header", [("Spreadsheet (.spr)", "spr"), ("CSV (.csv)", "csv")]
)
@pytest.mark.parametrize("output_fname_digits", [2, 5])
def test_execute(plugin, delimiters, header, output_fname_digits):
    data = Dataset(np.random.rand(5, 5))
    plugin.set_param_value("header", header[0])
    plugin.set_param_value("significant_digits", 5)
    plugin.set_param_value("delimiter", delimiters[0])
    plugin.set_param_value("label", "test")
    plugin.set_param_value("output_fname_digits", output_fname_digits)
    plugin.pre_execute()
    plugin.execute(data, global_index=1)
    _fname = Path(plugin.get_output_filename(header[1]))
    _imported_data = np.genfromtxt(_fname, delimiter=delimiters[1], skip_header=1)
    assert _fname.exists()
    assert np.allclose(_imported_data, data)


if __name__ == "__main__":
    pytest.main()
