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
from numpy._core.numeric import sort

from pydidas.gui.utils.main_menu_utils import get_available_exit_states


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
        "other_config_file.yaml",
    ]

    for filename in valid_files + invalid_files:
        file_path = tmp_path / filename
        file_path.write_text("")

    with patch("pydidas.gui.utils.main_menu_utils.PYDIDAS_CONFIG_PATHS", [tmp_path]):
        yield valid_files


def test_get_available_exit_states(mock_config_dir_exit_states):
    """
    Test that get_available_exit_states only returns valid filenames.
    """
    expected_filenames = mock_config_dir_exit_states

    actual_filenames = get_available_exit_states()

    assert actual_filenames == sorted(expected_filenames)


if __name__ == "__main__":
    pytest.main([__file__])
#
