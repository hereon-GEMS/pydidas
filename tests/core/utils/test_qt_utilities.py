# This file is part of pydidas.
#
# Copyright 2024, Helmholtz-Zentrum Hereon
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
__copyright__ = "Copyright 2024, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"


import pytest
import weakref
from qtpy import QtWidgets

from pydidas.core.utils import update_child_qobject, weak_partial


def test_update_child_qobject(qapp):
    _width = 100
    _left = 42
    _obj = QtWidgets.QWidget()
    update_child_qobject(_obj, "geometry", left=_left, width=_width)
    _geo = _obj.geometry()
    assert _geo.width() == _width
    assert _geo.left() == _left


def test_weak_partial__forwards_args_and_kwargs():
    class _Owner:
        def method(self, a, b=0):
            return a, b

    _owner = _Owner()
    _func = weak_partial(_owner.method, 1, b=2)
    assert _func() == (1, 2)


def test_weak_partial__does_not_keep_owner_alive():
    class _Owner:
        def method(self):
            return None

    _owner = _Owner()
    _ref = weakref.ref(_owner)
    _fn = weak_partial(_owner.method)
    del _owner
    assert _ref() is None
    with pytest.raises(RuntimeError):
        _fn()


if __name__ == "__main__":
    pytest.main([__file__])
