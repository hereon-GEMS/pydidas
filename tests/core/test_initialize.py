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


from unittest.mock import MagicMock, patch

import pytest
from qtpy import QtCore

from pydidas.initialize import initialize_qsetting_values
from pydidas.version import VERSION


@pytest.fixture
def mock_settings(tmp_path):
    """
    Redirects QSettings to a temporary file for the test.
    """
    test_conf_file = tmp_path / "test_pydidas.conf"

    unmodified_qsettings = QtCore.QSettings
    unmodified_format = QtCore.QSettings.Format.IniFormat

    def tmp_settings_factory(*args, **kwargs):
        return unmodified_qsettings(str(test_conf_file), unmodified_format)

    with patch("qtpy.QtCore.QSettings", side_effect=tmp_settings_factory):
        yield test_conf_file


@patch("pydidas.core.constants.QSETTINGS_GLOBAL_KEYS", ["test_key"])
@patch("pydidas.core.constants.QSETTINGS_USER_KEYS", [])
@patch("pydidas.core.constants.QSETTINGS_USER_SPECIAL_KEYS", [])
def test_initialize_qsettings_values__old_version(mock_settings):
    setup_settings = QtCore.QSettings()
    setup_settings.setValue("00.00.00/global/test_key", "test_value")
    setup_settings.sync()
    del setup_settings

    initialize_qsetting_values()

    verify_settings = QtCore.QSettings()
    assert verify_settings.value(f"{VERSION}/global/test_key") == "test_value"


@patch("pydidas.core.constants.QSETTINGS_GLOBAL_KEYS", ["other_test_key"])
@patch("pydidas.core.constants.QSETTINGS_USER_KEYS", [])
@patch("pydidas.core.constants.QSETTINGS_USER_SPECIAL_KEYS", [])
@patch("pydidas.initialize.get_generic_parameter")
def test_initialize_qsettings_values__default_value(mock_get_param, mock_settings):
    mock_param = MagicMock()
    mock_param.default = "default_value"
    mock_get_param.return_value = mock_param

    initialize_qsetting_values()

    verify_settings = QtCore.QSettings()
    assert verify_settings.value(f"{VERSION}/global/other_test_key") == "default_value"


if __name__ == "__main__":
    pytest.main([__file__])
#
