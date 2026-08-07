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

"""Unit tests for pydidas.core.system.shared_memory."""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2026, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"


import uuid
from multiprocessing.shared_memory import SharedMemory

import pytest

from pydidas.core.system.shared_memory import create_or_replace_shared_memory


@pytest.fixture
def shm_name():
    """Yield a unique shared memory name and clean up after the test."""
    name = f"pytest_shm_{uuid.uuid4().hex[:12]}"
    yield name
    # Best-effort cleanup: attach and unlink if still present.
    try:
        _shm = SharedMemory(name=name, create=False)
        _shm.close()
        _shm.unlink()
    except FileNotFoundError:
        pass


def test_create_or_replace_shared_memory__creates_new(shm_name):
    shm = create_or_replace_shared_memory(shm_name, 64)
    assert shm is not None
    assert isinstance(shm, SharedMemory)


def test_create_or_replace_shared_memory__correct_size(shm_name):
    size = 128
    shm = create_or_replace_shared_memory(shm_name, size)
    assert shm.size == size


def test_create_or_replace_shared_memory__replaces_stale(shm_name):
    stale = SharedMemory(name=shm_name, create=True, size=32)
    stale.close()
    # Do NOT unlink — simulate a stale segment left by a crashed process.
    shm = create_or_replace_shared_memory(shm_name, 64)
    assert isinstance(shm, SharedMemory)


def test_create_or_replace_shared_memory__stale_replaced_with_new_size(shm_name):
    stale = SharedMemory(name=shm_name, create=True, size=32)
    stale.close()
    new_size = 256
    shm = create_or_replace_shared_memory(shm_name, new_size)
    assert shm.size == new_size


def test_create_or_replace_shared_memory__logs_warning_for_stale(shm_name):
    from unittest.mock import MagicMock, patch

    import pydidas.core.system.shared_memory as sm_module

    with patch.object(sm_module.logger, "warning") as mock_warn:
        with patch(
            "pydidas.core.system.shared_memory.SharedMemory",
            side_effect=[FileExistsError(), MagicMock(), MagicMock()],
        ):
            create_or_replace_shared_memory(shm_name, 64)
    mock_warn.assert_called_once()
    assert shm_name in mock_warn.call_args[0][0]


def test_create_or_replace_shared_memory__no_warning_for_fresh(shm_name):
    from unittest.mock import patch

    import pydidas.core.system.shared_memory as sm_module

    with patch.object(sm_module.logger, "warning") as mock_warn:
        create_or_replace_shared_memory(shm_name, 64)
    mock_warn.assert_not_called()


if __name__ == "__main__":
    pytest.main([__file__])
