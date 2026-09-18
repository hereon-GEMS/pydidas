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

"""Unit tests for the lazy default frame registry."""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2026, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"


import pytest

from pydidas.gui.default_frames import (
    DEFAULT_FRAMES,
    FRAME_MODULE_PATHS,
    _load_frame_class,
    get_default_frames,
)
from pydidas.widgets.base_classes import BaseFrame


def test_default_frames__contains_only_known_frame_names():
    assert DEFAULT_FRAMES
    assert set(DEFAULT_FRAMES).issubset(FRAME_MODULE_PATHS)


def test_load_frame_class__returns_base_frame_subclass():
    frame_class = _load_frame_class("HomeFrame")
    assert issubclass(frame_class, BaseFrame)
    assert frame_class.__name__ == "HomeFrame"


def test_get_default_frames__raises_for_current_import_error():
    FRAME_MODULE_PATHS["NonExistentFrame"] = "pydidas.gui.frames.non_existent_frame"
    DEFAULT_FRAMES.append("NonExistentFrame")
    with pytest.raises(ImportError, match="pydidas.gui.frames.non_existent_frame"):
        get_default_frames()


def test_load_frame_class__raises_for_unknown_name():
    with pytest.raises(KeyError):
        _load_frame_class("DoesNotExistFrame")


if __name__ == "__main__":
    pytest.main([__file__])
