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


import pytest

from pydidas.core.utils.converters import convert_to_slice


@pytest.mark.parametrize("object", [(7, 8), 7, [7], (7,), slice(7, 8), (slice(7, 8),)])
def test_convert_to_slice__single_index(object):
    assert convert_to_slice(object) == slice(7, 8)


@pytest.mark.parametrize(
    "object", [None, slice(None), (None, None), [None, None], (None,)]
)
def test_convert_to_slice__full_slicing(object):
    assert convert_to_slice(object) == slice(None, None)


@pytest.mark.parametrize(
    "invalid_object",
    ["string", 7.5, [7, "string"], [7.5], ("string",), (slice(None), slice(None))],
)
def test_convert_to_slice__invalid_types(invalid_object):
    with pytest.raises(ValueError):
        convert_to_slice(invalid_object)


@pytest.mark.parametrize("invalid_object", [[7, 8, 9], (7, 8, 9), [7, "string", 5]])
def test_convert_to_slice__invalid_length(invalid_object):
    with pytest.raises(ValueError):
        convert_to_slice(invalid_object)


@pytest.mark.parametrize("object", [(8, None), [8, None], slice(8, None)])
def test_convert_to_slice__w_None_index(object):
    assert convert_to_slice(object) == slice(8, None)


if __name__ == "__main__":
    pytest.main()
