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

"""
The shared_memory module provides functions for managing shared
memory.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2026, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"
__all__ = ["create_or_replace_shared_memory"]


from multiprocessing.shared_memory import SharedMemory
from typing import Any

from pydidas.core.utils import pydidas_logger


logger = pydidas_logger()


def create_or_replace_shared_memory(name: str, size: int) -> SharedMemory:
    """
    Create a SharedMemory segment, replacing any stale segment with the same name.

    On Unix, named shared memory segments persist after a process crash. This
    function handles the ``FileExistsError`` raised when a stale segment with the
    same name already exists by unlinking it before creating a fresh one.

    Parameters
    ----------
    name : str
        The name for the shared memory segment.
    size : int
        The size in bytes for the new shared memory segment.

    Returns
    -------
    SharedMemory
        The newly created SharedMemory object.
    """
    try:
        return SharedMemory(name=name, create=True, size=size)
    except FileExistsError:
        logger.warning(
            f"Stale shared memory segment '{name}' found (likely from a previous "
            "crash). Unlinking and recreating it."
        )
        _stale = SharedMemory(name=name, create=False)
        _stale.close()
        _stale.unlink()
        return SharedMemory(name=name, create=True, size=size)


def close_shared_memory_dict(shares: dict[Any, SharedMemory], unlink: bool=False) -> None:
    """
    Close all shared memory segments and unlink the shared memory if specified.

    Parameters
    ----------
    shares : dict[Any, SharedMemory]
        A dictionary of shared memory segments to close.
    unlink : bool, optional
        Whether to unlink the shared memory segments after closing, by default False.
    """
    for _key, _shm in shares.items():
        try:
            _shm.close()
            if unlink:
                _shm.unlink()
        except FileNotFoundError as e:
            logger.error(f"Error closing shared memory segment '{_key}': {e}")
    shares.clear()