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
__copyright__ = "Copyright 2026, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"


import pytest

from pydidas.core.utils.hdf5.hdf5_filter_keys import (
    FILTER_EXCEPTIONS,
    FILTER_KEY_DEFAULT_ACTIVE,
    FILTER_KEY_TITLE,
    FILTER_KEY_TOOLTIP,
    FILTER_KEYS,
)


def test_filter_keys():
    assert isinstance(FILTER_KEYS, list)
    for key in FILTER_KEYS:
        assert isinstance(key, str)


def test_filter_key_default_active():
    assert set(FILTER_KEY_DEFAULT_ACTIVE) == set(FILTER_KEYS)
    assert isinstance(FILTER_KEY_DEFAULT_ACTIVE, dict)
    for key, value in FILTER_KEY_DEFAULT_ACTIVE.items():
        assert isinstance(key, str)
        assert isinstance(value, bool)


def test_filter_key_title():
    assert set(FILTER_KEY_TITLE) == set(FILTER_KEYS)
    assert isinstance(FILTER_KEY_TITLE, dict)
    for key, value in FILTER_KEY_TITLE.items():
        assert isinstance(key, str)
        assert isinstance(value, str)


def test_filter_key_tooltip():
    assert set(FILTER_KEY_TOOLTIP) == set(FILTER_KEYS)
    assert isinstance(FILTER_KEY_TOOLTIP, dict)
    for key, value in FILTER_KEY_TOOLTIP.items():
        assert isinstance(key, str)
        assert isinstance(value, str)


def test_filter_exceptions():
    assert set(FILTER_EXCEPTIONS) == set(FILTER_KEYS)
    assert isinstance(FILTER_EXCEPTIONS, dict)
    for key, value in FILTER_EXCEPTIONS.items():
        assert isinstance(key, str)
        assert isinstance(value, list)
        for item in value:
            assert isinstance(item, str)


if __name__ == "__main__":
    pytest.main([__file__])
